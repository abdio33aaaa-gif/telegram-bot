import os, threading, requests, tempfile, re, urllib.parse
import telebot
from flask import Flask

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Live"

def resolve_vm_via_proxy(short_url):
    # نحل vm.tiktok عن طريق سيرفر وسيط مش محظور
    try:
        # الطريقة 1: allorigins proxy
        encoded = urllib.parse.quote(short_url, safe='')
        proxy_url = f"https://api.allorigins.win/raw?url={encoded}"
        r = requests.get(proxy_url, timeout=20, headers={'User-Agent':'Mozilla/5.0'})
        html = r.text
        # نطلع الرابط الطويل من الـ HTML
        match = re.search(r'https://www\.tiktok\.com/@[^/]+/video/\d+', html)
        if match:
            print(f"Proxy resolved: {match.group(0)}")
            return match.group(0)
        # جرب canonical
        match2 = re.search(r'"canonicalUrl":"([^"]+)"', html)
        if match2:
            return match2.group(1).replace('\\u002F','/')
    except Exception as e:
        print(f"Proxy resolve fail: {e}")

    # الطريقة 2: محاولة مباشرة (لو فك الحظر)
    try:
        r = requests.get(short_url, headers={'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)'}, allow_redirects=True, timeout=15)
        if "/video/" in r.url:
            return r.url
    except Exception as e:
        print(f"Direct resolve fail: {e}")

    return short_url

def get_video_url(original_url):
    long_url = resolve_vm_via_proxy(original_url)
    print(f"Final long url: {long_url}")

    # جرب 3 APIs مختلفة
    apis = [
        ("tikwm.com", f"https://www.tikwm.com/api/", {"url": long_url, "count": 12, "cursor": 0, "web": 1, "hd": 1}),
        ("tiklydown", f"https://api.tiklydown.eu.org/api/download?url={long_url}", None),
    ]

    for name, api_url, data in apis:
        try:
            if data:
                resp = requests.post(api_url, data=data, headers={'User-Agent':'Mozilla/5.0'}, timeout=30).json()
            else:
                resp = requests.get(api_url, headers={'User-Agent':'Mozilla/5.0'}, timeout=30).json()

            print(f"{name} response: {str(resp)[:200]}")

            if name == "tikwm.com" and resp.get("code") == 0:
                d = resp.get("data", {})
                video = d.get("hdplay") or d.get("play")
                if video:
                    return video

            if name == "tiklydown" and resp.get("video"):
                video = resp["video"].get("noWatermark") or resp["video"].get("watermark")
                if video:
                    return video

        except Exception as e:
            print(f"{name} fail: {e}")
            continue

    return None

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "🚀 ارسل رابط TikTok (vm.tiktok بيشتغل هلا)\n@MyDownload2026_bot")

@bot.message_handler(func=lambda m: True)
def handle(m):
    url = m.text.strip().split()[0]
    if not url.startswith("http"):
        return
    wait = bot.send_message(m.chat.id, "⚡️ ثواني... عم حل الرابط القصير عن طريق سيرفر وسيط")

    try:
        direct = get_video_url(url)
        if not direct:
            raise Exception("API ما رجع رابط - جرب رابط طويل من تيك توك")

        print(f"Downloading video: {direct[:60]}")
        r = requests.get(direct, headers={'User-Agent':'Mozilla/5.0','Referer':'https://www.tiktok.com/'}, stream=True, timeout=60)
        r.raise_for_status()

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        for chunk in r.iter_content(chunk_size=1024*1024):
            if chunk:
                tmp.write(chunk)
        tmp.close()

        with open(tmp.name, 'rb') as f:
            bot.send_video(m.chat.id, f, caption="✅ تم\n@MyDownload2026_bot")

        os.remove(tmp.name)
        bot.delete_message(m.chat.id, wait.message_id)

    except Exception as e:
        print(f"FINAL: {e}")
        bot.edit_message_text(f"❌ {e}", m.chat.id, wait.message_id)

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
