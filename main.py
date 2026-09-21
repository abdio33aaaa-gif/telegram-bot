import os
import telebot
from telebot import types
import yt_dlp
import glob

TOKEN = os.getenv("TOKEN")
CHANNEL = "@BotKanal24"
CHANNEL_LINK = "https://t.me/BotKanal24"

bot = telebot.TeleBot(TOKEN)

WELCOME = "اهلا 😍\nابعت رابط وخلّي الباقي عليي 🚀"

def is_subscribed(uid):
    try:
        m = bot.get_chat_member(CHANNEL, uid)
        return m.status in ['member','administrator','creator']
    except:
        return True

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, WELCOME)

@bot.message_handler(func=lambda m: True)
def handle(m):
    url = m.text.strip()
    if "http" not in url:
        return
    if not is_subscribed(m.from_user.id):
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("📢 اشترك", url=CHANNEL_LINK))
        kb.add(types.InlineKeyboardButton("✅ تحققت", callback_data="check"))
        bot.reply_to(m, "اشترك ثانية بس", reply_markup=kb)
        return

    s = bot.reply_to(m, "⏳ عم حملو...")
    for f in glob.glob(f"/tmp/{m.from_user.id}.*"):
        try:
            os.remove(f)
        except:
            pass

    opts = {
        "outtmpl": f"/tmp/{m.from_user.id}.%(ext)s",
        "format": "best[ext=mp4]/best",
        "quiet": True,
        "noplaylist": True,
    }

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        with open(filename, 'rb') as f:
            bot.send_video(m.chat.id, f, caption="تم ✅")

        bot.delete_message(m.chat.id, s.message_id)
        os.remove(filename)
    except Exception as e:
        bot.edit_message_text(f"خطأ: {e}", m.chat.id, s.message_id)

@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    if is_subscribed(c.from_user.id):
        bot.send_message(c.message.chat.id, "تم! ابعت الرابط هلق 🚀")
    else:
        bot.answer_callback_query(c.id, "لسه ما اشتركت ❌", show_alert=True)

bot.infinity_polling(skip_pending=True)
