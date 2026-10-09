import os
from flask import Flask
from threading import Thread
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_USERNAME = "BotKanal24"  # قناتك
CHANNEL_LINK = f"https://t.me/{CHANNEL_USERNAME}"

# ===== سيرفر مشان ما يوقع =====
app = Flask('')
@app.route('/')
def home(): return "Bot is Alive!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# ===== فحص الاشتراك =====
async def is_subscribed(user_id, context):
    try:
        m = await context.bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return m.status in ['member','administrator','creator']
    except:
        return False

# ===== /start مع الرسالة الجديدة =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not await is_subscribed(user_id, context):
        keyboard = [
            [InlineKeyboardButton("📢 القناة الرسمية", url=CHANNEL_LINK)],
            [InlineKeyboardButton("✅ تحققت من الاشتراك", callback_data="check")]
        ]
        await update.message.reply_text(
            f"أهلاً بك عزيزي 👋\n\n"
            f"⚠️ يجب الاشتراك في قناتنا أولاً لتستخدم البوت\n"
            f"القناة: @{CHANNEL_USERNAME}\n\n"
            f"اشترك ثم اضغط تحققت",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # هاي الرسالة يلي بدك ياها متل الصورة
    await update.message.reply_text(
        "ماذا يمكن لهذا البوت فعله؟\n\n"
        "🚀 بوت التحميل الخارق - أسرع بوت تحميل\n\n"
        "تيك توك - انستغرام - فيسبوك - يوتيوب\n\n"
        "ماذا أقدم لك؟ 👇\n"
        "✅ تيك توك بدون علامة مائية\n"
        "✅ انستا ريلز وستوري بجودة عالية\n"
        "✅ فيسبوك بضغطة واحدة\n"
        "✅ يوتيوب فيديو MP4 وصوت MP3\n"
        "✅ سريع جداً ويعمل 24 ساعة\n\n"
        "طريقة الاستخدام:\n"
        "انسخ رابط الفيديو وارسله هنا فقط!\n\n"
        f"📢 القناة الرسمية: @{CHANNEL_USERNAME}\n"
        "👨‍💻 المطور: السيد شيخ أحمد"
    )

async def check_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if await is_subscribed(query.from_user.id, context):
        await query.message.delete()
        await query.message.reply_text(
            "ماذا يمكن لهذا البوت فعله؟\n\n"
            "🚀 بوت التحميل الخارق - أسرع بوت تحميل\n\n"
            "تيك توك - انستغرام - فيسبوك - يوتيوب\n\n"
            "ماذا أقدم لك؟ 👇\n"
            "✅ تيك توك بدون علامة مائية\n"
            "✅ انستا ريلز وستوري بجودة عالية\n"
            "✅ فيسبوك بضغطة واحدة\n"
            "✅ يوتيوب فيديو MP4 وصوت MP3\n"
            "✅ سريع جداً ويعمل 24 ساعة\n\n"
            "طريقة الاستخدام:\n"
            "انسخ رابط الفيديو وارسله هنا فقط!\n\n"
            f"📢 القناة الرسمية: @{CHANNEL_USERNAME}\n"
            "👨‍💻 المطور: السيد شيخ أحمد"
        )
    else:
        await query.answer("❌ لسه ما اشتركت! اشترك أولاً", show_alert=True)

# ===== التحميل - مع حل حظر يوتيوب =====
async def downloader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_subscribed(update.effective_user.id, context):
        return await start(update, context)
    
    url = update.message.text
    if "http" not in url: return

    status = await update.message.reply_text("⏳ عم حمل... ثواني يا باشا...")

    opts = {
        'format': 'best[ext=mp4]/bestaudio/best',
        'quiet': True,
        'nocheckcertificate': True,
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
        'http_headers': {'User-Agent': 'Mozilla/5.0'}
    }

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        
        await context.bot.send_video(
            chat_id=update.effective_chat.id,
            video=open(filename, 'rb'),
            caption=f"✅ تم التحميل\n📢 @{CHANNEL_USERNAME}"
        )
        os.remove(filename)
        await status.delete()
    except Exception as e:
        print(e)
        await status.edit_text("❌ ما قدرت حملو، جرب رابط فيديو تاني مباشر مو قائمة تشغيل")

if __name__ == '__main__':
    keep_alive()
    bot = ApplicationBuilder().token(BOT_TOKEN).build()
    bot.add_handler(CommandHandler("start", start))
    bot.add_handler(CallbackQueryHandler(check_callback))
    bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, downloader))
    print("Bot Started")
    bot.run_polling()
