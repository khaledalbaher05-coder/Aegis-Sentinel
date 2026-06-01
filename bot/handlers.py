from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler
)

from bot.database import (
    get_user_balance,
    get_all_services,
    add_balance,
    deduct_balance,
    transaction_exists,
    save_transaction
)

from bot.payments import verify_transaction

from bot.config import WALLET_ADDRESS


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = (
        "🦅 رادار السايبر والبرمجة\n\n"
        "مرحباً بك في النظام 👋\n"
        "اختر أحد الخيارات التالية:"
    )

    kb = [
        [
            InlineKeyboardButton(
                "🛒 تصفح الخدمات",
                callback_data="buy_server"
            )
        ],
        [
            InlineKeyboardButton(
                "💰 محفظتي",
                callback_data="balance_info"
            )
        ]
    ]

    if update.callback_query:

        await update.callback_query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(kb)
        )

    else:

        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(kb)
        )


async def button_handler(update, context):

    query = update.callback_query

    print("BUTTON:", query.data)

    await query.answer()

    if query.data == "start":

        await start(update, context)

    elif query.data == "balance_info":

        bal = get_user_balance(query.from_user.id)

        kb = [
            [
                InlineKeyboardButton(
                    "🔙 رجوع",
                    callback_data="start"
                )
            ]
        ]

        await query.edit_message_text(
            f"💰 رصيدك الحالي:\n{bal}$",
            reply_markup=InlineKeyboardMarkup(kb)
        )

    elif query.data == "pay_info":

        text = (
            "💳 شحن الرصيد عبر USDT TRC20\n\n"
            f"{WALLET_ADDRESS}\n\n"
            "بعد التحويل أرسل:\n"
            "/pay TX_HASH"
        )

        kb = [
            [
                InlineKeyboardButton(
                    "🔙 رجوع",
                    callback_data="start"
                )
            ]
        ]

        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(kb)
        )

    elif query.data == "buy_server":

        srvs = get_all_services()

        if not srvs:

            await query.edit_message_text(
                "❌ لا توجد خدمات متاحة حالياً"
            )

            return

        kb = [
            [
                InlineKeyboardButton(
                    f"{name} - ({price}$)",
                    callback_data=f"select_{srv_id}"
                )
            ]
            for srv_id, name, price in srvs
        ]

        kb.append([
            InlineKeyboardButton(
                "🔙 رجوع",
                callback_data="start"
            )
        ])

        await query.edit_message_text(
            "🛒 اختر الخدمة المطلوبة:",
            reply_markup=InlineKeyboardMarkup(kb)
        )

    elif query.data.startswith("select_"):

        srv_id = int(query.data.split("_")[1])

        services = get_all_services()

        service = next(
            (s for s in services if s[0] == srv_id),
            None
        )

        if not service:

            await query.edit_message_text(
                "❌ الخدمة غير موجودة"
            )

            return

        _, name, price = service

        kb = [
            [
                InlineKeyboardButton(
                    "✅ تأكيد الطلب",
                    callback_data=f"confirm_{srv_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔙 رجوع",
                    callback_data="buy_server"
                )
            ]
        ]

        await query.edit_message_text(
            f"❓ هل تريد شراء:\n\n{name}\n\nبسعر {price}$ ؟",
            reply_markup=InlineKeyboardMarkup(kb)
        )

    elif query.data.startswith("confirm_"):

        srv_id = int(query.data.split("_")[1])

        services = get_all_services()

        service = next(
            (s for s in services if s[0] == srv_id),
            None
        )

        if not service:

            await query.edit_message_text(
                "❌ الخدمة غير موجودة"
            )

            return

        _, name, price = service

        balance = get_user_balance(
            query.from_user.id
        )

        if balance >= price:

            success = deduct_balance(
                query.from_user.id,
                price
            )

            if success:

                await query.edit_message_text(
                    f"🎉 تم تنفيذ الطلب بنجاح\n\nالخدمة: {name}"
                )

            else:

                await query.edit_message_text(
                    "❌ حدث خطأ أثناء تنفيذ العملية"
                )

        else:

            need = round(price - balance, 2)

            kb = [
                [
                    InlineKeyboardButton(
                        "💳 شحن الرصيد",
                        callback_data="pay_info"
                    )
                ]
            ]

            await query.edit_message_text(
                f"❌ الرصيد غير كافٍ\n\nالمبلغ المطلوب: {need}$",
                reply_markup=InlineKeyboardMarkup(kb)
            )


async def pay_command(update, context):

    if not context.args:

        await update.message.reply_text(
            "❌ طريقة الاستخدام:\n/pay TX_HASH"
        )

        return

    tx_hash = context.args[0]

    if transaction_exists(tx_hash):

        await update.message.reply_text(
            "❌ تم استخدام هذه العملية مسبقاً"
        )

        return

    await update.message.reply_text(
        "⏳ جاري التحقق من عملية الدفع..."
    )

    is_valid, amt = verify_transaction(tx_hash)

    if is_valid:

        save_transaction(
            tx_hash,
            update.effective_user.id,
            amt
        )

        add_balance(
            update.effective_user.id,
            amt
        )

        await update.message.reply_text(
            f"✅ تم إضافة الرصيد بنجاح\n\nالمبلغ: {amt}$"
        )

        await start(update, context)

    else:

        await update.message.reply_text(
            "❌ العملية غير صالحة أو لم يتم العثور عليها"
        )


async def send_jobs_to_channel(context):
    pass


def setup_handlers(app):

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("pay", pay_command)
    )

    app.add_handler(
        CallbackQueryHandler(button_handler)
    )
