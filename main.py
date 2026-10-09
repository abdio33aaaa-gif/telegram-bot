import os
import threading
import tempfile
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Live OK"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 أهلاً بيك في بوت التحميل السريع\n\n"
        "طريقة الاستخدام:\n"
        "انسخ رابط الفيديو وارسله هنا فقط!\n\n"
        "📢 القناة الرسمية: @BotKanal24\n"
        "👨‍💻 المطور: السيد شيخ أحمد"
    )

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "http" not in url:
        return
    
    await update.message.reply_text("⏳ عم حمّل الفيديو، ثواني...")
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {
                'outtmpl': f'{tmpdir}/%(title).30s.%(ext)s',
                'format': 'mp4/best',
                'quiet': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)
            
            # ابعت الفيديو
            with open(file_path, 'rb') as f:
                await update.message.reply_video(video=f, caption="✅ تفضل - @BotKanal24")
                
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text(f"❌ ما قدرت حمّل الرابط\nتأكد انو الرابط صحيح وعام")

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_flask, daemon=True).start()

print(f"TOKEN OK? {bool(TOKEN)}")
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
print("Starting bot...")
application.run_polling(drop_pending_updates=True)
