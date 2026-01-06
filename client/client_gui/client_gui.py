import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog
import configparser
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
CONFIG_FILE = os.path.join(BASE_DIR, "config.ini")



def load_config():
    if not os.path.exists(CONFIG_FILE):
        tk.messagebox.showerror("Error", f"{CONFIG_FILE} not found")
        sys.exit(1)
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE, encoding="utf-8")
    host = config["server"]["host"]
    port = int(config["server"]["port"])
    return host, port

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("TCP Chat Client")
        self.host, self.port = load_config()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.host, self.port))
        except:
            tk.messagebox.showerror("Error", f"Cannot connect to server {self.host}:{self.port}")
            master.destroy()
            return

        # никнейм
        self.nick = simpledialog.askstring("Nickname", "Enter your nickname:", parent=master)
        if not self.nick:
            tk.messagebox.showerror("Error", "Nickname cannot be empty")
            master.destroy()
            return
        self.sock.send(self.nick.encode())


        # ждём подтверждение сервера
        data = self.sock.recv(1024).decode()
        if "Добро пожаловать" not in data:
            tk.messagebox.showinfo("Info", data)
            master.destroy()
            return


        # GUI элементы
        self.text_area = scrolledtext.ScrolledText(master, state='disabled', wrap='word')
        self.text_area.pack(padx=10, pady=10, fill='both', expand=True)

        self.entry_message = tk.Entry(master)
        self.entry_message.pack(padx=10, pady=5, fill='x')
        self.entry_message.bind("<Return>", self.send_message)

        self.button_send = tk.Button(master, text="Send", command=self.send_message)
        self.button_send.pack(padx=10, pady=5)

        self.button_exit = tk.Button(master, text="Exit", command=self.close)
        self.button_exit.pack(padx=10, pady=5)



        # поток для приёма сообщений
        threading.Thread(target=self.receive_messages, daemon=True).start()



    def receive_messages(self):
        while True:
            try:
                data = self.sock.recv(1024)
                if not data:
                    self.append_message("[INFO] Server disconnected")
                    break
                self.append_message(data.decode())
            except:
                break

    def send_message(self, event=None):
        msg = self.entry_message.get().strip()
        if msg == "":
            return
        if msg.lower() == "exit":
            self.close()
            return
        self.sock.send(msg.encode())
        self.append_message(f"[YOU]: {msg}")
        self.entry_message.delete(0, tk.END)

    def append_message(self, message):
        self.text_area.config(state='normal')
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.config(state='disabled')
        self.text_area.yview(tk.END)

    def close(self):
        try:
            self.sock.close()
        except:
            pass
        self.master.destroy()



if __name__ == "__main__":
    root = tk.Tk()
    client = ChatClient(root)
    root.mainloop()
