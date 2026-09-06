import os
from pyrogram import Client, filters
from yt_dlp import YoutubeDL

# بيانات البوت (سنقوم لاحقاً بإضافتها كمتغيرات بيئية في Render)
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

app = Client("youtube_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
def start(client, message):
    message.reply_text("أهلاً بك! أرسل لي رابط فيديو من يوتيوب وسأقوم بتحميله لك فوراً.")

@app.on_message(filters.text & ~filters.command("start"))
def download_video(client, message):
    url = message.text
    if "youtube.com" not in url and "youtu.be" not in url:
        message.reply_text("الرجاء إرسال رابط يوتيوب صحيح.")
        return

    status_message = message.reply_text("جاري بدء التحميل...")

    cookie_path = "cookies.txt" if os.path.exists("cookies.txt") else None

    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'cookiefile': cookie_path,
    }

    try:
        status_message.edit_text("جاري تحميل الفيديو من يوتيوب...")
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        status_message.edit_text("جاري الرفع إلى تيليجرام...")
        app.send_video(message.chat.id, video=filename, caption=info.get('title', ''))
        
        # حذف الملف بعد الإرسال لتوفير المساحة
        if os.path.exists(filename):
            os.remove(filename)
            
        status_message.delete()
    except Exception as e:
        status_message.edit_text(f"حدث خطأ أثناء التحميل: {str(e)}")

app.run()
