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

# FLASK WEBSITE

# =========================

app_flask = Flask(
**name**,
static_folder="landing_page"
)

@app_flask.route("/")
def home():
return send_from_directory(
"landing_page",
"index.html"
)

@app_flask.route("/offers.json")
def offers():
return send_from_directory(
"landing_page",
"offers.json"
)

def run_web():
app_flask.run(
host="0.0.0.0",
port=10000
)

# =========================

# LOGGING

# =========================

logging.basicConfig(
format="%(asctime)s - %(levelname)s - %(message)s",
level=logging.INFO
)

logger = logging.getLogger(**name**)

# =========================

# ERROR HANDLER

# =========================

async def error_handler(update, context):

```
print("ERROR:", context.error)
```

# =========================

# MAIN

# =========================

async def main():

```
print("🚀 STARTING BOT")

init_db()

app = (
    ApplicationBuilder()
    .token(TOKEN)
    .build()
)

setup_handlers(app)

setup_admin_handlers(app)

app.add_handler(
    CommandHandler(
        "activate",
        activate_group
    ),
    group=0
)

app.add_handler(
    MessageHandler(
        filters.ChatType.GROUPS
        & filters.TEXT
        & ~filters.COMMAND,
        anti_spam
    ),
    group=1
)

app.add_error_handler(
    error_handler
)

if app.job_queue:

    app.job_queue.run_repeating(
        send_jobs_to_channel,
        interval=30,
        first=5
    )

print("✅ BOT ONLINE")

await app.initialize()
await app.start()
await app.updater.start_polling()

while True:
    await asyncio.sleep(3600)
```

# =========================

# START

# =========================

if **name** == "**main**":

```
threading.Thread(
    target=run_web
).start()

asyncio.run(main())

