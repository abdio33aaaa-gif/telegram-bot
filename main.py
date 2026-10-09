import os, threading, tempfile
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@BotKanal24"
CHANNEL_LINK = "https://t.me/BotKanal24"

app = Flask(__name__)
@app.route('/')
def home(): return "OK"

async def is_subscribed(bot, user_id):
    try:
        m = await bot.get_chat_member(CHANNEL, user_id)
        return m.status in ['member','administrator','creator']
    except: return False

def get_sub_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 اشترك بالقناة", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ تحققت - فعل البوت", callback_data="check_sub")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_subscribed(context.bot, update.effective_user.id):
        await update.message.reply_text(f"⚠️ يجب الاشتراك أولاً {CHANNEL}", reply_markup=get_sub_keyboard())
        return
    await update.message.reply_text("👋 أهلاً بيك في بوت التحميل السريع\n\nانسخ رابط الفيديو وارسله هنا فقط!\n\n📢 @BotKanal24\n👨‍💻 السيد شيخ أحمد")

async def check_sub_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if await is_subscribed(context.bot, query.from_user.id):
        await query.edit_message_text("✅ تم تفعيل البوت، أرسل الرابط الآن 🚀")
        await start(update, context) # يبعت الترحيب
    else:
        await query.answer("❌ لسه ما اشتركت، اشترك أولاً", show_alert=True)

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_subscribed(context.bot, update.effective_user.id):
        await update.message.reply_text(f"⚠️ اشترك أولاً {CHANNEL}", reply_markup=get_sub_keyboard())
        return
    url = update.message.text.strip()
    if "http" not in url: return
    msg = await update.message.reply_text("⏳ عم حمّل...")
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            opts = {
                'outtmpl': f'{tmpdir}/video.%(ext)s',
                'format': 'best[ext=mp4]/best',
                'quiet': True,
                'extractor_args': {'youtube': {'player_client': ['android']}},
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                path = ydl.prepare_filename(info)
            await context.bot.delete_message(update.effective_chat.id, msg.message_id)
            with open(path, 'rb') as f:
                await update.message.reply_video(f, caption=f"✅ @BotKanal24")
    except Exception as e:
        print(e)
        await context.bot.edit_message_text(update.effective_chat.id, msg.message_id,
            "❌ يوتيوب محظور على Render\n✅ جرب تيك توك، انستا، فيسبوك شغال 100%\n\nاذا بدك يوتيوب لازم ننقل البوت لـ VPS مدفوع")

def run_flask(): app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
threading.Thread(target=run_flask, daemon=True).start()

application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(check_sub_callback, pattern="check_sub"))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
print("Starting...")
application.run_polling(drop_pending_updates=True)
