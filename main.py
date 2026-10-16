import os, threading, requests, tempfile
import telebot
from flask import Flask

TOKEN = os.getenv("BOT_TOKEN")
# حط رابط الـ Worker يلي اخدتو من Cloudflare هون
WORKER_URL = os.getenv("WORKER_URL", "https://tiktok-proxy.YOURNAME.workers.dev")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Live via Cloudflare Worker"

def get_tiktok(vm_url):
    try:
        # الطلب بيروح Render -> Cloudflare Worker -> TikTok (مو محظور)
        print(f"Calling worker: {WORKER_URL} with {vm_url}")
        r = requests.get(f"{WORKER_URL}?url={vm_url}", timeout=30).json()
        print(f"Worker response code: {r.get('code')}")
        if r.get("code") == 0:
            d = r.get("data", {})
            return d.get("hdplay") or d.get("play")
    except Exception as e:
        print(f"Worker fail: {e}")
    return None

@bot.message_handler(func=lambda m: True)
def handle(m):
    url = m.text.strip().split()[0]
    if not url.startswith("http"):
        return
    wait = bot.send_message(m.chat.id, "⚡️ عم حمل...")

    try:
        direct = get_tiktok(url)
        if not direct:
            raise Exception("Worker ما رجع رابط")

        r = requests.get(direct, headers={'User-Agent':'Mozilla/5.0','Referer':'https://www.tiktok.com/'}, stream=True, timeout=60)
        r.raise_for_status()
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        for chunk in r.iter_content(1024*1024):
            if chunk: tmp.write(chunk)
        tmp.close()

        with open(tmp.name, 'rb') as f:
            bot.send_video(m.chat.id, f, caption="✅ @MyDownload2026_bot")
        os.remove(tmp.name)
        bot.delete_message(m.chat.id, wait.message_id)
    except Exception as e:
        print(e)
        bot.edit_message_text(f"❌ {e}", m.chat.id, wait.message_id)

@bot.message_handler(commands=['start'])
def start(m): bot.send_message(m.chat.id, "🚀 ابعت رابط TikTok vm.tiktok بيشتغل هلا")

def run_bot():
    while True:
        try: bot.infinity_polling(timeout=90, long_polling_timeout=90)
        except: continue
def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    run_web()
