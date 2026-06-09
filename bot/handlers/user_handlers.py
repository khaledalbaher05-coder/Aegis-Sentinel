from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

import random
import json

from bot.database import (
    register_user,
    get_all_services,
    create_order,
    get_user_balance
)

from bot.config import (
    CHANNEL_USERNAME
)

# =========================
# TEMP PAYMENTS
# =========================
pending_payments = {}

# =========================
# ACTIVE USERS
# =========================
active_users = {}

# =========================
# START COMMAND
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    register_user(
        user.id,
        user.username or user.first_name
    )

    balance = get_user_balance(user.id)

    services = get_all_services()

    keyboard = []

    for service in services:

        keyboard.append([
            InlineKeyboardButton(
                service[1],
                callback_data=f"service_{service[0]}"
            )
        ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    protection_status = "🔴 غير مفعلة"

    if user.id in active_users:
        protection_status = "🟢 مفعلة"

    text = f"""
🛡️ AEGIS SENTINEL

━━━━━━━━━━━━━━

💰 الرصيد:
${balance}

🛡️ الحماية:
{protection_status}

━━━━━━━━━━━━━━

اختر الخدمة:
"""

    await update.message.reply_text(
        text,
        reply_markup=reply_markup
    )

# =========================
# MAIN MENU
# =========================
async def show_main_menu(query):

    services = get_all_services()

    keyboard = []

    for service in services:

        keyboard.append([
            InlineKeyboardButton(
                service[1],
                callback_data=f"service_{service[0]}"
            )
        ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    balance = get_user_balance(
        query.from_user.id
    )

    protection_status = "🔴 غير مفعلة"

    if query.from_user.id in active_users:
        protection_status = "🟢 مفعلة"

    text = f"""
🛡️ AEGIS SENTINEL

━━━━━━━━━━━━━━

💰 الرصيد:
${balance}

🛡️ الحماية:
{protection_status}

━━━━━━━━━━━━━━

اختر الخدمة:
"""

    await query.message.reply_text(
        text,
        reply_markup=reply_markup
    )

# =========================
# SERVICE CLICK
# =========================
async def service_click(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    service_id = int(
        query.data.split("_")[1]
    )

    services = get_all_services()

    selected = None

    for service in services:

        if service[0] == service_id:
            selected = service
            break

    if not selected:

        await query.edit_message_text(
            "❌ الخدمة غير موجودة"
        )

        return

    service_name = selected[1]
    description = selected[2]
    base_price = selected[3]

    unique_cents = (
        query.from_user.id % 99
    ) / 100

    price = round(
        base_price + unique_cents,
        2
    )

    print("DEBUG 1")
    print("service =", service_name)
    print("price =", price)

    create_order(
        query.from_user.id,
        service_name,
        price,
    )

    pending_payments[
        query.from_user.id
    ] = {
        "service": service_name,
        "price": price
    }

    text = f"""
💳 طلب جديد

━━━━━━━━━━━━━━

🛡️ الخدمة:
{service_name}

📄 الوصف:
{description}

💰 السعر:
${price}

━━━━━━━━━━━━━━

اختر طريقة الدفع:
"""

    keyboard = [

        [
            InlineKeyboardButton(
                "💸 USDT",
                callback_data="pay_crypto"
            ),

            InlineKeyboardButton(
                "📲 شام كاش",
                callback_data="pay_shamcash"
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ رجوع",
                callback_data="back_main"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text,
        reply_markup=reply_markup
    )

# =========================
# PAY CRYPTO
# =========================
async def pay_crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id

    data = pending_payments[user_id]

    keyboard = [

        [
            InlineKeyboardButton(
                "✅ تم الدفع",
                callback_data="confirm_payment"
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ رجوع",
                callback_data="back_main"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    caption = f"""
💸 الدفع عبر USDT (TRC20)

━━━━━━━━━━━━━━

💰 المطلوب:
${data['price']}

━━━━━━━━━━━━━━

🏦 عنوان المحفظة:

TNphKc3qmusVEHW4bw17LnHWGMAVxa1WdB

━━━━━━━━━━━━━━

💳 بعد التحويل اضغط:
✅ تم الدفع

🔍 سيتم التحقق من الدفع تلقائياً
"""

    with open("assets/usdt_qr.png", "rb") as qr:

        await query.message.reply_photo(
            photo=qr,
            caption=caption,
            reply_markup=reply_markup
        )

# =========================
# CONFIRM PAYMENT
# =========================
async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id

    if user_id not in pending_payments:

        await query.message.reply_text(
            "❌ لا يوجد طلب"
        )

        return

    data = pending_payments[user_id]

    await query.message.reply_text(
        f"""
⏳ تم إرسال طلب التحقق

━━━━━━━━━━━━━━

🛡️ الخدمة:
{data['service']}

💰 السعر:
${data['price']}

━━━━━━━━━━━━━━

🔍 جاري التحقق من وصول الدفع...

⚠️ لن يتم التفعيل حتى يصل التحويل للمحفظة
"""
    )

# =========================
# PAY SHAMCASH
# =========================
async def pay_shamcash(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id

    data = pending_payments[user_id]

    keyboard = [
        [
            InlineKeyboardButton(
                "⬅️ رجوع",
                callback_data="back_main"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    caption = f"""
📲 الدفع عبر شام كاش

━━━━━━━━━━━━━━

💰 المطلوب:
${data['price']}

━━━━━━━━━━━━━━

📌 الرقم:
0933333333
"""

    with open("assets/shamcash_qr.png", "rb") as qr:

        await query.message.reply_photo(
            photo=qr,
            caption=caption,
            reply_markup=reply_markup
        )

# =========================
# BACK MAIN
# =========================
async def back_main(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    try:
        await query.message.delete()
    except:
        pass

    await show_main_menu(query)

# =========================
# STATUS COMMAND
# =========================
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if user_id not in active_users:

        await update.message.reply_text(
            "🔴 لا توجد حماية مفعلة"
        )

        return

    service = active_users[user_id]["service"]

    await update.message.reply_text(
        f"""
🟢 الحماية مفعلة

━━━━━━━━━━━━━━

🛡️ الخدمة:
{service}
"""
    )

# =========================
# TXID HANDLER
# =========================
async def txid_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return

# =========================
# AUTO OFFERS
# =========================
async def send_jobs_to_channel(context):

    try:

        offers = [

            {
                "title": "🛡️ CYBER FORTRESS PRO",
                "description": "✅ Channel Shield\n✅ Dark Web Monitoring\n✅ Instant Threat Alerts",
                "price": "199"
            },

            {
                "title": "🔥 TELEGRAM DEFENDER X",
                "description": "✅ Anti Spam System\n✅ Auto Ban Attackers\n✅ AI Security Protection",
                "price": "149"
            },

            {
                "title": "🚀 VIP Security Shield",
                "description": "✅ Full Telegram Protection\n✅ Advanced Moderation\n✅ Scam Detection",
                "price": "179"
            }

        ]

        offer = random.choice(offers)

        title = offer["title"]
        description = offer["description"]
        price = offer["price"]

        # DELETE OLD OFFER
        try:

            with open("last_offer.txt", "r") as f:
                old_msg_id = int(f.read())

            await context.bot.delete_message(
                chat_id=CHANNEL_USERNAME,
                message_id=old_msg_id
            )

        except:
            pass

        # SEND NEW OFFER
        msg = await context.bot.send_message(
            chat_id=CHANNEL_USERNAME,
            text=f"""
🔥 عرض تلقائي جديد

━━━━━━━━━━━━━━

{title}

{description}

💰 السعر:
{price}$

━━━━━━━━━━━━━━

🚀 اطلب الآن عبر البوت
"""
        )

        # SAVE MESSAGE ID
        with open("last_offer.txt", "w") as f:
            f.write(str(msg.message_id))

        # UPDATE WEBSITE
        offer_data = {
            "title": title,
            "description": description,
            "price": price
        }

        with open(
            "landing_page/offers.json",            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                offer_data,
                f,
                ensure_ascii=False
            )

        print("✅ OFFER SENT + WEBSITE UPDATED")

    except Exception as e:

        print("AUTO OFFER ERROR:", e)

# =========================
# SETUP HANDLERS
# =========================
def setup_handlers(app):

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        CommandHandler(
            "status",
            status_command
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            service_click,
            pattern="^service_"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            pay_crypto,
            pattern="^pay_crypto$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            confirm_payment,
            pattern="^confirm_payment$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            pay_shamcash,
            pattern="^pay_shamcash$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            back_main,
            pattern="^back_main$"
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            txid_handler
        )
    )

