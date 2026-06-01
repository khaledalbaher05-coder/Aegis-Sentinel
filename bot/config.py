import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

TOKEN = os.getenv("BOT_TOKEN")
TRON_API_KEY = os.getenv("TRON_API_KEY")
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

print("TOKEN =", TOKEN)
