import os
import threading
import requests
import yt_dlp
import re
import telebot
from flask import Flask

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Fixed - No Indent Error"

def expand_tiktok(short_url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)'
        }
        s = requests.Session()
        r = s.get(short_url, headers=headers, allow_redirects=True, timeout=20)
        long_url = r.url
        if "vm.tiktok" in long_url or "vt.tiktok" in long_url:
            m = re.search(r'https://www\.tiktok\.com/@[^/]+/video/\d+', r.text)
            if m:
                return m.group(0)
        return long_url
    except:
        return short_url

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id,
        "🚀 أهلا بك في بوت التحميل السريع!\n\n"
        "📥 المنصات المدعومة:\n"
        "• TikTok\n"
        "• Instagram\n"
        "• Facebook\n\n"
        "أرسل رابط فيديو عام وسأحاول تنزيله بأفضل جودة.\n\n"
        "@MyDownload2026_bot")

@bot.message_handler(func=lambda m: True)
def handle(m):
    url = m.text.strip().split()[0]
    if not url.startswith("http"):
        return
    wait = bot.send_message(m.chat.id, "⚡️ جاري التحميل...")
    try:
        if "vm.tiktok.com" in url or "vt.tiktok.com" in url:
            url = expand_tiktok(url)

        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info
