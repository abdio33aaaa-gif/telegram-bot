import os
import asyncio
from pyrogram import Client, filters
import yt_dlp

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("أهلاً! أرسل رابط يوتيوب")

@app.on_message(filters.text & ~filters.command("start"))
async def download(client, message):
    url = message.text
    if "youtube.com" not in url and "youtu.be" not in url:
        return
    status = await message.reply("⏳ جاري التحميل...")
    try:
        ydl_opts = {'format': 'best', 'outtmpl': '%(title)s.%(ext)s'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file = ydl.prepare_filename(info)
        await client.send_video(message.chat.id, file, caption=info.get('title',''))
        os.remove(file)
        await status.delete()
    except Exception as e:
        await status.edit(f"خطأ: {e}")

app.run()
