import os, requests, yt_dlp, telebot
from flask import Flask

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = os.getenv("CHANNEL") # اذا عندك قناة اشتراك اجباري
app = Flask(__name__)
bot = telebot.TeleBot(BOT_TOKEN)

def resolve_url(url):
    # هذا يفك رابط vm.tiktok القصير
    try:
        r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, allow_redirects=True, timeout=10)
        return r.url
    except:
        return url

def is_subscribed(user_id):
    if not CHANNEL: return True
    try:
        member = bot.get_chat_member(CHANNEL, user_id)
        return member.status in ['member','administrator','creator']
    except: return True

@bot.message_handler(commands=['start'])
def start(message):
    text = """أهلاً بيك بـ بوت التحميل السريع ⚡️

🚀 يحمل بجودة HD - بدون علامة مائية
📥 تيك توك | انستا ستوري | يوتيوب | فيسبوك

بس ابعت الرابط وانا بجيبو بثانية 👇"""
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: True)
def handle(message):
    url = message.text.strip()
    if not url.startswith("http"): return
    url = resolve_url(url)
    
    wait = bot.reply_to(message, "⏳ عم حمل...")
    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': '%(id)s.%(ext)s',
            'quiet': True,
            'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file = ydl.prepare_filename(info)
        
        with open(file, 'rb') as f:
            bot.send_video(message.chat.id, f, caption="✅ تفضل - بدون علامة مائية")
        os.remove(file)
        bot.delete_message(message.chat.id, wait.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ فشل، جرب رابط تاني\n{e}",
