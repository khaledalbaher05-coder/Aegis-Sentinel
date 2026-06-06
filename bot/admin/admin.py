from telegram import Update

from telegram.ext import (
    CommandHandler,
    ContextTypes
)

from bot.config import (
    ADMIN_ID,
    CHANNEL_USERNAME
)

from bot.database import (
    get_users_count,
    get_orders_count,
    get_total_payments
)

from auto_offers import add_offer

# =========================
# ADMIN PANEL
# =========================
async def admin_panel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    if user_id != ADMIN_ID:

        await update.message.reply_text(
            "❌ ليس لديك صلاحية."
        )

        return

    users = get_users_count()

    orders = get_orders_count()

    payments = get_total_payments()

    text = f"""
👑 AEGIS ADMIN PANEL

━━━━━━━━━━━━━━

👥 Users: {users}

🛒 Orders: {orders}

💰 Revenue: ${payments}

━━━━━━━━━━━━━━
"""

    await update.message.reply_text(
        text
    )

# =========================
# AUTO OFFER COMMAND
# =========================
async def offer_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    # حماية الأمر للإدمن فقط
    if user_id != ADMIN_ID:

        await update.message.reply_text(
            "❌ ليس لديك صلاحية."
        )

        return

    try:

        # أخذ النص كامل
        full_text = update.message.text.replace(
            "/offer",
            ""
        ).strip()

        parts = full_text.split("|")

        # تحقق من الصيغة
        if len(parts) < 3:

            await update.message.reply_text(
                "❌ الصيغة الصحيحة:\n/offer title | description | price"
            )

            return

        title = parts[0].strip()

        description = parts[1].strip()

        price = parts[2].strip()

        # إضافة العرض للموقع
        success = add_offer(
            title,
            description,
            price
        )

        # منع التكرار
        if not success:

            await update.message.reply_text(
                "⚠️ العرض موجود مسبقاً"
            )

            return

        # رسالة القناة
        text = f"""
🔥 عرض جديد متوفر الآن

━━━━━━━━━━━━━━

🛡️ الخدمة:
{title}

📄 التفاصيل:
{description}

💰 السعر:
${price}

━━━━━━━━━━━━━━

📩 للتواصل:
@mostaql_hunter
"""

        # نشر بالقناة
        await context.bot.send_message(
            chat_id=CHANNEL_USERNAME,
            text=text
        )

        # رسالة نجاح
        await update.message.reply_text(
            "✅ تم نشر العرض بالقناة والموقع"
        )

    except Exception as e:

        print(e)

        await update.message.reply_text(
            "❌ حدث خطأ أثناء إضافة العرض"
        )

# =========================
# SETUP
# =========================
def setup_admin_handlers(app):

    app.add_handler(
        CommandHandler(
            "admin",
            admin_panel
        )
    )

    app.add_handler(
        CommandHandler(
            "offer",
            offer_command
        )
    )

