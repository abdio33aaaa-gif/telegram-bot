import os, threading, requests, yt_dlp, re
import telebot
from flask import Flask

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Fixed - TikTok vm working"

def expand_tiktok(short_url):
    """يحل رابط vm.tiktok.com حتى لو تيك توك حاطط حماية"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8'
        }
        # تيك توك بيعمل تحويل مرتين، لازم نتابعو
        s = requests.Session()
        r = s.get(short_url, headers=headers, allow_redirects=True, timeout=20)
        # طلع الرابط الطويل من الصفحة
        long_url = r.url
        # اذا لسا قصير، دور على الرابط بالـ HTML
        if "vm.tiktok" in long_url or "vt.tiktok" in long_url:
            m = re.search(r'https://www\.tiktok\.com/@[^/]+/video/\d+', r.text)
            if m:
                return m.group(0)
        return long_url
    except Exception as e:
        print(f"Expand fail: {e}")
        return short_url

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id,
        "🚀 أهلاً بك في بوت التحميل السريع!\n\n"
        "📥 المنصات المدعومة:\n• TikTok\n• Instagram\n• Facebook\n\n"
        "أرسل رابط فيديو عام وسأحاول تنزيله بأفضل جودة متاحة.\n\n"
        "⚠️ المحتوى الخاص قد لا يعمل.\n\n@MyDownload2026_bot"
    )

@bot.message_handler(func=lambda m: True)
def handle(m):
    url = m.text.strip().split()[0] # بيشيل أي نص اضافي
    if not url.startswith("http"):
        return

    wait = bot.send_message(m.chat.id, "⚡️ جاري التحميل...")

    try:
        # 1- اذا الر
