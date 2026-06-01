import logging

from telegram.ext import ApplicationBuilder

from bot.config import TOKEN
from bot.database import init_db
from bot.handlers import setup_handlers, send_jobs_to_channel

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)


def main():
    logger.info("Initializing database...")
    init_db()

    logger.info("Starting bot...")

    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .build()
    )

    setup_handlers(app)

    app.job_queue.run_repeating(
        send_jobs_to_channel,
        interval=300,
        first=10
    )

    logger.info("🚀 Aegis Sentinel Bot is running...")

    app.run_polling(
        allowed_updates=None,
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
