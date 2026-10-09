import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
print(f"TOKEN FOUND: {bool(TOKEN)}")

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("اهلا! ابعتلي رابط تيك توك او انستا او فيسبوك 🎥")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"استلمت الرابط: {update.message.text}\nجاري التحميل... (هون بتحط كود التحميل)")

def run_bot():
    if not TOKEN:
        print("ERROR: BOT_TOKEN not set in Render Environment!")
        return
    print("Starting bot polling...")
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters
