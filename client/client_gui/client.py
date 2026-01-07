import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox
import configparser
import os
import sys

# настройки
BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
CONFIG_FILE = os.path.join(BASE_DIR, "config.ini")
BUFFER_SIZE = 1024




def load_config(): # загрузка host и port
    if not os.path.exists(CONFIG_FILE):
        messagebox.showerror(
            "[ERROR]",
            f"Файл конфигурации не найден:\n{CONFIG_FILE}"
        )
        sys.exit(1)

    config = configparser.ConfigParser()
    config.read(CONFIG_FILE, encoding="utf-8")

    try:
        host = config["server"]["host"]
        port = int(config["server"]["port"])
    except (KeyError, ValueError):
        messagebox.showerror(
            "[ERROR]",
            "Неверный формат config.ini"
        )
        sys.exit(1)

    return host, port


class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("TCP Chat Client")
        self.master.geometry("850x650")

        self.host, self.port = load_config()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if not self.connect():
            return

        if not self.register_nick():
            return

        self.create_gui()
        self.start_receiver()

    def connect(self): # подключение к серверу
        try:
            self.sock.connect((self.host, self.port))
            return True
        except Exception:
            messagebox.showerror(
                "[ERROR]",
                f"Не удалось подключиться к {self.host}:{self.port}"
            )
            self.master.destroy()
            return False

    def register_nick(self): # регистрация никнейма
        while True:
            nick = simpledialog.askstring(
                "Никнейм",
                "Введите ваш никнейм (3–16 символов):",
                parent=self.master
            )

            if nick is None:
                self.master.destroy()
                return False

            nick = nick.strip()

            if not nick:
                messagebox.showwarning(
                    "Ошибка",
                    "Ник не может быть пустым"
                )
                continue

            if len(nick) < 3 or len(nick) > 16:
                messagebox.showwarning(
                    "Ошибка",
                    "Длина ника должна быть от 3 до 16 символов"
                )
                continue

            self.sock.send(nick.encode("utf-8"))
            response = self.sock.recv(BUFFER_SIZE).decode("utf-8")

            if response.startswith("[INFO]"):
                messagebox.showinfo("TCP Chat Client", response)
                self.nick = nick
                return True
            else:
                messagebox.showwarning("error", response)


    
    # элементы интерфейса
    def create_gui(self):
        self.text_area = scrolledtext.ScrolledText(
            self.master,
            state="disabled",
            wrap="word"
        )
        self.text_area.pack(padx=10, pady=10, fill="both", expand=True)

        self.entry_message = tk.Entry(self.master)
        self.entry_message.pack(padx=10, pady=5, fill="x")
        self.entry_message.bind("<Return>", self.send_message)

        buttons = tk.Frame(self.master)
        buttons.pack(pady=5)

        tk.Button(
            buttons,
            text="Отправить",
            command=self.send_message
        ).pack(side="left", padx=5)

        tk.Button(
            buttons,
            text="Выйти",
            command=self.close
        ).pack(side="left", padx=5)

    # поток приёма сообщений
    def start_receiver(self):
        threading.Thread(
            target=self.receive_messages,
            daemon=True
        ).start()

    def receive_messages(self):
        while True:
            try:
                data = self.sock.recv(BUFFER_SIZE)
                if not data:
                    self.append_message("[INFO] Сервер отключился")
                    break
                self.append_message(data.decode("utf-8"))
            except Exception:
                break

    def send_message(self, event=None):
        message = self.entry_message.get().strip()
        if not message:
            return

        if message.lower() == "exit":
            self.close()
            return

        try:
            self.sock.send(message.encode("utf-8"))
            self.append_message(f"[YOU]: {message}")
            self.entry_message.delete(0, tk.END)
        except Exception:
            self.append_message("[ERROR] Не удалось отправить сообщение")


    
    def append_message(self, message):
        self.text_area.config(state="normal")
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.config(state="disabled")
        self.text_area.yview(tk.END)


    
    def close(self): # корректное закрытие
        try:
            self.sock.close()
        except Exception:
            pass
        self.master.destroy()




if __name__ == "__main__":
    root = tk.Tk()
    ChatClient(root)
    root.mainloop()
