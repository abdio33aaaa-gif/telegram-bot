import os, threading, requests, tempfile
import telebot
from flask import Flask

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Working"

def get_direct_link(original_url):
    # cobalt بيحل vm.tiktok مباشرة
    try:
        r = requests.post(
            "https://api.cobalt.tools/api/json",
            json={"url": original_url},
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            timeout=30
        ).json()
        print(f"Cobalt response: {r}")
        if r.get("status") in ["tunnel","redirect"]:
            return r.get("url")
        if r.get("picker"):
            return r["picker"][0]["url"]
    except Exception as e:
        print(f"Cobalt error: {e}")

    try:
        r = requests.get(f"https://tiklydown.eu.org/api/download?url={original_url}", timeout=20).json()
        if r.get("video"):
            return r["video"].get("noWatermark")
    except Exception as e:
        print(f"Tikly error: {e}")

    return None

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "🚀 ابعت رابط TikTok (حتى لو vm.tiktok) ورح حملو\n@MyDownload2026_bot")

@bot.message_handler(func=lambda m: True)
def handle(m):
    url = m.text.strip().split()[0]
    if not url.startswith("http"):
        return

    wait = bot.send_message(m.chat.id, "⚡️ عم حمل الفيديو... ثواني")

    try:
        direct_url = get_direct_link(url)
        if not direct_url:
            raise Exception("No direct link")

        # هون السر - نحمل الفيديو كملف على سيرفر Render
        print(f"Downloading: {direct_url}")
        video_data = requests.get(direct_url, headers={'User-Agent':'Mozilla/5.0'}, timeout=60, stream=True)

        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as f:
            for chunk in video_data.iter_content(chunk_size=8192):
                f.write(chunk)
            temp_path = f.name

        # نبعتو كملف
        with open(temp_path, 'rb') as video_file:
            bot.send_video(m.chat.id, video_file, caption="✅ بدون علامة\n@MyDownload2026_bot")

        os.remove(temp_path)
        bot.delete_message(m.chat.id, wait.message_id)

    except Exception as e:
        print(f"FINAL ERROR: {e}")
        try:
            bot.edit_message_text(f"❌ فشل: {e}\nجرب رابط طويل من تيك توك > مشاركة > نسخ الرابط", m.chat.id, wait.message_id)
        except:
            pass

def run_bot():
    while True:
        try:
            bot.infinity_polling(timeout=90, long_polling_timeout=90)
        except Exception as e:
            print(f"Restart bot: {e}")
            continue

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    run_web()
