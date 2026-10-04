import os, telebot, glob, re, requests
from telebot import types
import yt_dlp

TOKEN = os.getenv("TOKEN")
CHANNEL = "@BotKanal24"
CHANNEL_LINK = "https://t.me/BotKanal24"
bot = telebot.TeleBot(TOKEN)

WELCOME = "اهلا 😍 ابعت رابط وخلّي الباقي عليي 🚀"

PIPED_APIS = [
    "https://pipedapi.kavin.rocks",
    "https://pipedapi.adminforge.de",
    "https://api.piped.private.coffee"
]

def is_subscribed(uid):
    try:
        m = bot.get_chat_member(CHANNEL, uid)
        return m.status in ['member','administrator','creator']
    except:
        return True

def get_yt_id(url):
    m = re.search(r'(?:youtu\.be/|shorts/|v=)([A-Za-z0-9_-]{11})', url)
    return m.group(1) if m else None

def download_via_piped(yt_id, user_id):
    for api in PIPED_APIS:
        try:
            r = requests.get(f"{api}/streams/{yt_id}", timeout=15).json()
            if "videoStreams" not in r:
                continue
            best = None
            for st in r["videoStreams"]:
                # نفضل mp4 فيه صوت وصورة
                if "mp4" in st.get("mimeType","") and not st.get("videoOnly"):
                    best = st["url"]
                    break
            if not best:
               
