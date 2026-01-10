import asyncio
from logger import logger

MIN_NICK_LEN = 3
MAX_NICK_LEN = 16

clients = {}
clients_lock = asyncio.Lock()


async def send_to_user(username, message): # отправка сообщения конкретному пользователю
    async with clients_lock:
        if username in clients:
            writer = clients[username]["writer"]
            try:
                writer.write(message.encode())
                await writer.drain()
            except Exception as e:
                logger.exception(f"Ошибка при отправке сообщения {username}: {e}")
                await disconnect_user(username)


async def broadcast(message, sender): # отправка сообщения всем кроме отправителя
    async with clients_lock:
        for user, data in list(clients.items()):
            if user != sender:
                writer = data["writer"]
                try:
                    writer.write(message.encode())
                    await writer.drain()
                except Exception as e:
                    logger.exception(f"Ошибка при рассылке сообщения {user}: {e}")
                    await disconnect_user(user)


async def disconnect_user(username): # отключение пользователя
    async with clients_lock:
        if username in clients:
            try:
                clients[username]["writer"].close()
                await clients[username]["writer"].wait_closed()
            except Exception:
                pass
            del clients[username]

    await broadcast(f"[SERVER] {username} покинул чат", "SERVER")
    logger.info(f"{username} отключился")


# команды
async def handle_help(username):
    await send_to_user(
        username,
        "/help — список команд\n"
        "/who — список подключенных\n"
        "/msg <user> <text> — личное сообщение\n"
        "/exit — выход"
    )

# /who
async def handle_who(username):
    async with clients_lock:
        users = ", ".join(clients.keys())
    await send_to_user(username, f"Online: {users}")

# /msg
async def handle_private_message(sender, target, text):
    async with clients_lock:
        if target not in clients:
            await send_to_user(sender, "Пользователь не найден")
            return

    await send_to_user(target, f"[ЛС] {sender}: {text}")
    await send_to_user(sender, f"[{target}]: {text}")
    logger.info(f"[ЛС] {sender} -> {target}: {text}")


# действия при выборе команд
async def handle_command(username, message):
    parts = message.strip().split(" ", 2)
    cmd = parts[0]

    if cmd == "/help":
        await handle_help(username)
    elif cmd == "/who":
        await handle_who(username)
    elif cmd == "/msg":
        if len(parts) < 3:
            await send_to_user(username, "Используйте: /msg <user> <text>")
        else:
            await handle_private_message(username, parts[1], parts[2])
    elif cmd == "/exit":
        await disconnect_user(username)
    else:
        await send_to_user(username, "Неизвестная команда. Введите /help")


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info('peername')
    nick = None

    try: # регистрация ника
        while True:
            try:
                data = await reader.read(1024)
            except (ConnectionResetError, ConnectionAbortedError, OSError):
                return
            if not data:
                return

            nick_candidate = data.decode().strip()
            async with clients_lock:

                # если ник не входит в наши условия
                if not (MIN_NICK_LEN <= len(nick_candidate) <= MAX_NICK_LEN):
                    writer.write(f"Ник должен быть от {MIN_NICK_LEN} до {MAX_NICK_LEN} символов".encode())
                    await writer.drain()

                # если такой ник занят
                elif nick_candidate in clients:
                    writer.write("Ник уже занят, введите другой".encode())
                    await writer.drain()

                else:
                    nick = nick_candidate
                    clients[nick] = {"reader": reader, "writer": writer}
                    writer.write(f"[INFO] Добро пожаловать, {nick}!".encode())
                    await writer.drain()
                    break

        logger.info(f"{nick} подключился с {addr}")
        await broadcast(f"[SERVER] {nick} вошёл в чат", "SERVER")

        # основной цикл
        while True:
            try:
                data = await reader.read(1024)
            except (ConnectionResetError, ConnectionAbortedError, OSError):
                break
            if not data:
                break

            message = data.decode().strip()
            if not message:
                continue

            logger.info(f"[{nick}] {message}")

            if message.startswith("/"):
                await handle_command(nick, message)
            else:
                await broadcast(f"[{nick}]: {message}", nick)



    except Exception as e:
        logger.exception(f"Необработанная ошибка для {nick}: {e}")
    finally:
        if nick:
            await disconnect_user(nick)
