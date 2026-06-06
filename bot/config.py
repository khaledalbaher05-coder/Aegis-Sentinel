import os

from dotenv import load_dotenv
from pathlib import Path


# =========================
# BASE DIR
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent


# =========================
# LOAD ENV
# =========================
load_dotenv(BASE_DIR / ".env")


# =========================
# BOT CONFIG
# =========================
TOKEN = os.getenv(
    "BOT_TOKEN"
)

ADMIN_ID = int(
    os.getenv("ADMIN_ID")
)


# =========================
# PAYMENT
# =========================
WALLET_ADDRESS = os.getenv(
    "WALLET_ADDRESS"
)

TRON_API_KEY = os.getenv(
    "TRON_API_KEY"
)


# =========================
# CHANNEL
# =========================
CHANNEL_USERNAME = "@mostaql_hunter"


# =========================
# GITHUB CONFIG
# =========================
GITHUB_TOKEN = os.getenv(
    "GITHUB_TOKEN"
)

GITHUB_REPO = "khaledalbaher05-coder/phantom-offers"

GITHUB_OFFERS_PATH = "offers.json"


# =========================
# DEBUG
# =========================
print("BOT STARTED")

