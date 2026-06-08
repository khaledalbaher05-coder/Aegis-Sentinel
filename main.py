import logging
import asyncio
import threading

from flask import Flask, send_from_directory

from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    filters
)

from bot.config import TOKEN
from bot.database import init_db

from bot.handlers.user_handlers import (
    setup_handlers,
    send_jobs_to_channel
)

from bot.admin.admin import (
    setup_admin_handlers
)

from bot.security.security import (
    anti_spam,
    activate_group
)

# =========================
# FLASK APP
# =========================
web_app = Flask(
    __name__,
    static_folder="landing_page"
)

@web_app.route("/")
def landing_page():
    return send_from_directory(
        "landing_page",
        "index.html"
    )

@web_app.route("/offers.txt")
def offers():
    return send_from_directory(
        ".",
        "offers.txt"
    )

# =========================
# LOGGING
# =========================
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# =========================
# ERROR HANDLER
# =========================
async def error_handler(update, context):

    print("ERROR:", context.error)

# =========================
# BOT MAIN
# =========================
async def bot_main():

    print("🚀 STARTING BOT")

    # DATABASE
    init_db()

    # APP
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .build()
    )

    # USER HANDLERS
    setup_handlers(app)

    # ADMIN
    setup_admin_handlers(app)

    # ACTIVATE
    app.add_handler(
        CommandHandler(
            "activate",
            activate_group
        ),
        group=0
    )

    # GROUP SECURITY
    app.add_handler(
        MessageHandler(
            filters.ChatType.GROUPS
            & filters.TEXT
            & ~filters.COMMAND,
            anti_spam
        ),
        group=1
    )

    # ERRORS
    app.add_error_handler(
        error_handler
    )

    # AUTO OFFERS
    if app.job_queue:

        app.job_queue.run_repeating(
            send_jobs_to_channel,
            interval=300,
            first=10
        )

    print("✅ BOT ONLINE")

    # START BOT
    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    # KEEP RUNNING
    while True:
        await asyncio.sleep(3600)

# =========================
# START FLASK
# =========================
def run_web():

    web_app.run(
        host="0.0.0.0",
        port=10000
    )

# =========================
# START ALL
# =========================
if __name__ == "__main__":

    # START WEBSITE
    threading.Thread(
        target=run_web
    ).start()

    # START BOT
    asyncio.run(bot_main())

