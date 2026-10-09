import os
import threading
import tempfile
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@BotKanal24"  # قناتك
CHANNEL_LINK = "https://t.me/BotKanal24"

app = Flask(__name__)
@app.route('/')
def home(): return "OK"

async def is_subscribed(bot, user_id):
    try:
        member = await bot.get_chat_member(CHANNEL, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return True  # اذا ما قدر يتأكد خلي يكمل

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_subscribed(context.bot, update.effective_user.id):
        keyboard = [[InlineKeyboardButton("📢 اشترك بالقناة", url=CHANNEL_LINK)]]
        await update.message.reply_text(
            f"⚠️ يجب الاشتراك بقناتنا أولاً {CHANNEL} حتى تستخدم البوت",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    await update.message.reply_text(
        "👋 أهلاً بيك في بوت التحميل السريع\n\n"
        "طريقة الاستخدام:\nانسخ رابط الفيديو وارسله هنا فقط!\n\n"
        f"📢 القناة الرسمية: {CHANNEL}\n👨‍💻 المطور: السيد شيخ أحمد"
    )

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # فحص الاشتراك اول شي
    if not await is_subscribed(context.bot, update.effective_user.id):
        keyboard = [[InlineKeyboardButton("📢 اشترك بالقناة", url=CHANNEL_LINK)]]
        await update.message.reply_text(
            f"⚠️ اشترك بالقناة أولاً {CHANNEL}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    url = update.message.text.strip()
    if "http" not in url: return
    
    msg = await update.message.reply_text("⏳ عم حمّل الفيديو، ثواني...")
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {
                'outtmpl': f'{tmpdir}/video.%(ext)s',
                'format': 'mp4/best[height<=720]/best',
                'quiet': True,
                'no_warnings': True,
                # هاد الحل لمشكلة يوتيوب على Render
                'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)

            await context.bot.delete_message(update.effective_chat.id, msg.message_id)
            with open(file_path, 'rb') as f:
                await update.message.reply_video(video=f, caption=f"✅ تم التحميل - {CHANNEL}")
                
    except Exception as e:
        print(f"Error: {e}")
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=msg.message_id,
            text="❌ ما قدرت حمّل الرابط\nجرب رابط تيك توك أو انستا، يوتيوب محظور أحياناً على السيرفر"
        )

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

threading.Thread(target=run_flask, daemon=True).start()
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
print("Starting bot...")
application.run_polling(drop_pending_updates=True)
