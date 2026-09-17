import telebot
from telebot import types
import threading

TOKEN1 = "8977024211:AAG3OD86xIdCl7t13Oalk_Fy7X8xG1ZAOJs"
TOKEN2 = "8911586038:AAEJPLNv8dVdgKZL0n0qhqEMxvC9h_BeUp0"
CHANNEL = "@BotKanal24"
CHANNEL_LINK = "https://t.me/BotKanal24"

user_links = {}

def channel_markup():
    m = types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton("📢 قناتنا الرسمية - انضم الآن", url=CHANNEL_LINK))
    return m

def is_subscribed(bot, user_id):
    try:
        member = bot.get_chat_member(CHANNEL, user_id)
        return member.status in ['member','administrator','creator']
    except:
        return False

def create_bot(TOKEN):
    bot = telebot.TeleBot(TOKEN)

    @bot.message_handler(commands=['start'])
    def start(m):
        name = m.from_user.first_name
        welcome = f"""
🌟 أهلاً {name} 🌟
━━━━━━━━━━━━━━━
👑 بوت التحميل الأسطوري 👑
🎬 تيك توك | 📸 انستا | 📘 فيسبوك | 🎥 يوتيوب
━━━━━━━━━━━━━━━
⚠️ اشترك بالقناة أولاً
"""
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 اشترك بالقناة", url=CHANNEL_LINK))
        markup.add(types.InlineKeyboardButton("✅ تحققت", callback_data="check_sub"))
        markup.add(types.InlineKeyboardButton("
