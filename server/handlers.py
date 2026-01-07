import threading
import time
import logging

MIN_NICK_LEN = 3
MAX_NICK_LEN = 16

clients = {}
clients_lock = threading.Lock()




# отправка сообщений
def send_to_user(username, message):
    with clients_lock:
        if username in clients:
            try:
                clients[username]["socket"].sendall(message.encode())
            except Exception:
                disconnect_user(username)


def broadcast(message, sender):
    with clients_lock:
        for user, data in list(clients.items()):
            if user != sender:
                try:
                    data["socket"].sendall(message.encode())
                except Exception:
                    disconnect_user(user)


def disconnect_user(username):
    with clients_lock:
        if username in clients:
            try:
                clients[username]["socket"].close()
            except Exception:
                pass
            del clients[username]

    broadcast(f"[SERVER] {username} покинул чат", "SERVER")
    logging.info(f"{username} отключился")


# команды
def handle_help(username):
    send_to_user(
        username,
        "/help — список команд\n"
        "/who — список подключенных\n"
        "/ping — проверить задержку\n"
        "/msg <user> <text> — личное сообщение\n"
        "/exit или exit — выход"
    )


def handle_who(username):
    with clients_lock:
        users = ", ".join(clients.keys())
    send_to_user(username, f"Online: {users}")


def handle_private_message(sender, target, text):
    with clients_lock:
        if target not in clients:
            send_to_user(sender, "Пользователь не найден")
            return

    send_to_user(target, f"[ЛС] {sender}: {text}")
    send_to_user(sender, f"[{target}]: {text}")


def handle_ping(username):
    with clients_lock:
        clients[username]["last_ping"] = time.time()
    send_to_user(username, "__ping__")


def handle_pong(username):
    with clients_lock:
        start = clients[username]["last_ping"]

    if start:
        rtt = (time.time() - start) * 1000
        send_to_user(username, f"Ping: {rtt:.2f} ms")


def handle_command(username, message):
    parts = message.split(" ", 2)
    cmd = parts[0]

    if cmd == "/help":
        handle_help(username)

    elif cmd == "/who":
        handle_who(username)

    elif cmd == "/ping":
        handle_ping(username)

    elif cmd == "/msg":
        if len(parts) < 3:
            send_to_user(username, "Используйте: /msg <user> <text>")
        else:
            handle_private_message(username, parts[1], parts[2])

    elif cmd == "/exit":
        disconnect_user(username)

    else:
        send_to_user(username, "Неизвестная команда. Введите /help")



def handle_client(conn, addr):
    nick = None
    try:
        # регистрация ника
        while True:
            try:
                data = conn.recv(1024)
            except (ConnectionResetError, ConnectionAbortedError):
                return

            if not data:
                return

            nick = data.decode().strip()

            with clients_lock:
                if not (MIN_NICK_LEN <= len(nick) <= MAX_NICK_LEN):
                    conn.send(
                        f"Ник должен быть от {MIN_NICK_LEN} до {MAX_NICK_LEN} символов".encode()
                    )
                elif nick in clients:
                    conn.send("Ник уже занят, введите другой".encode())
                else:
                    clients[nick] = {
                        "socket": conn,
                        "address": addr,
                        "last_ping": None
                    }
                    conn.send(f"[INFO] Добро пожаловать, {nick}!".encode())
                    break

        logging.info(f"{nick} подключился")
        broadcast(f"[SERVER] {nick} вошёл в чат", "SERVER")

        # основной цикл
        while True:
            try:
                data = conn.recv(1024)
            except (ConnectionResetError, ConnectionAbortedError):
                break

            if not data:
                break

            message = data.decode().strip()
            if not message:
                continue

            logging.info(f"[{nick}] {message}")

            # ответ на ping
            if message == "__pong__":
                handle_pong(nick)
                continue

            # команды
            if message.startswith("/"):
                handle_command(nick, message)
            else:
                broadcast(f"{nick}: {message}", nick)

    finally:
        if nick:
            disconnect_user(nick)
        conn.close()
