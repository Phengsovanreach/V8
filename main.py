import logging
from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from config import BOT_TOKEN, WEBHOOK_URL, PORT
from downloader import get_formats, download_video, download_audio
from utils import clean_file

logging.basicConfig(level=logging.INFO)

app = FastAPI()
bot = ApplicationBuilder().token(BOT_TOKEN).build()

user_links = {}

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me video link 🎬")

# ---------------- MESSAGE ----------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    user_links[chat_id] = url

    formats = get_formats(url)

    buttons = [
        [InlineKeyboardButton(f["q"], callback_data=f"v|{f['id']}")]
        for f in formats
    ]
    buttons.append([InlineKeyboardButton("🎵 MP3", callback_data="a")])

    await update.message.reply_text(
        "Choose format:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ---------------- BUTTON ----------------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat_id
    url = user_links.get(chat_id)

    await query.edit_message_text("Processing... ⏬")

    try:
        if query.data.startswith("v|"):
            format_id = query.data.split("|")[1]
            file_path = download_video(url, format_id)
        else:
            file_path = download_audio(url)

        await context.bot.send_document(chat_id, open(file_path, "rb"))
        clean_file(file_path)

    except Exception as e:
        await context.bot.send_message(chat_id, f"Error: {e}")

# ---------------- REGISTER ----------------
bot.add_handler(CommandHandler("start", start))
bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
bot.add_handler(CallbackQueryHandler(button))

# ---------------- WEBHOOK ----------------
@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, bot.bot)
    await bot.process_update(update)
    return {"ok": True}

@app.get("/")
async def home():
    return {"status": "V8 ULTRA PRO running"}

# ---------------- STARTUP ----------------
@app.on_event("startup")
async def startup():
    await bot.initialize()
    await bot.bot.set_webhook(f"{WEBHOOK_URL}/webhook")

# ---------------- RUN ----------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)