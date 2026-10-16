import os, threading, requests, tempfile, re
import telebot
from flask import Flask

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Live - TikTok Fixed Final"

def get_tiktok(url):
    print(f"=== Trying URL: {url} ===")
    # API 1 - tiklydown مجاني ويحل vm.tiktok لحاله
    try:
        api_url = f"https://api.tiklydown.eu.org/api/download?url={url}"
        print(f"Calling {api_url}")
        r = requests.get(api_url, headers={'User-Agent':'Mozilla/5.0'}, timeout=20).json()
        print(f"Response: {str(r)[:300]}")
        if r.get("video"):
            v = r["video"].get("noWatermark") or r["video"].get("watermark")
            if v:
                print(f"FOUND video via tiklydown")
                return v
    except Exception as e:
        print(f"tiklydown error: {e}")

    # API 2 - tikwm مباشر (يشتغل ببعض IPs)
    try:
        print("Trying tikwm direct")
        r = requests.post("https://www.tikwm.com/api/",
            data={"url": url, "count": "12", "cursor": "0", "web": "1", "hd": "1"},
            headers={'User-Agent':'Mozilla/5.0'}, timeout=20).json()
        print(f"tikwm code: {r.get('code')}")
        if r.get("code") == 0:
            d = r.get("data", {})
            v = d.get("hdplay") or d.get("play")
            if v:
                print(f"FOUND via tikwm")
                return v
    except Exception as e:
        print(f"tikwm error: {e}")

    return None

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "🚀 ارسل رابط TikTok - vm.tiktok يشتغل\n@MyDownload2026_bot")

@bot.message_handler(func=lambda m: True)
def handle(m):
    text = m.text.strip().split()[0]
    if not text.startswith("http"):
        return
    print(f"Received from {m.chat.id}: {text}")
    wait = bot.send_message(m.chat.id, "⚡️ ثواني...")

    try:
        direct = get_tiktok(text)
        if not direct:
            raise Exception("ما قدرت اجيب الفيديو - جرب رابط طويل")

        print(f"Downloading video file...")
        r = requests.get(direct, headers={'User-Agent':'Mozilla/5.0','Referer':'https://www.tiktok.com/'}, stream=True, timeout=60)
        r.raise_for_status()

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        for chunk in r.iter_content(chunk_size=1024*1024):
            if chunk:
                tmp.write(chunk)
        tmp.close()
        print(f"File saved {tmp.name}, sending to Telegram")

        with open(tmp.name, 'rb') as f:
            bot.send_video(m.chat.id, f, caption="✅ بدون علامة\n@MyDownload2026_bot")

        os.remove(tmp.name)
        bot.delete_message(m.chat.id, wait.message_id)
        print("Done success")

    except Exception as e:
        print(f"FINAL FAIL: {e}")
        bot.edit_message_text(f"❌ فشل: {e}\nجرب انسخ الرابط الطويل من TikTok", m.chat.id, wait.message_id)

def run_bot():
    print("Starting bot polling...")
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Polling error {e}")
            continue

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    run_web()
