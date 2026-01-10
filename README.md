# EN

# TCP Server–Client Chat

A project for a TCP server and client in Python.
The project demonstrates the basics of network programming, multithreading, socket management, logging, and the interaction of multiple clients through a server.


## Features

* `asyncio` for asynchronous connection handling
* Connect multiple clients at the same time
* Sending messages to all clients (broadcast)
* Registering nicknames
* Correctly disconnecting clients
* Notifying clients when the server is shut down
* Centralized logging (to file and console)
* UTF-8 support for logs

## Project Launch

* It is important that the launch `client.py` and `config.ini` were in the same folder.
* In `config.ini`, the host must be equal to the IP address of the machine where the server is running, otherwise the client will not be able to connect.

### Linux/macOS

Launch server:

```
bash
./scripts/run_server.sh
```

Launch client:

```
bash
./scripts/run_client.sh
```

### Windows

Run via:

```
server.bat
```

Or from the terminal:

```
python server/main.py
```

After startup, the server begins listening for incoming connections.

#### Starting the Client

Open **one or more terminal windows** and run:

```
python client.py
```
* Easy launch via `.exe` for clients can be created using PyInstaller

## Usage

* After connecting to the server, enter a username
* Type a message and press Enter — it will be sent to other clients

Your messages:

```
[YOU]: message
```

Messages from other clients:

```
["Nickname"]: message
```

There is also a list of commands:

```
/help
```

Exit command:

```
/exit
```

If the server shuts down, the client receives:

```
[INFO] The server has shut down
```

and exits gracefully.

## Logging

The server logs:

* to the console
* to the file `logs/server_log.txt`

Log format:

```
YYYY-MM-DD HH:MM:SS [LEVEL] message
```

Logging functionality is implemented in a separate module: `logger.py`.

---

# RU

# TCP Сервер–Клиент Чат

Небольшой проект TCP-сервера и клиента на Python.
Проект демонстрирует основы сетевого программирования, многопоточность, работу с сокетами, логирование и взаимодействие нескольких клиентов через сервер.


## Возможности

* `asyncio` для асинхронной обработки подключений
* Подключение нескольких клиентов одновременно
* Рассылка сообщений всем клиентам (broadcast)
* Регистрация никнеймов (псевдонимов)
* Корректное отключение клиентов
* Уведомление клиентов при выключении сервера
* Централизованное логирование (в файл и консоль)
* Поддержка UTF-8 для логов

## Запуск проекта

* Важно, чтобы запуск `client.py` и `config.ini` были в одной папке.
* В `config.ini` host должен быть равен IP-адресу машины, где запущен сервер, иначе клиент не сможет подключиться.

### Linux/macOS

Запуск сервера:

```
bash
./scripts/run_server.sh
```

Запуск клиента:

```
bash
./scripts/run_client.sh
```

### Windows

Запуск через:

```
server.bat
```

Или через терминал:

```
python server/main.py
```

После запуска сервер начинает принимать подключения.

#### Запуск клиента

Откройте **одно или несколько окон** терминала и запустите:

```
python client.py
```
* Простой запуск через `.exe` для клиентов может быть создан с помощью PyInstaller

## Использование

* После подключения к серверу необходимо ввести имя пользователя
* Введите сообщение и нажмите Enter — оно будет отправлено другим клиентам

Ваши сообщения:

```
[YOU]: сообщение
```

Сообщения других клиентов:

```
["Ник"]: сообщение
```

Также существует список команд:

```
/help
```

Команда выхода:

```
/exit
```

Если сервер выключается, клиент получает:

```
[INFO] Сервер отключился
```

и корректно завершает работу.

## Логирование

Сервер ведёт логирование:

* в консоль
* в файл `logs/server_log.txt`

Формат логов:

```
YYYY-MM-DD HH:MM:SS [LEVEL] сообщение
```

Код логирования вынесен в отдельный модуль `logger.py`.

---

# config.ini

```
[server]
host = 0.0.0.0 # IP
port = 5000
```
