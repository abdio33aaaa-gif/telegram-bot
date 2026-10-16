import os, threading, requests, tempfile, re, urllib.parse
import telebot
from flask import Flask

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Live - Final Fix"

def get_tiktok_final(vm_url):
    print(f"Trying: {vm_url}")

    # 1- نحاول نحل vm.tiktok عن طريق proxy تاني كلياً - مو من Render
    # نستخدم tdown worker يلي شغال على Cloudflare وما بينحظر
    workers = [
        f"https://tdownv4.sl-bjs.workers.dev/?down={urllib.parse.quote(vm_url)}",
        f"https://tikwm.com/api/?url={urllib.parse.quote(vm_url)}&hd=1",
    ]

    for w_url in workers:
        try:
            print(f"Trying worker: {w_url[:50]}")
            r = requests.get(w_url, headers={'User-Agent':'Mozilla/5.0'}, timeout=30).json()
            print(f"Worker response: {str(r)[:300]}")
            # tdownv4 بيرجع download_url
            if r.get("download_url"):
                return r["download_url"]
            # tikwm بيرجع data.play
            if r.get("code") == 0 and r.get("data"):
                return r["data"].get("hdplay") or r["data"].get("play")
            if r.get("data") and isinstance(r["data"], dict):
                # بعض النسخ
                return r["data"].get("play")
        except Exception as e:
            print(f"Worker fail {w_url[:20]}: {e}")
            continue

    # 2- نجرب tikwm عن طريق corsproxy - يعني الطلب بيطلع من سيرفر تاني مو Render
    try:
        proxy_target = "https://www.tikwm.com/api/"
        cors_url = f"https://corsproxy.io/?{urllib.parse.quote(proxy_target)}"
        print(f"Trying corsproxy tikwm")
        r = requests.post(
            cors_url,
            data={"url": vm_url, "count": "12", "cursor": "0", "web": "1", "hd": "1"},
            headers={'User-Agent':'Mozilla/5.0'},
            timeout=30
        ).json()
        print(f"corsproxy response code: {r.get('code')}")
        if r.get("code") == 0:
            d = r.get("data", {})
            return d.get("hdplay") or d.get("play")
    except Exception as e:
        print(f"corsproxy fail: {e}")

    return None

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "🚀 ابعت رابط TikTok - حتى vm.tiktok هلا بيشتغل\n@MyDownload2026_bot")

@bot.message_handler(func=lambda m: True)
def handle(m):
    url = m.text.strip().split()[0]
    if not url.startswith("http"):
        return
    wait = bot.send_message(m.chat.id, "⚡️ ثواني... عم جيب الفيديو من سيرفر وسيط")

    try:
        direct = get_tiktok_final(url)
        if not direct:
            raise Exception("ما قدرت جيب الرابط - تيك توك حاظر Render")

        print(f"Downloading: {direct[:80]}")
        r = requests.get(direct, headers={'User-Agent':'Mozilla/5.0','Referer':'https://www.tiktok.com/'}, stream=True, timeout=80)
        r.raise_for_status()

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        for chunk in r.iter_content(chunk_size=1024*1024):
            if chunk:
                tmp.write(chunk)
        tmp.close()

        with open(tmp.name, 'rb') as f:
            bot.send_video(m.chat.id, f, caption="✅ تم التحميل\n@MyDownload2026_bot")

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
