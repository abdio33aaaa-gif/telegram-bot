import os, threading, requests, re
import telebot
from flask import Flask

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Working - vm.tiktok fix"

def get_tiktok_video(url):
    """يجرب 3 مواقع لحد ما واحد يشتغل - بيحل vm.tiktok مباشرة"""

    # 1- جرب tikwm - بيحل الروابط القصيرة مباشرة بدون ما نحلها نحن
    try:
        r = requests.get(f"https://www.tikwm.com/api/?url={url}",
                        headers={'User-Agent':'Mozilla/5.0'}, timeout=15).json()
        if r.get('code') == 0:
            data = r['data']
            video = data.get('hdplay') or data.get('play') or data.get('wmplay')
            if video:
                return video
    except Exception as e:
        print(f"tikwm fail: {e}")

    # 2- جرب tikmate
    try:
        r = requests.get(f"https://tikmate.app/api/look?q={url}",
                        headers={'User-Agent':'Mozilla/5.0'}, timeout=15).json()
        if r.get('success'):
            return f"https://tikmate.app{r.get('token')}{r.get('id')}.mp4"
    except Exception as e:
        print(f"tikmate fail: {e}")

    # 3- جرب ssstik
    try:
        # جيب التوكن
        session = requests.Session()
        page = session.get("https://ssstik.io/en", headers={'User-Agent':'Mozilla/5.0'}, timeout=15).text
        m = re.search(r"s_tt\s*=\s*'([^']+)'", page)
        if m:
            tt = m.group(1)
            res = session.post("https://ssstik.io/abc?url=dl", data={'id':url,'locale':'en','tt':tt},
                               headers={'User-Agent':'Mozilla/5.0'}, timeout=15).text
            m2 = re.search(r'href="([^"]+)"[^>]*>Without watermark', res)
            if not m2:
                m2 = re.search(r'<a[^>]+href="([^"]+)"[^>]*download', res)
            if m2:
                return m2.group(1)
    except Exception as e:
        print(f"ssstik fail: {e}")

    return None

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id,
        "🚀 أهلا بك في بوت التحميل السريع!\n\n"
        "📥 TikTok - Instagram - Facebook\n"
        "أرسل رابط عام\n\n"
        "@MyDownload2026_bot")

@bot.message_handler(func=lambda m: True)
def handle(m):
    url = m.text.strip().split()[0]
    if not url.startswith("http"):
        return

    wait = bot.send_message(m.chat.id, "⚡️ ثواني... عم حل الرابط")

    try:
        video_url = None
        if "tiktok.com" in url:
            video_url = get_tiktok_video(url)
        else:
            # انستا وفيسبوك
            import yt_dlp
            opts = {'format':'best','quiet':True,'no_warnings':True,'noplaylist':True}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_url = info.get('url') or (info['formats'][-1]['url'] if info.get('formats') else None)

        if video_url:
            bot.send_video(m.chat.id, video_url, caption="✅ بدون علامة\n@MyDownload2026_bot")
            bot.delete_message(m.chat.id, wait.message_id)
        else:
            raise Exception("No video")

    except Exception as e:
        print(f"Error final: {e}")
        bot.edit_message_text(
            "❌ ما قدرت حل الرابط\n"
            "• الرابط عام مو خاص\n"
            "• جرب رابط طويل من مشاركة > نسخ الرابط",
            m.chat.id, wait.message_id)

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
