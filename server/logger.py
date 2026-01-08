import logging
import logging.handlers
import os

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# ротация файлов максимум 5 файлов по 5 МБ
log_file = os.path.join(LOG_DIR, "server_log.txt")
file_handler = logging.handlers.RotatingFileHandler(
    log_file, maxBytes=5*1024*1024, backupCount=5, encoding="utf-8"
)

# форматирование логов
formatter = logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] %(message)s")
file_handler.setFormatter(formatter)

# стрим-лог консоль
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# основной логгер
logger = logging.getLogger("TCPServer")
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)
