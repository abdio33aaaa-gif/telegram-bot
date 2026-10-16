import os, threading, requests, tempfile
import telebot
from flask import Flask

# يقرا التوكن من Render Environment
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    print("ERROR: BOT_TOKEN not found!")
    exit(1)

print(f"Token OK, len={len(TOKEN)}")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Live - @MyDownload2026_bot"

def get_video(url):
    print(f"Get: {url}")
    # 1- Cobalt يدعم يوتيوب / تيك توك / فيس / انستا
    try:
        r = requests.post("https://api.cobalt.tools/api/json",
            json={"url": url, "vQuality": "720"},
            headers={'Accept':'application/json','Content-Type':'application/json'},
            timeout=25).json()
        print(f"Cobalt: {r}")
        if r.get("url"):
            return r["url"]
    except Exception as e:
        print(f"Cobalt fail: {e}")

    # 2- احتياط للتيك توك vm.tiktok
    try:
        r = requests.get(f"https://api.tiklydown.eu.org/api/download?url={url}",
            headers={'User-Agent':'Mozilla/5.0'}, timeout=20).json()
        print(f"tiklydown: {str(r)[:200]}")
        if r.get("video"):
            return r["video"].get("noWatermark") or r["video"].get("watermark")
    except Exception as e:
        print(f"tiklydown fail: {e}")

    return None

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id,
        "🚀 رجعنا!\n\nيدعم:\n• YouTube\n• TikTok حتى vm.tiktok\n• Facebook\n• Instagram\n\nدز الرابط")

@bot.message_handler(func=lambda m: True)
def handle(m):
    txt = m.text.strip().split()[0]
    if not txt.startswith("http"):
        return
    wait = bot.send_message(m.chat.id, "⚡️ ثواني...")
    try:
        direct = get_video(txt)
        if not direct:
            raise Exception("ما قدرت اجيب الفيديو")

        print(f"Downloading file...")
        r = requests.get(direct, stream=True, timeout=60,
            headers={'User-Agent':'Mozilla/5.0','Referer':'https://www.tiktok.com/'})
        r.raise_for_status()

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        for c in r.iter_content(1024*1024):
            if c: tmp.write(c)
        tmp.close()

        with open(tmp.name, 'rb') as f:
            bot.send_video(m.chat.id, f, caption="✅ @MyDownload2026_bot")
        os.remove(tmp.name)
        bot.delete_message(m.chat.id, wait.message_id)
        print("Sent OK")

    except Exception as e:
        print(f"FAIL: {e}")
        bot.edit_message_text(f"❌ {e}", m.chat.id, wait.message_id)

def run_bot():
    print("Starting polling...")
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Polling error: {e}")
            continue

def run_web():
    port = int(os.getenv("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    run_web()
