import threading
import logging

clients = {}  # nick: socket
clients_lock = threading.Lock()



def broadcast(message, sender_nick):
    with clients_lock:
        for nick, sock in clients.items():
            if nick != sender_nick:
                try:
                    sock.send(f"[{sender_nick}]: {message}".encode())
                except:
                    pass

def handle_client(conn, addr):
    nick = ""
    try:
        # ждем первый ввод ника от клиента
        while True:
            nick = conn.recv(1024).decode().strip()
            with clients_lock:
                if nick != "" and nick not in clients:
                    clients[nick] = conn
                    conn.send(f"[INFO] Добро пожаловать, {nick}!".encode())
                    break
                else:
                    conn.send("Ник занят или пустой, введите другой:".encode())


        logging.info(f"{nick} подключился")


        while True:
            data = conn.recv(1024)
            if not data:
                break
            message = data.decode()
            logging.info(f"[{nick}] {message}")
            broadcast(message, nick)


    except ConnectionResetError:
        logging.warning(f"{nick} отключился неожиданно")
    finally:
        with clients_lock:
            if nick in clients:
                del clients[nick]
        conn.close()

        logging.info(f"{nick} отключился")
        broadcast(f"{nick} покинул чат", "SERVER")
