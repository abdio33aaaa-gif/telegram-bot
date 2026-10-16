import os, threading, requests, tempfile, urllib.parse
import telebot
from flask import Flask

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Live - Final Fix"

def get_video_direct(vm_url):
    print(f"Original: {vm_url}")

    # نستخدم corsproxy.io حتى الطلب ما يطلع من Render
    # Render -> corsproxy.io -> tikwm.com -> TikTok
    try:
        target = "https://www.tikwm.com/api/"
        proxy_url = f"https://corsproxy.io/?{urllib.parse.quote(target)}"

        data = {
            "url": vm_url,
            "count": "12",
            "cursor": "0",
            "web": "1",
            "hd": "1"
        }

        r = requests.post(proxy_url, data=data, timeout=30, headers={'User-Agent':'Mozilla/5.0'})
        j = r.json()
        print(f"corsproxy tikwm code: {j.get('code')}")

        if j.get("code") == 0:
            d = j.get("data", {})
            video = d.get("hdplay") or d.get("play")
            if video:
                print(f"Found via corsproxy: {video[:50]}")
                return video
    except Exception as e:
        print(f"corsproxy fail: {e}")

    # احتياط 2: tiklydown API (هو سيرفره على Cloudflare مو محظور)
    try:
        r = requests.get(f"https://api.tiklydown.eu.org/api/download?url={vm_url}",
                         headers={'User-Agent':'Mozilla/5.0'}, timeout=20).json()
        print(f"tiklydown: {str(r)[:200]}")
        if r.get("video"):
            return r["video"].get("noWatermark") or r["video"].get("watermark")
    except Exception as e:
        print(f"tiklydown fail: {e}")

    return None

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "🚀 ارسل رابط TikTok - حتى vm.tiktok بيشتغل هلا\n@MyDownload2026_bot")

@bot.message_handler(func=lambda m: True)
def handle(m):
    url = m.text.strip().split()[0]
    if not url.startswith("http"):
        return
    wait = bot.send_message(m.chat.id, "⚡️ ثواني... عم حل الرابط")

    try:
        direct = get_video_direct(url)
        if not direct:
            raise Exception("ما قدرت جيب الفيديو - جرب رابط طويل")

        print(f"Downloading file...")
        r = requests.get(direct, headers={'User-Agent':'Mozilla/5.0','Referer':'https://www.tiktok.com/'}, stream=True, timeout=70)
        r.raise_for_status()

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        for chunk in r.iter_content(chunk_size=1024*1024):
            if chunk:
                tmp.write(chunk)
        tmp.close()

        with open(tmp.name, 'rb') as f:
            bot.send_video(m.chat.id, f, caption="✅ @MyDownload2026_bot")

        os.remove(tmp.name)
        bot.delete_message(m.chat.id, wait.message_id)

    except Exception as e:
        print(f"FINAL ERROR: {e}")
        bot.edit_message_text(f"❌ فشل: {e}", m.chat.id, wait.message_id)

def run_bot():
    while True:
        try:
            bot.infinity_polling(timeout=90, long_polling_timeout=90)
        except: continue

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    run_web()
