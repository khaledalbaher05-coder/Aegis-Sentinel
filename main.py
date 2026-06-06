import logging

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
# MAIN
# =========================
def main():

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

    # =========================
    # ACTIVATE
    # =========================
    app.add_handler(
        CommandHandler(
            "activate",
            activate_group
        ),
        group=0
    )

    # =========================
    # GROUP SECURITY
    # =========================
    app.add_handler(
        MessageHandler(
            filters.ChatType.GROUPS
            & filters.TEXT
            & ~filters.COMMAND,
            anti_spam
        ),
        group=1
    )

    # =========================
    # ERRORS
    # =========================
    app.add_error_handler(
        error_handler
    )

    # =========================
    # JOBS
    # =========================
    app.job_queue.run_repeating(
        send_jobs_to_channel,
        interval=300,
        first=10
    )

    print("✅ BOT ONLINE")

    # START
    app.run_polling(
        drop_pending_updates=True
    )


# =========================
# START
# =========================
if __name__ == "__main__":

    main()

