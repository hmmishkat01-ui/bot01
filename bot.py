from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8725525204:AAFcY4eYmGaba9iHen64pi5mUZLllTRW3pE"

ADMIN_ID = 8173902419
WHATSAPP_LINK = "https://wa.me/8801676631455"
BKASH_NUMBER = "01711974357"
GROUP_LINK = "https://chat.whatsapp.com/GKpKHEXkzh6CA88k9cjX1f"

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📝 Admission নিতে চাই", callback_data="admission")],
        [InlineKeyboardButton("💬 Help / WhatsApp", url=WHATSAPP_LINK)]
    ]

    await update.message.reply_text(
        "আসসালামু আলাইকুম 👋\n\n"
        "🎓 Sky IT Premium Admission Bot-এ আপনাকে স্বাগতম।\n\n"
        "Admission নিতে নিচের বাটনে চাপ দিন।\n"
        "কোনো সমস্যা হলে Help / WhatsApp চাপুন।",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "admission":
        user_data[user_id] = {"step": "name"}
        await query.message.reply_text("👤 আপনার পূর্ণ নাম লিখুন:")

    elif query.data == "pay_bkash":
        user_data[user_id]["payment_method"] = "bKash"
        user_data[user_id]["step"] = "trxid"

        await query.message.reply_text(
            "💳 bKash Payment Instruction\n\n"
            f"📱 bKash Personal Number: {BKASH_NUMBER}\n\n"
            "এই নাম্বারে টাকা Send Money করুন।\n"
            "Payment করার পর Transaction ID লিখুন।"
        )

    elif query.data.startswith("approve_"):
        if user_id != ADMIN_ID:
            await query.message.reply_text("❌ আপনার permission নেই।")
            return

        target_id = int(query.data.split("_")[1])
        data = user_data.get(target_id)

        if not data:
            await query.message.reply_text("Data পাওয়া যায়নি।")
            return

        data["status"] = "Approved"

        await context.bot.send_message(
            target_id,
            "✅ অভিনন্দন!\n\n"
            "আপনার admission complete হয়েছে।\n\n"
            f"👉 আমাদের premium group link:\n{GROUP_LINK}"
        )

        await query.message.reply_text("✅ Admission approved. User-কে group link পাঠানো হয়েছে।")

    elif query.data.startswith("reject_"):
        if user_id != ADMIN_ID:
            await query.message.reply_text("❌ আপনার permission নেই।")
            return

        target_id = int(query.data.split("_")[1])

        if target_id in user_data:
            user_data[target_id]["status"] = "Rejected"

        await context.bot.send_message(
            target_id,
            "❌ দুঃখিত, আপনার admission request reject হয়েছে।\n\n"
            "Payment info ভুল হলে Help / WhatsApp-এ যোগাযোগ করুন।"
        )

        await query.message.reply_text("❌ Request rejected.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()

    if user_id not in user_data:
        await update.message.reply_text("Admission শুরু করতে /start দিন।")
        return

    step = user_data[user_id].get("step")

    if step == "name":
        user_data[user_id]["name"] = text
        user_data[user_id]["step"] = "phone"
        await update.message.reply_text("📞 আপনার ফোন/WhatsApp নাম্বার লিখুন:")

    elif step == "phone":
        user_data[user_id]["phone"] = text
        user_data[user_id]["step"] = "payment"

        keyboard = [
            [InlineKeyboardButton("💳 bKash Payment", callback_data="pay_bkash")],
            [InlineKeyboardButton("💬 Help / WhatsApp", url=WHATSAPP_LINK)]
        ]

        await update.message.reply_text(
            "আপনি কোন মাধ্যমে payment করবেন?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif step == "trxid":
        user_data[user_id]["trxid"] = text
        user_data[user_id]["step"] = "screenshot"

        await update.message.reply_text(
            "📸 এখন payment screenshot পাঠান।\n\n"
            "Screenshot ছাড়া admission verify করা যাবে না।"
        )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in user_data:
        await update.message.reply_text("Admission শুরু করতে /start দিন।")
        return

    if user_data[user_id].get("step") != "screenshot":
        await update.message.reply_text("এখন screenshot দরকার নেই।")
        return

    data = user_data[user_id]
    data["status"] = "Pending Approval"

    admin_message = (
        "📥 নতুন Admission Request\n\n"
        f"👤 Name: {data.get('name')}\n"
        f"📞 Phone: {data.get('phone')}\n"
        f"💳 Payment Method: {data.get('payment_method')}\n"
        f"🧾 Transaction ID: {data.get('trxid')}\n"
        f"🆔 Telegram ID: {user_id}\n\n"
        "Payment screenshot নিচে forwarded করা হয়েছে।"
    )

    keyboard = [
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
        ]
    ]

    await context.bot.send_message(
        ADMIN_ID,
        admin_message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await context.bot.forward_message(
        chat_id=ADMIN_ID,
        from_chat_id=update.message.chat_id,
        message_id=update.message.message_id
    )

    await update.message.reply_text(
        "✅ আপনার admission request submit হয়েছে।\n\n"
        "Admin payment verify করলে আপনাকে group link পাঠানো হবে।"
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Sky IT Premium Admission Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()