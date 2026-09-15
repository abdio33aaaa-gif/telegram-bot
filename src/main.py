import os
import asyncio

# هذا السطر هو يلي كان معطل البوت كلو!
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

from pyrogram import Client, filters
import yt_dlp

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("🟢 البوت يعمل الآن!\nأهلاً بك في بوت تحميل الفيديوهات!\n\nارسل رابط من YouTube / TikTok / Instagram / Facebook")

@app.on_message(filters.text & ~filters.command("start"))
async def download(client, message):
    url = message.text.strip()
    if not url.startswith("http"):
        return
    msg = await message.reply("⏳ جاري التحميل...")
    try:
        ydl_opts = {'format': 'best', 'outtmpl': 'video.%(ext)s', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        await message.reply_video(filename, caption="✅ تم التحميل!")
        os.remove(filename)
        await msg.delete()
    except Exception as e:
        await msg.edit(f"❌ فشل التحميل: {e}")

print("Bot started!")
app.run()
