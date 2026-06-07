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

from bot.database import (
    register_user,
    get_all_services,
    create_order,
    save_payment,
    get_user_balance,
    deduct_balance,
    activate_subscription
)

from bot.config import (
    WALLET_ADDRESS,
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

    create_order(
        query.from_user.id,
        service_name
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
                "💰 شراء من الرصيد",
                callback_data="buy_balance"
            )
        ],

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
# BUY FROM BALANCE
# =========================
async def buy_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id

    if user_id not in pending_payments:

        await query.edit_message_text(
            "❌ لا يوجد طلب"
        )

        return

    data = pending_payments[user_id]

    balance = get_user_balance(user_id)

    price = data["price"]

    if balance < price:

        await query.edit_message_text(
            f"""
❌ الرصيد غير كافي

💰 رصيدك:
${balance}

💳 السعر:
${price}
"""
        )

        return

    deduct_balance(
        user_id,
        price
    )

    activate_subscription(
        user_id,
        data["service"]
    )

    active_users[user_id] = {
        "service": data["service"]
    }

    await context.bot.send_message(
        chat_id=CHANNEL_USERNAME,
        text=f"""
🎉 عملية شراء جديدة

━━━━━━━━━━━━━━

🛡️ الخدمة:
{data['service']}

💰 السعر:
${price}

👤 المستخدم:
{user_id}
"""
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "⬅️ الرجوع للرئيسية",
                callback_data="back_main"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"""
✅ تم التفعيل بنجاح

━━━━━━━━━━━━━━

🛡️ الخدمة:
{data['service']}

💰 السعر:
${price}

━━━━━━━━━━━━━━

🟢 الحماية مفعلة
""",
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
                "⬅️ رجوع",
                callback_data="back_main"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    text = f"""
💸 الدفع عبر USDT

━━━━━━━━━━━━━━

💰 المطلوب:
${data['price']}

━━━━━━━━━━━━━━

🏦 المحفظة:

{WALLET_ADDRESS}
"""

    await query.edit_message_text(
        text,
        reply_markup=reply_markup
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

━━━━━━━━━━━━━━

📸 قم بمسح QR وإرسال صورة التحويل للإدارة
"""

    try:

        with open("assets/shamcash_qr.png", "rb") as qr:

            await query.message.reply_photo(
                photo=qr,
                caption=caption,
                reply_markup=reply_markup
            )

        await query.message.delete()

    except Exception as e:

        await query.message.reply_text(
            f"❌ خطأ بتحميل QR\n\n{e}"
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

        title = "🛡️ CYBER FORTRESS PRO"

        description = """
✅ Channel Shield
✅ Dark Web Monitoring
✅ Instant Threat Alerts
"""

        price = "199"

        # =========================
        # SEND TO TELEGRAM
        # =========================
        await context.bot.send_message(
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

        # =========================
        # SAVE TO LANDING PAGE
        # =========================
        offer_data = f"""{title}
{description}
{price}
"""

        with open(
            "landing_page/offers.txt",
            "w",
            encoding="utf-8"
        ) as f:

            f.write(offer_data)

        print("✅ OFFER SENT + SAVED")

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
            buy_balance,
            pattern="^buy_balance$"
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

