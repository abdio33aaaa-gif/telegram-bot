import telebot
from telebot import types
import os
import yt_dlp

TOKEN = os.getenv("TOKEN")
CHANNEL = "@BotKanal24"
CHANNEL_LINK = "https://t.me/BotKanal24"

bot = telebot.TeleBot(TOKEN)

# ترحيب قصير ما بطفش
WELCOME = """أهلاً 😍

ابعت رابط وخلّي الباقي عليي 🚀
تيك توك - انستا - فيسبوك - يوتيوب
بدون علامة مائية ✨
"""

def is_subscribed(user_id):
    try:
        m = bot.get_chat_member(CHANNEL, user_id)
        return m.status in ['member','administrator','creator']
    except:
        return True

@bot.message_handler(command
