import telebot, threading, os, re, glob, shutil, json
from telebot import types
import yt_dlp
import instaloader

# حط التوكنات الجديدة بعد ما تعمل revoke
TOKEN1 = "TOKEN_JADID_1"
TOKEN2 = "TOKEN_JADID_2"
CHANNEL = "@BotKanal24"
CHANNEL_LINK = "https://t.me/BotKanal24"

user_links = {}
STATS_FILE = "sources.json"

def log_source(source):
    try:
        with open(STATS_FILE, "r") as f:
            data = json.load(f)
    except:
        data = {}
    data[source] = data.get(source, 0) + 1
    with open(STATS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_source(text):
    parts = text.split()
    if len(parts) > 1:
        return parts[1].lower()
    return "search_direct"

def is_subscribed(bot, uid):
    try:
        m = bot.get_chat_member(CHANNEL, uid)
        return m.status in ['member','administrator','creator']
    except:
        return False

def clean_tmp(fid):
    for f in glob.glob(f'/tmp/{fid}*'):
        try: os.remove(f)
        except: pass
    folder = f'/tmp/{fid}_post'
    if os.path.exists(folder):
        shutil.rmtree(folder, ignore_errors=True)

def create_bot(TOKEN):
    bot = telebot.TeleBot(TOKEN)

    @bot.message_handler(commands=['start'])
    def start(m):
        source = get_source(m.text)
        log_source(source)

        txt = f"""🌟 اهلا {m.from_user.first_name} 🌟
━━━━━━━━━━━━━━━
👑 بوت التحميل الاسطوري 👑
🎬 تيك توك | 📸 انستا | 📘 فيسبوك | 🎥 يوتيوب
💎
