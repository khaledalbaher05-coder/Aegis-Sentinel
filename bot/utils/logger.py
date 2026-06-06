import logging
import os

# إنشاء مجلد logs إذا غير موجود
if not os.path.exists("logs"):
    os.makedirs("logs")

# إعداد اللوجر
logger = logging.getLogger("AegisSentinel")

logger.setLevel(logging.INFO)

# تنسيق الرسائل
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)

# ملف اللوج
file_handler = logging.FileHandler("logs/bot.log")

file_handler.setFormatter(formatter)

# طباعة بالتيرمنال
stream_handler = logging.StreamHandler()

stream_handler.setFormatter(formatter)

# إضافة الهاندلرز
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
