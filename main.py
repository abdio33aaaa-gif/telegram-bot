# bot_fixed.py - جاهز لـ Render
import os, threading, requests, yt_dlp, re, telebot
from flask import Flask

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "OK"

def expand_tiktok(u):
    try:
        h = {'User-Agent':'Mozilla/5.0'}
        r = requests.Session().get(u, headers=h, allow_redirects=True, timeout=20)
        long = r.url
        if "vm.tiktok" in long:
            m = re.search(r'https://www.tiktok.com/@[^/]+/video/\d+', r.text)
            if m:
                return m.group(0)
        return long
    except:
        return u

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "🚀 أهلا بك في بوت التحميل السريع!\n📥 TikTok + Instagram + Facebook\nأرسل الرابط")

@bot.message_handler(func=lambda m: True)
def handle(m):
    url = m.text.strip().split()[0]
    if not url.startswith("http"):
        return
    w = bot.send_message(m.chat.id, "⚡️ جاري التحميل...")
    try:
        if "vm.tiktok.com" in url or "vt.tiktok.com" in url:
            url = expand_tiktok(url)
        opts = {'format':'best','quiet':True,'no_warnings':True,'noplaylist':True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            vurl = info.get('url')
            if not vurl and info.get('formats'):
                vurl = info['formats'][-1]['url']
            if vurl:
                bot.send_video(m.chat.id, vurl, caption="✅ @MyDownload2026_bot")
                bot.delete_message(m.chat.id, w.message_id)
                return
        raise Exception("no url")
    except Exception as e:
        print(e)
        bot.edit_message_text("❌ ما قدرت حل الرابط - جرب رابط طويل", m.chat.id, w.message_id)

def run_bot():
    while True:
        try:
            bot.infinity_polling(timeout=90, long_polling_timeout=90)
        except:
            continue

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    run_web()
