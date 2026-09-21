import os, glob, tempfile
import telebot
from telebot import types
import yt_dlp

TOKEN = os.getenv("TOKEN")
CHANNEL = "@BotKanal24"
bot = telebot.TeleBot(TOKEN)
temp_data = {}

def is_subscribed(uid):
    try:
        m = bot.get_chat_member(CHANNEL, uid)
        return m.status in ['member','administrator','creator']
    except: return False

@bot.message_handler(commands=['start'])
def start(msg):
    if not is_subscribed(msg.from_user.id):
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("اشترك بقناتنا", url=f"https://t.me/{CHANNEL.replace('@','')}"))
        mk.add(types.InlineKeyboardButton("تحققت ✅", callback_data="check"))
        bot.send_message(msg.chat.id, "لازم تشترك اول 👇", reply_markup=mk)
    else:
        bot.send_message(msg.chat.id, "ابعت رابط 📥")

@bot.callback_query_handler(func=lambda c: c.data=="check")
def check(c):
    if is_subscribed(c.from_user.id):
        bot.send_message(c.message.chat.id, "تم ✅ ابعت رابط")
    else:
        bot.answer_callback_query(c.id, "لسه ما اشتركت!", show_alert=True)

@bot.message_handler(func=lambda m: m.text and "http" in m.text)
def dl(msg):
    url = msg.text.strip()
    temp_data[msg.chat.id] = url
    w = bot.reply_to(msg, "⏳ جاري التحميل...")
    try:
        with tempfile.TemporaryDirectory() as tmp:
            opts = {
                "format": "best[ext=mp4]/best",
                "outtmpl": os.path.join(tmp, "video.%(ext)s"),
                "quiet": True,
            }
            with yt_dlp.YoutubeDL(opts) as y:
                y.download([url])
            files = glob.glob(os.path.join(tmp, "*"))
            if files:
                with open(files[0], "rb") as f:
                    bot.send_video(msg.chat.id, f)
            bot.delete_message(msg.chat.id, w.message_id)
    except Exception as e:
        print(e)
        bot.edit_message_text(f"❌ فشل: {e}", msg.chat.id, w.message_id)

bot.infinity_polling()
