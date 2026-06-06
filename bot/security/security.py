from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatMemberStatus

import time


# =========================
# ACTIVE GROUPS
# =========================
active_groups = {}

# =========================
# SPAM CACHE
# =========================
spam_cache = {}

# =========================
# WARN CACHE
# =========================
warn_cache = {}


# =========================
# ACTIVATE GROUP
# =========================
async def activate_group(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    chat = update.effective_chat
    user = update.effective_user

    member = await context.bot.get_chat_member(
        chat.id,
        user.id
    )

    # ADMIN CHECK
    if member.status not in [
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.OWNER
    ]:

        await update.message.reply_text(
            "❌ يجب أن تكون أدمن"
        )

        return

    # SAVE ACTIVE
    active_groups[chat.id] = True

    await update.message.reply_text(
        """
🛡️ تم تفعيل الحماية بنجاح

━━━━━━━━━━━━━━

✅ Anti Spam فعال
✅ Link Block فعال
✅ Auto Mute فعال
✅ مراقبة الرسائل فعالة

🤖 المجموعة أصبحت محمية
"""
    )


# =========================
# MUTE USER
# =========================
async def mute_user(
    update,
    context,
    user_id,
    minutes=10
):

    until_date = int(
        time.time() + (minutes * 60)
    )

    try:

        await context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=user_id,
            permissions={},
            until_date=until_date
        )

        return True

    except Exception as e:

        print(e)

        return False


# =========================
# ANTI SPAM SYSTEM
# =========================
async def anti_spam(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    # NO MESSAGE
    if not update.message:
        return

    # IGNORE EDITED
    if update.edited_message:
        return

    chat_id = update.effective_chat.id

    # GROUP NOT ACTIVE
    if chat_id not in active_groups:
        return

    user_id = update.effective_user.id

    # =========================
    # IGNORE ADMINS
    # =========================
    member = await context.bot.get_chat_member(
        chat_id,
        user_id
    )

    if member.status in [
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.OWNER
    ]:
        return

    text = (
        update.message.text or ""
    ).lower()

    # =========================
    # CREATE WARN SLOT
    # =========================
    if user_id not in warn_cache:
        warn_cache[user_id] = 0

    # =========================
    # BLOCK LINKS
    # =========================
    has_link = False

    blocked_words = [
        "http",
        "https",
        "t.me",
        "telegram.me",
        ".com",
        ".net",
        ".xyz",
        "discord.gg"
    ]

    for word in blocked_words:

        if word in text:
            has_link = True
            break

    # =========================
    # CHECK ENTITIES
    # =========================
    if update.message.entities:

        for entity in update.message.entities:

            if entity.type in [
                "url",
                "text_link"
            ]:

                has_link = True
                break

    # =========================
    # DELETE LINK
    # =========================
    if has_link:

        try:

            await update.message.delete()

            warn_cache[user_id] += 1

            # =========================
            # AUTO MUTE
            # =========================
            if warn_cache[user_id] >= 3:

                muted = await mute_user(
                    update,
                    context,
                    user_id,
                    minutes=30
                )

                if muted:

                    await context.bot.send_message(
                        chat_id,
                        f"""
🚫 تم كتم المستخدم مؤقتاً

👤 المستخدم:
{update.effective_user.first_name}

⏳ مدة الكتم:
30 دقيقة

🛡️ السبب:
إرسال روابط مزعجة متكررة
"""
                    )

                warn_cache[user_id] = 0

                return

            await context.bot.send_message(
                chat_id,
                f"""
🚫 تم حذف رابط

👤 المستخدم:
{update.effective_user.first_name}

⚠️ عدد التحذيرات:
{warn_cache[user_id]}/3

🛡️ الحماية فعالة
"""
            )

        except Exception as e:

            print(e)

        return

    # =========================
    # SPAM DETECTION
    # =========================
    now = time.time()

    if user_id not in spam_cache:
        spam_cache[user_id] = []

    spam_cache[user_id].append(now)

    # KEEP LAST 5 SECONDS
    spam_cache[user_id] = [

        t for t in spam_cache[user_id]
        if now - t < 5
    ]

    # =========================
    # MORE THAN 5 MSG
    # =========================
    if len(spam_cache[user_id]) > 5:

        try:

            await update.message.delete()

            warn_cache[user_id] += 1

            # =========================
            # AUTO MUTE
            # =========================
            if warn_cache[user_id] >= 3:

                muted = await mute_user(
                    update,
                    context,
                    user_id,
                    minutes=15
                )

                if muted:

                    await context.bot.send_message(
                        chat_id,
                        f"""
⚠️ تم كتم المستخدم

👤 المستخدم:
{update.effective_user.first_name}

⏳ مدة الكتم:
15 دقيقة

🛡️ السبب:
Spam / Flood
"""
                    )

                warn_cache[user_id] = 0

                return

            await context.bot.send_message(
                chat_id,
                f"""
⚠️ تم كشف سبام

👤 المستخدم:
{update.effective_user.first_name}

⚠️ التحذيرات:
{warn_cache[user_id]}/3

🛡️ الحماية تدخلت تلقائياً
"""
            )

        except Exception as e:

            print(e)

