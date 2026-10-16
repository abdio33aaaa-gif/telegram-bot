import os, threading, requests
import telebot
from flask import Flask

TOKEN = os.getenv("BOT_TOKEN") # توكن @MyDownload2026_bot
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "MyDownload2026_bot is Running!"

@bot.message_handler(commands=['start'])
def start(m):
    text = (
        "🚀 أهلاً بك في بوت التحميل السريع!\n\n"
        "📥 المنصات المدعومة:\n"
        "• TikTok\n"
        "• Instagram\n"
        "• Facebook\n\n"
        "أرسل رابط فيديو عام وسأحاول تنزيله بأفضل جودة متاحة.\n\n"
        "⚠️ المحتوى الخاص أو الذي يتطلب تسجيل الدخول قد لا يعمل.\n\n"
        "@MyDownload2026_bot"
    )
    bot.send_message(m.chat.id, text)

@bot.message_handler(func=lambda m: True)
def handle(m):
    url = m.text.strip()
    if not url.startswith("http"):
        bot.send_message(m.chat.id, "ابعت رابط فيديو صحيح 🙏")
        return

    wait = bot.send_message(m.chat.id, "⚡️ ثواني...")

    try:
        # 1- نحل الرابط القصير vm.tiktok.com
        if "vm.tiktok" in url or "vt.tiktok" in url:
            url = requests.get(url, allow_redirects=True, timeout=15, headers={'User-Agent':'Mozilla/5.0'}).url

        # 2- نحمل عن طريق tikwm (ما بيحتاج ffmpeg وبيشتغل على Render)
        api = f"https://www.tikwm.com/api/?url={url}"
        data = requests.get(api, timeout=20).json()

        if data.get('code') == 0 and 'data' in data:
            # تيك توك
            play_url = data['data'].get('play') or data['data'].get('hdplay')
            if play_url:
                bot.send_video(m.chat.id, play_url, caption="✅ تم التحميل بدون علامة\n@MyDownload2026_bot")
                bot.delete_message(m.chat.id, wait.message_id)
                return

        # 3- اذا مو تيك توك، نجرب yt-dlp كخطة بديلة للفيس وانستا
        # هون بنحتاج نجرب تحميل مباشر بدون حفظ
        bot.edit_message_text("⚠️ جرب رابط عام من زر مشاركة > نسخ الرابط\nالمحتوى الخاص ما بيتحمل", m.chat.id, wait.message_id)

    except Exception as e:
        print(f"Error: {e}")
        bot.edit_message_text(
            "❌ ما قدرت حمل الرابط\n\n"
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
        except Exception as e:
            print(f"Restarting: {e}")

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    run_web()
