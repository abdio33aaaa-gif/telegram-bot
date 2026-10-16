import os, threading, requests, tempfile
import telebot
from flask import Flask

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Live - TikTok Fixed"

def get_video(url):
    # نحول vm.tiktok ل رابط طويل اول شي
    try:
        r = requests.get(url, headers={'User-Agent':'Mozilla/5.0'}, allow_redirects=True, timeout=15)
        long_url = r.url
        print(f"Resolved: {url} -> {long_url}")
    except:
        long_url = url

    # API الوحيد يلي شغال على Render المجاني - tikwm
    try:
        resp = requests.post(
            "https://www.tikwm.com/api/",
            data={"url": long_url, "count": 12, "cursor": 0, "web": 1, "hd": 1},
            headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/x-www-form-urlencoded"},
            timeout=30
        ).json()
        print(f"tikwm response: {resp.get('code')}")
        if resp.get("code") == 0:
            data = resp.get("data", {})
            video_url = data.get("hdplay") or data.get("play") or data.get("wmplay")
            print(f"video_url found: {video_url[:50] if video_url else None}")
            return video_url
    except Exception as e:
        print(f"tikwm error: {e}")

    return None

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "🚀 ارسل رابط TikTok حتى لو vm.tiktok.com\nراح احملو مباشرة\n@MyDownload2026_bot")

@bot.message_handler(func=lambda m: True)
def handle(m):
    url = m.text.strip().split()[0]
    if not url.startswith("http"):
        return

    wait = bot.send_message(m.chat.id, "⚡️ ثواني... عم حل الرابط القصير")

    try:
        direct = get_video(url)
        if not direct:
            raise Exception("ما لقيت رابط الفيديو - جرب رابط طويل")

        # نحمل الفيديو كملف - هاد اهم شي
        print(f"Downloading file...")
        r = requests.get(direct, headers={'User-Agent':'Mozilla/5.0','Referer':'https://www.tiktok.com/'}, stream=True, timeout=60)
        r.raise_for_status()

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        for chunk in r.iter_content(chunk_size=1024*1024):
            if chunk:
                tmp.write(chunk)
        tmp.close()

        with open(tmp.name, 'rb') as f:
            bot.send_video(m.chat.id, f, caption="✅ بدون علامة\n@MyDownload2026_bot")

        os.remove(tmp.name)
        bot.delete_message(m.chat.id, wait.message_id)

    except Exception as e:
        print(f"FINAL ERROR: {e}")
        bot.edit_message_text(f"❌ {e}\nجرب: TikTok > مشاركة > نسخ الرابط (الطويل)", m.chat.id, wait.message_id)

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
