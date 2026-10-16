import os, threading, requests
import telebot
from flask import Flask

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Working - vm fix"

def get_video_url(original_url):
    # الطريقة 1: Cobalt API - بتحل vm.tiktok وانستا وفيسبوك
    try:
        r = requests.post(
            "https://api.cobalt.tools/api/json",
            json={"url": original_url},
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            timeout=25
        ).json()
        if r.get("status") in ["tunnel", "redirect", "picker"]:
            # لو رجع picker بكون فيه عدة فيديوهات
            if r.get("picker"):
                return r["picker"][0]["url"]
            return r.get("url")
    except Exception as e:
        print(f"Cobalt fail: {e}")

    # الطريقة 2: TiklyDown - مخصصة لتيك توك وبتحل vm.tiktok مباشرة
    try:
        r = requests.get(
            f"https://tiklydown.eu.org/api/download?url={original_url}",
            timeout=20
        ).json()
        if r.get("video"):
            return r["video"].get("noWatermark") or r["video"].get("watermark")
    except Exception as e:
        print(f"TiklyDown fail: {e}")

    # الطريقة 3: tikwm - احتياط
    try:
        r = requests.get(
            f"https://www.tikwm.com/api/?url={original_url}",
            headers={'User-Agent':'Mozilla/5.0'},
            timeout=20
        ).json()
        if r.get("code") == 0:
            return r["data"].get("hdplay") or r["data"].get("play")
    except Exception as e:
        print(f"tikwm fail: {e}")

    return None

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id,
        "🚀 أهلا بك في بوت التحميل السريع!\n\n"
        "📥 المنصات المدعومة:\n"
        "• TikTok بدون علامة\n"
        "• Instagram ريلز وستوري\n"
        "• Facebook - YouTube\n\n"
        "أرسل رابط عام وهلا بحملو!\n\n"
        "@MyDownload2026_bot"
    )

@bot.message_handler(func=lambda m: True)
def handle(m):
    url = m.text.strip().split()[0]
    if not url.startswith("http"):
        return

    wait = bot.send_message(m.chat.id, "⚡️ ثواني عم حل الرابط...")

    try:
        video = get_video_url(url)
        if video:
            bot.send_video(m.chat.id, video, caption="✅ بدون علامة\n@MyDownload2026_bot")
            bot.delete_message(m.chat.id, wait.message_id)
        else:
            raise Exception("All APIs failed")

    except Exception as e:
        print(f"Final fail for {url}: {e}")
        bot.edit_message_text(
            "❌ ما قدرت حل الرابط\n"
            "جرب تبعت الرابط الطويل:\n"
            "تيك توك > مشاركة > نسخ الرابط",
            m.chat.id, wait.message_id
        )

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
