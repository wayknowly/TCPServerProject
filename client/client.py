import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox
import configparser
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
CONFIG_FILE = os.path.join(BASE_DIR, "config.ini")
BUFFER_SIZE = 1024
MAX_MESSAGE_LEN = 512 # максимальная длина сообщения


# загрузка конфига
def load_config():
    if not os.path.exists(CONFIG_FILE):
        messagebox.showerror("[ERROR]", f"Файл конфигурации не найден:\n{CONFIG_FILE}")
        sys.exit(1)
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE, encoding="utf-8")
    try:
        host = config["server"]["host"]
        port = int(config["server"]["port"])
    except (KeyError, ValueError):
        messagebox.showerror("[ERROR]", "Неверный формат config.ini")
        sys.exit(1)
    return host, port


class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("TCP Chat Client")
        self.master.geometry("850x650")
        self.host, self.port = load_config()
        self.nick = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if not self.connect():
            return
        if not self.register_nick():
            return

        self.create_gui()
        threading.Thread(target=self.receive_messages, daemon=True).start()

    # подключение
    def connect(self):
        try:
            self.sock.connect((self.host, self.port))
            return True
        
        except Exception:
            messagebox.showerror("[ERROR]", f"Не удалось подключиться к {self.host}:{self.port}")
            self.master.destroy()
            return False

    # регистрация
    def register_nick(self):
        while True:
            nick = simpledialog.askstring(" ", "Введите ваш никнейм:", parent=self.master)
            if nick is None:
                self.master.destroy()
                return False
            
            nick = nick.strip()
            if not nick:
                messagebox.showwarning("[INFO]", "Никнейм не может быть пустым")
                continue
            if len(nick) > 15:
                messagebox.showwarning("[INFO]", "Ник слишком длинный (максимум 15 символов)")
                continue
            try:
                self.sock.send(nick.encode("utf-8"))
                response = self.sock.recv(BUFFER_SIZE).decode("utf-8")
            except Exception:
                messagebox.showerror("[ERROR]", "Ошибка соединения с сервером")
                self.master.destroy()
                return False
            
            if response.startswith("[INFO]"):
                messagebox.showinfo("Информация", response)
                self.nick = nick
                return True
            else:
                messagebox.showwarning("Ошибка", response)

    def create_gui(self):
        # окно чата
        self.text_area = scrolledtext.ScrolledText(
            self.master, state="disabled", wrap="word"
        )
        self.text_area.pack(padx=10, pady=10, fill="both", expand=True)
        
        # пкм по чату копировать
        self.text_area.bind("<Button-3>", self.show_text_menu)

        # поле ввода сообщений
        self.entry_message = tk.Entry(self.master)
        self.entry_message.pack(padx=10, pady=5, fill="x")
        self.entry_message.bind("<Return>", lambda e: self.send_message())
        
        # пкм вставить
        self.entry_message.bind("<Button-3>", self.show_entry_menu)

        # кнопки
        buttons = tk.Frame(self.master)
        buttons.pack(pady=5)
        tk.Button(buttons, text="Отправить", command=self.send_message).pack(side="left", padx=5)
        tk.Button(buttons, text="Выйти", command=lambda: self.send_message("/exit")).pack(side="left", padx=5)

    # окно копирования
    def show_text_menu(self, event):
        menu = tk.Menu(self.master, tearoff=0)
        menu.add_command(label="Копировать", command=self.copy_text)
        menu.tk_popup(event.x_root, event.y_root)

    # окно вставки
    def show_entry_menu(self, event):
        menu = tk.Menu(self.master, tearoff=0)
        menu.add_command(label="Вставить", command=lambda: self.entry_message.insert(tk.INSERT, self.master.clipboard_get()))
        menu.tk_popup(event.x_root, event.y_root)

    def copy_text(self):
        try:
            selected = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.master.clipboard_clear()
            self.master.clipboard_append(selected)
        except tk.TclError:
            pass

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

    def send_message(self, message=None):
        if message is None:
            message = self.entry_message.get().strip()
        if not message:
            return
        if len(message) > MAX_MESSAGE_LEN:
            messagebox.showwarning("[INFO]", f"Сообщение слишком длинное (макс {MAX_MESSAGE_LEN} символов)")
            return
        try:
            self.sock.send(message.encode("utf-8"))
            if message != "/exit":
                self.append_message(f"[YOU]: {message}")
            self.entry_message.delete(0, tk.END)
            if message == "/exit":
                self.close()
        except Exception:
            self.append_message("[ERROR] Не удалось отправить сообщение")

    def append_message(self, message):
        self.text_area.config(state="normal")
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.config(state="disabled")
        self.text_area.yview(tk.END)

    def close(self):
        try:
            self.sock.close()
        except Exception:
            pass
        self.master.destroy()



if __name__ == "__main__":
    root = tk.Tk()
    ChatClient(root)
    root.mainloop()
