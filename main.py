import telebot, threading, os, re, glob, shutil, time
from telebot import types
import yt_dlp
import instaloader

TOKEN1 = os.getenv("BOT_TOKEN")
TOKEN2 = os.getenv("BOT_TOKEN2")

CHANNEL = "@BotKanal24"
CHANNEL_LINK = "https://t.me/BotKanal24"
user_links = {}

def is_subscribed(bot, uid):
    try:
        m = bot.get_chat_member(CHANNEL, uid)
        return m.status in ['member','administrator','creator']
    except:
        return False

def create_bot(TOKEN):
    bot = telebot.TeleBot(TOKEN)

    @bot.message_handler(commands=['start'])
    def start(m):
        txt = f"🌟 اهلا {m.from_user.first_name} | ALBASHA | الباشا 🌟\n━━━━━━━━━━━━━━━\n👑 بوت التحميل الاسطوري 👑\n🎬 تيك توك | 📸 انستا | 📘 فيسبوك | يوتيوب\n💎 بدون علامة مائية - جودة عالية"
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton('📢 اشترك بقناتنا', url=CHANNEL_LINK))
        kb.add(types.InlineKeyboardButton('✅ تحققت', callback_data='check_sub'))
        kb.add(types.InlineKeyboardButton('🔗 قناتنا الرسمية', url=CHANNEL_LINK))
        bot.send_message(m.chat.id, txt, reply_markup=kb)

    @bot.message_handler(func=lambda m: 'http' in m.text)
    def handle(m):
        if not is_subscribed(bot, m.from_user.id):
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton('📢 اشترك اولا', url=CHANNEL_LINK))
            kb.add(types.InlineKeyboardButton('✅ تحقق', callback_data='check_sub'))
            bot.reply_to(m, '❌ اشترك بالقناة اولا', reply_markup=kb)
            return
        user_links[m.from_user.id] = m.text.strip()
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(types.InlineKeyboardButton('فيديو 🎬', callback_data='video'), types.InlineKeyboardButton('صوت 🎵', callback_data='audio'))
        kb.add(types.InlineKeyboardButton('📸 صور', callback_data='photo'))
        bot.reply_to(m, '✅ اختر:', reply_markup=kb)

    @bot.callback_query_handler(func=lambda call: True)
    def cb(call):
        if call.data == 'check_sub':
            if is_subscribed(bot, call.from_user.id):
                bot.answer_callback_query(call.id, 'تم ✅')
                bot.send_message(call.message.chat.id, '✅ تمام! ابعت الرابط')
            else:
                bot.answer_callback_query(call.id, 'ما اشتركت ❌')
            return
        url = user_links.get(call.from_user.id)
        if not url: return
        fid = call.from_user.id
        try:
            if call.data == 'video':
                opts = {'outtmpl': f'/tmp/{fid}.mp4', 'format': 'best[ext=mp4]/best', 'quiet': True}
                with yt_dlp.YoutubeDL(opts) as ydl: ydl.download([url])
                bot.send_video(call.message.chat.id, open(f'/tmp/{fid}.mp4
