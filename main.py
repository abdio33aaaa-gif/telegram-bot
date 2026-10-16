import os, threading, requests, tempfile
import telebot
from flask import Flask

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "OK"

def get_tiktok(url):
    # 1) API الجديد يلي بيحل vm.tiktok مباشرة - مجرب 2026
    try:
        r = requests.get(f"https://tdownv4.sl-bjs.workers.dev/?down={url}", timeout=25).json()
        print(f"tdown: {r}")
        if r.get("download_url"):
            return r["download_url"]
    except Exception as e:
        print(f"tdown fail {e}")

    # 2) tikwm بـ POST مو GET
    try:
        r = requests.post(
            "https://www.tikwm.com/api/",
            data={"url": url, "count": "12", "cursor": "0", "web": "1", "hd": "1"},
            headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/x-www-form-urlencoded"},
            timeout=25
        ).json()
        print(f"tikwm: {r}")
        if r.get("code") == 0:
            d = r.get("data", {})
            return d.get("hdplay") or d.get("play") or d.get("wmplay")
    except Exception as e:
        print(f"tikwm fail {e}")

    # 3) cobalt كاحتياط
    try:
        r = requests.post(
            "https://api.cobalt.tools/api/json",
            json={"url": url},
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            timeout=25
        ).json()
        print(f"cobalt: {r}")
        if r.get("status") in ["tunnel","redirect"]:
            return r.get("url")
        if r.get("picker"):
            return r["picker"][0]["url"]
    except Exception as e:
        print(f"cobalt fail {e}")

    return None

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "🚀 ابعت رابط TikTok حتى لو vm.tiktok ورح حملو\n@MyDownload2026_bot")

@bot.message_handler(func=lambda m: True)
def handle(m):
    url = m.text.strip().split()[0]
    if not url.startswith("http"):
        return
    wait = bot.send_message(m.chat.id, "⚡️ عم حل الرابط...")

    try:
        direct = get_tiktok(url)
        if not direct:
            raise Exception("No direct link from all APIs")

        # نحمل الفيديو كملف
        print(f"Downloading file: {direct}")
        resp = requests.get(direct, headers={'User-Agent':'Mozilla/5.0','Referer':'https://www.tiktok.com/'}, stream=True, timeout=60)
        resp.raise_for_status()

        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as f:
            for chunk in resp.iter_content(1024*1024):
                if chunk:
                    f.write(chunk)
            path = f.name

        with open(path, 'rb') as vf:
            bot.send_video(m.chat.id, vf, caption="✅ بدون علامة\n@MyDownload2026_bot")

        os.remove(path)
        bot.delete_message(m.chat.id, wait.message_id)

    except Exception as e:
        print(f"FINAL FAIL: {e}")
        bot.edit_message_text(f"❌ فشل: {e}", m.chat.id, wait.message_id)

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
