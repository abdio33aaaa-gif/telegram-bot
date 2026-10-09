import os
import threading
from flask import Flask
from telegram.ext import Application, CommandHandler
from telegram import Update

TOKEN = os.getenv("BOT_TOKEN")
app = Flask(__name__)

@app.route('/')
def home():
    return "OK"

async def start(update: Update, context):
    await update.message.reply_text(
        "👋 أهلاً بيك في بوت التحميل السريع\n\n"
        "طريقة الاستخدام:\n"
        "انسخ رابط الفيديو وارسله هنا فقط!\n\n"
        "📢 القناة الرسمية: @BotKanal24\n"
        "👨‍💻 المطور: السيد شيخ أحمد"
    )

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_flask, daemon=True).start()

print(f"TOKEN OK? {bool(TOKEN)}")
print("Starting bot...")
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.run_polling(drop_pending_updates=True)
