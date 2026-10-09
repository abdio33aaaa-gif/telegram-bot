import os
from flask import Flask
from threading import Thread
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_USERNAME = "BotKanal24"
CHANNEL_LINK = f"https://t.me/{CHANNEL_USERNAME}"

print(f"TOKEN FOUND: {bool(BOT_TOKEN)}") # رح يبين باللوغ

app = Flask('')
@app.route('/')
def home(): return "Bot is Alive! Go to Telegram"
def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
def keep_alive():
    Thread(target=run).start()

async def is_subscribed(user_id, context):
    try:
        m = await context.bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return m.status in ['member','administrator','creator']
    except:
        return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_subscribed(update.effective_user.id, context):
        kb = [[InlineKeyboardButton("📢 اشترك بالقناة", url=CHANNEL_LINK)],
              [InlineKeyboardButton("✅ تحققت ✅", callback_data="check")]]
        await update.message.reply_text(f"⚠️ يجب الاشتراك اولاً بقناة @{CHANNEL_USERNAME} حتى تستخدم البوت", reply_markup=InlineKeyboardMarkup(kb))
        return
    await update.message.reply_text(
        "ماذا يمكن لهذا البوت فعله؟\n\n"
        "🚀 بوت التحميل الخارق - أسرع بوت تحميل\n"
        "تيك توك - انستغرام - فيسبوك - يوتيوب\n\n"
        "✅ تيك توك بدون علامة مائية\n"
        "✅ انستا ريلز وستوري\n"
        "✅ فيسبوك بضغطة\n"
        "✅ يوتيوب MP4 و MP3\n"
        "✅ سريع ويعمل 24 ساعة\n\n"
        "انسخ رابط الفيديو وارسله هنا فقط!\n\n"
        f"📢 القناة الرسمية: @{CHANNEL_USERNAME}\n"
        "👨‍💻 المطور: السيد شيخ أحمد"
    )

async def check_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if await is_subscribed(q.from_user.id, context):
        try: await q.message.delete()
        except: pass
        await q.message.reply_text(
            "🚀 بوت التحميل الخارق جاهز!\n\n"
            "انسخ رابط الفيديو وارسله هنا فقط!\n\n"
            f"📢 القناة: @{CHANNEL_USERNAME}"
        )
    else:
        await q.answer("❌ لسه ما اشتركت بالقناة", show_alert=True)

async def downloader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_subscribed(update.effective_user.id, context):
        return await start(update, context)
    url = update.message.text.strip()
    if "http" not in url: return
    status = await update.message.reply_text("⏳ عم حمل... ثواني وبيوصل...")
    opts = {
        'format': 'best[ext=mp4]/bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            fn = ydl.prepare_filename(info)
        await context.bot.send_video(chat_id=update.effective_chat.id, video=open(fn,'rb'), caption=f"✅ تم التحميل عبر @{CHANNEL_USERNAME}")
        os.remove(fn)
        await status.delete()
    except Exception as e:
        print(f"DOWNLOAD ERROR: {e}")
        await status.edit_text(f"❌ ما قدرت حلو الرابط\nالسبب: يوتيوب حاظر السيرفرات المجانية جرب تيك توك او انستا")

if __name__ == '__main__':
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN NOT SET IN RENDER ENVIRONMENT!")
    else:
        print("Starting bot polling...")
        keep_alive()
        bot = ApplicationBuilder().token(BOT_TOKEN).build()
        bot.add_handler(CommandHandler("start", start))
        bot.add_handler(CallbackQueryHandler(check_callback))
        bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, downloader))
        bot.run_polling()
