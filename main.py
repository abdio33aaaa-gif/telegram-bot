import os, telebot
from telebot import types
import yt_dlp

TOKEN = os.getenv("TOKEN")
CHANNEL = "@BotKanal24"
CHANNEL_LINK = "https://t.me/BotKanal24"
bot = telebot.TeleBot(TOKEN)

WELCOME = "اهلا 😍\n\nابعت رابط وخلّي الباقي عليي 🚀\nتيك توك - انستا - فيسبوك - يوتيوب"

def is_subscribed(uid):
    try:
        m = bot.get_chat_member(CHANNEL, uid)
        return m.status in ['member','administrator','creator']
    except:
        return True

@bot.message_handler(commands=['start'])
def start(m):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("📢 قناتنا", url=CHANNEL_LINK))
    bot.send_message(m.chat.id, WELCOME, reply_markup=kb)

@bot.message_handler(func=lambda m: True)
def handle(m):
    url = m.text.strip()
    if "http" not in url:
        return
    if not is_subscribed(m.from_user.id):
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("📢 اشترك", url=CHANNEL_LINK))
        kb.add(types.InlineKeyboardButton("✅ تحققت", callback_data="check"))
        bot.reply_to(m, f"اشترك ثانية بس 👇\n{CHANNEL_LINK}", reply_markup=kb)
        return

    stat = bot.reply_to(m, "⏳ عم حملو... لا تغادر")
    path = f"/tmp/{m.from_user.id}.mp4"

    # اعدادات جديدة بتحل مشكلة يوتيوب
    opts = {
        'outtmpl': path,
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'quiet': True,
       
