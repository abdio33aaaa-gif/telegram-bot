import os
import asyncio
from flask import Flask
from threading import Thread
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# =========== الاعدادات ===========
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME", "ALBASHA") # غيرها ليوزر قناتك بدون @
CHANNEL_LINK = f"https://t.me/{CHANNEL_USERNAME}"

# =========== سيرفر مشان UptimeRobot ===========
app = Flask('')
@app.route('/')
def home():
    return "Bot is Alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# =========== فحص الاشتراك الاجباري ===========
async def is_subscribed(user_id, context):
    try:
        member = await context.bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return True # اذا ما قدر يفحص خليه يمرق

# =========== رسالة الترحيب الجديدة ===========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("📢 اشترك بالقناة", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ تحققت من الاشتراك", callback_data="check_sub")]
    ]
    # بنعمل فحص اول
    if not await is_subscribed(user.id, context):
        await update.message.reply_text(
            f"أهلاً {user.first_name} 👋\n\n"
            f"⚠️ يجب الاشتراك في قناتنا أولاً لتستخدم البوت\n\n"
            f"اشترك وبعدين اضغط تحققت",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    await update.message.reply_text(
        f"أهلاً وسهلاً {user.first_name} يا باشا 👑\n\n"
        f"🚀 **بوت تحميل الباشا - أسرع بوت تحميل**\n\n"
        f"📥 يدعم:\n"
        f"• يوتيوب (فيديو - صوت)\n"
        f"• تيك توك - انستا - فيسبوك\n\n"
        f"👇 فقط أرسل رابط الفيديو ورح حملو فوراً\n\n"
        f"المطور: @{CHANNEL_USERNAME}"
    )

# =========== تحميل الفيديو - محدث لفك حظر يوتيوب ===========
async def download_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    url = update.message.text.strip()

    # فحص الاشتراك
    if not await is_subscribed(user_id, context):
        keyboard = [[InlineKeyboardButton("📢 اشترك بالقناة", url=CHANNEL_LINK)]]
        await update.message.reply_text(
            "❌ يجب الاشتراك بالقناة أولاً",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if "http" not in url:
        return

    msg = await update.message.reply_text("⏳ عم حمل... ثواني يا باشا...")

    ydl_opts = {
        'format': 'best[ext=mp4]/bestaudio[ext=m4a]/best',
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'extractor_args': {
           
