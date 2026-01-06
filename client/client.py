import socket
import threading
import configparser
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
CONFIG_FILE = os.path.join(BASE_DIR, "config.ini")



def load_config(): # проверка config.ini
    if not os.path.exists(CONFIG_FILE):
        print(f"[ERROR] {CONFIG_FILE} не найден")
        sys.exit(1)

    config = configparser.ConfigParser()
    config.read(CONFIG_FILE, encoding="utf-8")
    try:
        host = config["server"]["host"]
        port = int(config["server"]["port"])
    except KeyError:
        print("[ERROR] неверный формат config.ini")
        sys.exit(1)
    return host, port

def receive_messages(client_socket): # функция принимает сообщения от сервера в отдельном потоке
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                print("\n[INFO] сервер отключился")
                break
            print(f"\n{data.decode()}\n> ", end="")
        except:
            break

def start_client(): # загружаем настройки сервера
    host, port = load_config()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        try:
            client.connect((host, port))
        except:
            print("[ERROR] не удалось подключиться к серверу")
            return

        # ввод ника
        while True:
            nick = input("Введите ваш ник: ").strip()
            if nick == "":
                print("Ник не может быть пустым.")
                continue
            client.send(nick.encode())

            # ждём ответ сервера
            data = client.recv(1024).decode()
            if data.startswith("[INFO] Добро пожаловать"):
                print(data)
                break
            elif "Ник занят" in data.lower():
                print(data)
            else:
                # игнорируем любые другие сообщения на этом этапе
                continue

        # поток для приёма сообщений
        threading.Thread(target=receive_messages, args=(client,), daemon=True).start()

        # основной цикл отправки сообщений
        while True:
            try:
                message = input("> ").strip()
                if message.lower() == "exit":
                    print("[EXIT] выход из чата...")
                    break
                client.send(message.encode())
                print(f"[YOU]: {message}")
            except KeyboardInterrupt:
                print("\n[EXIT] клиент закрыт")
                break



if __name__ == "__main__":
    start_client()
