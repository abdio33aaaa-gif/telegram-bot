import os
import threading
import tempfile
import requests
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@BotKanal24"
CHANNEL_LINK = "https://t.me/BotKanal24"

app = Flask(__name__)
@app.route('/')
def home():
    return "Bot Running - 61 Users OK"

async def is_subscribed(bot, user_id):
    try:
        m = await bot.get_chat_member(CHANNEL, user_id)
        return m.status in ['member','administrator','creator']
    except:
        return True

def get_sub_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 اشترك بالقناة", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ تحققت", callback_data="check_sub")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_subscribed(context.bot, update.effective_user.id):
        await update.message.reply_text("⚠️ اشترك أولاً", reply_markup=get_sub_keyboard())
        return
    text = """🚀 بوت التحميل السريع 2026

⚡️ يحمل من:
• TikTok بدون علامة
• Instagram Reels & Story
• Facebook
• YouTube MP4/MP3

📎 أرسل الرابط الآن ليبدأ التحميل

👨‍💻 @BotKanal24"""
    await update.message.reply_text(text)

async def check_sub_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if await is_subscribed(context.bot, query.from_user.id):
        await query.edit_message_text("✅ تم التفعيل!")
        await context.bot.send_message(chat_id=query.from_user.id, text="🚀 تم التفعيل\n📎 أرسل الرابط الآن")
    else:
        await query.answer("❌ لسه ما اشتركت", show_alert=True)

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_subscribed(context.bot, update.effective_user.id):
        await update.message.reply_text("⚠️ اشترك أولاً", reply_markup=get_sub_keyboard())
        return
    url = update.message.text.strip()
    if "http" not in url:
        return
    msg = await update.message.reply_text("⚡️ ثانية...")
    try:
        # فك روابط vm.tiktok
        if "vm.tiktok.com" in url or "vt.tiktok.com" in url:
            try:
                r = requests.get(url, allow_redirects=True, timeout=10, headers={"User-Agent":"Mozilla/5.0"})
                url = r.url
            except: pass
        
        # تيك توك API قوي ما بينحظر
        if "tiktok.com" in url:
            try:
                api = f"https://www.tikwm.com/api/?url={url}&hd=1"
                res = requests.get(api, headers={"User-Agent":"Mozilla/5.0"}, timeout=20).json()
                if res.get("code") == 0 and res["data"].get("play"):
                    video_url = res["data"]["play"]
                    await context.bot.delete_message(update.effective_chat.id, msg.message_id)
                    await update.message.reply_video(video=video_url, caption="✅ بدون علامة مائية\n📢 @BotKanal24")
                    return
            except Exception as e:
                print(f"TikTok API error: {e}")

        # fallback باقي المنصات
        with tempfile.TemporaryDirectory() as tmpdir:
            opts = {'outtmpl': f'{tmpdir}/%(title)s.%(ext)s','format':'best[ext=mp4]/best','quiet':True,'noplaylist':True}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                path = ydl.prepare_filename(info)
            await context.bot.delete_message(update.effective_chat.id, msg.message_id)
            with open(path, 'rb') as f:
                await update.message.reply_video(f, caption="✅ @BotKanal24")

    except Exception as e:
        print(e)
        try:
            await context.bot.edit_message_text(update.effective_chat.id, msg.message_id, "❌ ما قدرت حملو، جرب رابط تاني")
        except: pass

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
threading.Thread(target=run_flask, daemon=True).start()

application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(check_sub_callback, pattern="check_sub"))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
application.run_polling(drop_pending_updates=True)
