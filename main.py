import os, threading, requests, tempfile, re
import telebot
from flask import Flask
import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Working - TikTok Fixed"

def resolve_vm(url):
    # نحول vm.tiktok.com ل رابط طويل
    try:
        r = requests.get(url, headers={'User-Agent':'Mozilla/5.0'}, allow_redirects=True, timeout=15)
        # الرابط النهائي بيكون فيه /video/
        final = r.url
        print(f"Resolved {url} -> {final}")
        return final
    except Exception as e:
        print(f"Resolve fail: {e}")
        return url

def get_tiktok_file(original_url):
    long_url = resolve_vm(original_url)

    # الطريقة 1: yt-dlp مع اعدادات جديدة لتجاوز بلوك تيك توك
    try:
        tmpdir = tempfile.mkdtemp()
        ydl_opts = {
            'outtmpl': f'{tmpdir}/%(id)s.%(ext)s',
            'format': 'mp4',
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'
            },
            'extractor_args': {
                'tiktok': {
                    'api_hostname': ['api16-normal-c-useast1a.tiktokv.com', 'api16-normal-c-useast2a.tiktokv.com'],
                    'app_version': ['30.9.1'],
                }
            }
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(long_url, download=True)
            filename = ydl.prepare_filename(info)
            print(f"yt-dlp success: {filename}")
            return filename
    except Exception as e:
        print(f"yt-dlp fail: {e}")

    # الطريقة 2: tikwm API بـ POST
    try:
        r = requests.post(
            "https://www.tikwm.com/api/",
            data={"url": long_url, "count":"12","cursor":"0","web":"1","hd":"1"},
            headers={"User-Agent":"Mozilla/5.0"},
            timeout=20
        ).json()
        if r.get("code")==0:
            play = r["data"].get("play") or r["data"].get("hdplay")
            if play:
                print(f"tikwm success: {play}")
                # نحمل الملف
                tmp = tempfile.mktemp(suffix='.mp4')
                data = requests.get(play, headers={'User-Agent':'Mozilla/5.0'}, timeout=30).content
                open(tmp,'wb').write(data)
                return tmp
    except Exception as e:
        print(f"tikwm fail: {e}")

    return None

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "🚀 بوت التيك توك شغال!\nابعت رابط حتى لو vm.tiktok\n@MyDownload2026_bot")

@bot.message_handler(func=lambda m: True)
def handle(m):
    url = m.text.strip().split()[0]
    if not url.startswith("http"):
        return
    wait = bot.send_message(m.chat.id, "⚡️ ثواني عم حل الرابط القصير...")

    try:
        filepath = get_tiktok_file(url)
        if not filepath or not os.path.exists(filepath):
            raise Exception("ما قدرت حمل الفيديو")

        with open(filepath, 'rb') as f:
            bot.send_video(m.chat.id, f, caption="✅ تم التحميل\n@MyDownload2026_bot")

        # تنظيف
        try:
            os.remove(filepath)
            os.rmdir(os.path.dirname(filepath))
        except:
            pass
        bot.delete_message(m.chat.id, wait.message_id)

    except Exception as e:
        print(f"FINAL: {e}")
        bot.edit_message_text(f"❌ فشل: {e}\nجرب رابط طويل: TikTok > مشاركة > نسخ الرابط", m.chat.id, wait.message_id)

def run_bot():
    while True:
        try:
            bot.infinity_polling(timeout=90, long_polling_timeout=90)
        except Exception as e:
            print(e)
            continue

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    run_web()
