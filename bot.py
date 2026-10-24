import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")

CHANNEL = "@denov_avto_savdo"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚗 E'lon berish — BEPUL", callback_data="new_ad")]
    ]

    await update.message.reply_text(
        "🚗 DENOV AVTO SAVDO BOT\n\n"
        "Assalomu alaykum!\n"
        "Avtomobilingizni kanalimizga bepul joylashtiring.\n\n"
        "✅ E'lonlar admin tekshiruvidan o'tadi.\n"
        "🆓 Hozircha e'lon berish mutlaqo bepul!",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "new_ad":
        await query.message.reply_text(
            "🚘 Avtomobilingizning markasi va modelini yozing.\n"
            "Masalan: Chevrolet Cobalt"
        )

def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN sozlanmagan!")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
