import os
from pyrogram import Client, filters
import yt_dlp

# جلب بيانات البوت تلقائياً من إعدادات رندر البيئية لتكون بأمان تام
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text("أهلاً بك! البوت يعمل بنجاح وجاهز لتحميل الفيديوهات عبر yt-dlp.")

# تشغيل البوت
print("البوت يبدأ بالتشغيل الآن...")
app.run()
