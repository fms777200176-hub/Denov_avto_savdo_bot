import os
import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8545646821
CHANNEL = "@denov_avto_savdo"

FIELDS = [
    ("model", "🚗 Mashina markasi va modeli"),
    ("year", "📅 Ishlab chiqarilgan yili"),
    ("gearbox", "⚙️ Korobkasi"),
    ("fuel", "⛽ Yoqilg‘i turi"),
    ("mileage", "🛣 Yurgan masofasi (km)"),
    ("color", "🎨 Rangi va holati"),
    ("currency", "💰 Narx valyutasi"),
    ("price", "💵 Narxi"),
    ("location", "📍 Joylashuvi"),
    ("phone", "📞 Telefon raqami"),
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton(
            "🚗 E’lon berish — BEPUL",
            callback_data="new_ad"
        )
    ]]

    await update.message.reply_text(
        "🚘 DENOV AVTO SAVDO BOT\n\n"
        "Assalomu alaykum!\n"
        "🎉 Hozircha e’lon joylashtirish mutlaqo bepul!\n\n"
        "E’loningiz admin tekshiruvidan so‘ng kanalga joylanadi.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "new_ad":
        context.user_data["ad"] = {}
        context.user_data["step"] = 0
        await ask_next(query.message, context)

    elif query.data == "uzs":
        context.user_data["ad"]["currency"] = "so‘m"
        context.user_data["step"] += 1
        await ask_next(query.message, context)

    elif query.data == "usd":
        context.user_data["ad"]["currency"] = "AQSH dollari"
        context.user_data["step"] += 1
        await ask_next(query.message, context)

    elif query.data == "approve":
        ad_text = context.user_data.get("pending_ad")
        if ad_text:
            await context.bot.send_message(
                chat_id=CHANNEL,
                text=ad_text,
            )
            await query.edit_message_text("✅ E’lon kanalga joylandi!")

    elif query.data == "reject":
        await query.edit_message_text("❌ E’lon rad etildi.")

async def ask_next(message, context):
    step = context.user_data.get("step", 0)

    if step >= len(FIELDS):
        await send_for_approval(message, context)
        return

    key, question = FIELDS[step]

    if key == "currency":
        keyboard = [[
            InlineKeyboardButton("🇺🇿 So‘m", callback_data="uzs"),
            InlineKeyboardButton("🇺🇸 Dollar", callback_data="usd"),
        ]]
        await message.reply_text(
            "💰 Narx qaysi valyutada?",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    else:
        await message.reply_text(question + "ni kiriting:")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "ad" not in context.user_data:
        await update.message.reply_text(
            "Boshlash uchun /start buyrug‘ini yuboring."
        )
        return

    step = context.user_data.get("step", 0)

    if step >= len(FIELDS):
        return

    key, _ = FIELDS[step]

    if key == "currency":
        await update.message.reply_text(
            "Valyutani yuqoridagi tugmalardan tanlang."
        )
        return

    context.user_data["ad"][key] = update.message.text.strip()
    context.user_data["step"] = step + 1

    await ask_next(update.message, context)

async def send_for_approval(message, context):
    ad = context.user_data["ad"]

    text = (
        "🚗 DENOV AVTO SAVDO — SOTILADI!\n\n"
        f"🚘 Avtomobil: {ad.get('model', '')}\n"
        f"📅 Yili: {ad.get('year', '')}\n"
        f"⚙️ Korobka: {ad.get('gearbox', '')}\n"
        f"⛽ Yoqilg‘i: {ad.get('fuel', '')}\n"
        f"🛣 Yurgani: {ad.get('mileage', '')} km\n"
        f"🎨 Rangi/holati: {ad.get('color', '')}\n"
        f"💰 Narxi: {ad.get('price', '')} {ad.get('currency', '')}\n"
        f"📍 Manzil: {ad.get('location', '')}\n"
        f"📞 Telefon: {ad.get('phone', '')}\n\n"
        "🆓 E’lon hozircha bepul."
    )

    context.user_data["pending_ad"] = text

    keyboard = [[
        InlineKeyboardButton("✅ Kanalga joylash", callback_data="approve"),
        InlineKeyboardButton("❌ Rad etish", callback_data="reject"),
    ]]

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    await message.reply_text(
        "✅ E’loningiz adminga tekshirish uchun yuborildi!\n"
        "Tasdiqlangach kanalga joylanadi."
    )

def main():
    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN topilmadi. Uni server sozlamalarida kiriting."
        )

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()

if __name__ == "__main__":
    main()
