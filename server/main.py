import asyncio
from config import HOST, PORT
from handlers import handle_client
from logger import logger

async def main():
    server = await asyncio.start_server(handle_client, HOST, PORT)
    addr = server.sockets[0].getsockname()
    logger.info(f"Сервер запущен на {addr[0]}:{addr[1]}")

    async with server:
        await server.serve_forever()



if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Сервер выключен")
    except Exception as e:
        logger.exception(f"Неожиданная ошибка: {e}")
