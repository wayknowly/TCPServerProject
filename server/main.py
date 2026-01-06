import socket
import threading
from config import HOST, PORT
from handlers import handle_client
import logger

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[LISTENING] Сервер запущен на {HOST}:{PORT}")

    try:
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count()-1}")
    except KeyboardInterrupt:
        print("\n[STOP] Сервер выключен")
    finally:
        server.close()




if __name__ == "__main__":
    start_server()