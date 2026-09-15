import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً! 🚀\nابعتلي رابط من يوتيوب - تيك توك - انستا - فيسبوك")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith("http"):
        return
    await update.message.reply_text("⏳ عم حمّل... ثواني بس")

    # خيارات اقوى لتيك توك والباقي
    ydl_opts = {
        'outtmpl': 'video.%(ext)s',
        'format': 'mp4/best/bv*+ba',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'extractor_args': {
            'youtube': {'player_client': ['android']},
            'tiktok': {'api_hostname': 'api16-normal-c-useast1a.tiktokv.com', 'webpage_api': True},
            'instagram': {'api_version': 'v1'}
        },
        'http_headers': {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15'}
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            # اذا الملف webm غيرو ل mp4
            if not os.path.exists(filename):
                for f in os.listdir('.'):
                    if f.startswith('video.'):
                        filename = f
                        break

        await update.message.reply_video(video=open(filename, 'rb'), caption="تم ✅ @بوتك")
        os.remove(filename)
    except Exception as e:
        await update.message.reply_text(f"❌ ما قدرت حمّل هالرابط\nجرب رابط تاني اطول من تيك توك ( مو vm )\n\nالخطأ: {e}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
app.run_polling()
