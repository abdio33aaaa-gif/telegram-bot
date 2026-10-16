import os, threading, requests, tempfile
import telebot
from flask import Flask

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Live - Free Fix"

def get_video_free(vm_url):
    print(f"Trying {vm_url}")
    # هذا API مجاني 100% ويحل vm.tiktok لحاله
    try:
        r = requests.get(f"https://api.tiklydown.eu.org/api/download?url={vm_url}",
                         headers={'User-Agent':'Mozilla/5.0'}, timeout=25).json()
        print(f"tiklydown response: {str(r)[:250]}")
        if r.get("video"):
            video = r["video"].get("noWatermark") or r["video"].get("watermark")
            if video:
                return video
    except Exception as e:
        print(f"tiklydown fail: {e}")

    # احتياط اذا فشل الأول
    try:
        r = requests.post("https://tikdown.org/api/ajaxSearch",
            data={"q": vm_url, "lang": "en"},
            headers={'User-Agent':'Mozilla/5.0','Content-Type':'application/x-www-form-urlencoded'},
            timeout=25).json()
        # يرجع html فيه رابط
        import re
        m = re.search(r'href="([^"]+\.mp4[^"]*)"', r.get("data",""))
        if m:
            return m.group(1)
    except Exception as e:
        print(f"tikdown fail: {e}")

    return None

@bot.message_handler(func=lambda m: True)
def handle(m):
    url = m.text.strip().split()[0]
    if not url.startswith("http"): return
    wait = bot.send_message(m.chat.id, "⚡️ ثواني...")
    try:
        direct = get_video_free(url)
        if not direct:
            raise Exception("ما لقيت الفيديو")
        print(f"Downloading {direct[:60]}")
        r = requests.get(direct, headers={'User-Agent':'Mozilla/5.0'}, stream=True, timeout=60)
        r.raise_for_status()
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        for c in r.iter_content(1024*1024):
            if c: tmp.write(c)
        tmp.close()
        with open(tmp.name, 'rb') as f:
            bot.send_video(m.chat.id, f, caption="✅ مجاني - @MyDownload2026_bot")
        os.remove(tmp.name)
        bot.delete_message(m.chat.id, wait.message_id)
    except Exception as e:
        print(e)
        bot.edit_message_text(f"❌ {e}", m.chat.id, wait.message_id)

@bot.message_handler(commands=['start'])
def start(m): bot.send_message(m.chat.id, "🚀 شغال مجاني - دز رابط TikTok")

def run_bot():
    while True:
        try: bot.infinity_polling()
        except: continue
def run_web():
    app.run(host='0.0.0.0', port=int(os.getenv("PORT",10000)))

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    run_web()
