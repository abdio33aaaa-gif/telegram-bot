import os, threading, requests, yt_dlp
import telebot
from flask import Flask

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "MyDownload2026_bot Running!"

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id,
        "🚀 أهلاً بك في بوت التحميل السريع!\n\n"
        "📥 المنصات المدعومة:\n"
        "• TikTok\n• Instagram\n• Facebook\n\n"
        "أرسل رابط فيديو عام وسأحاول تنزيله بأفضل جودة متاحة.\n\n"
        "⚠️ المحتوى الخاص أو الذي يتطلب تسجيل الدخول قد لا يعمل.\n\n"
        "@MyDownload2026_bot"
    )

@bot.message_handler(func=lambda m: True)
def handle(m):
    url = m.text.strip()
    if not url.startswith("http"):
        return

    wait = bot.send_message(m.chat.id, "⚡️ جاري التحميل...")

    try:
        # 1- حل روابط vm.tiktok المختصرة
        if "vm.tiktok" in url or "vt.tiktok" in url:
            url = requests.get(url, allow_redirects=True, timeout=15, headers={'User-Agent':'Mozilla/5.0'}).url
            url = url.split("?")[0] # تنظيف الرابط

        # 2- محاولة تيك توك عن طريق tikwm (أسرع)
        if "tiktok.com" in url:
            api = f"https://www.tikwm.com/api/?url={url}"
            r = requests.get(api, timeout=15).json()
            if r.get('code') == 0:
                play = r['data'].get('play') or r['data'].get('hdplay')
                if play:
                    bot.send_video(m.chat.id, play, caption="✅ بدون علامة\n@MyDownload2026_bot")
                    bot.delete_message(m.chat.id, wait.message_id)
                    return

        # 3- انستا وفيسبوك وتيك توك كخطة بديلة عن طريق yt-dlp بدون تحميل ملف (مشان ما نحتاج ffmpeg)
        # هاد هو يلي كان ناقص وسبب الخطأ بالصورة
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'best',
            'noplaylist': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            # جيب رابط الفيديو المباشر
            direct_url = info.get('url')
            if not direct_url and 'entries' in info:
                direct_url = info['entries'][0].get('url')
            if not direct_url and 'formats' in info:
                direct_url = info['formats'][-1]['url']

            if direct_url:
                bot.send_video(m.chat.id, direct_url, caption="✅ تم التحميل\n@MyDownload2026_bot")
                bot.delete_message(m.chat.id, wait.message_id)
                return
            else:
                raise Exception("no direct url")

    except Exception as e:
        print(f"Error on {url}: {e}")
        bot.edit_message_text(
            "❌ ما قدرت حل الرابط\n\n"
            "تأكد انو:\n"
            "• الرابط عام مو خاص\n"
            "• نسختو من زر مشاركة > نسخ الرابط\n"
            "• جرب رابط طويل",
            m.chat.id, wait.message_id
        )

def run_bot():
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as ex:
            print(f"Crash: {ex}")

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    run_web()
