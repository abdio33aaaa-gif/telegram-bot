import os
from pyrogram import Client, filters
from yt_dlp import YoutubeDL

# قراءة المتغيرات بشكل آمن تماماً لتجنب انهيار البوت
api_id_env = os.getenv("API_ID")
API_ID = int(api_id_env) if api_id_env and api_id_env.isdigit() else 0
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

app = Client("youtube_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
