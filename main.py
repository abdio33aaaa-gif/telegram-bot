import telebot
from telebot import types
import os
import yt_dlp

TOKEN = os.getenv("TOKEN")
CHANNEL = "@BotKanal24"
CHANNEL_LINK = "https://t.me/BotKanal24"

bot = telebot.TeleBot(TOKEN)

WELCOME = "اهلا 😍\n\nابعت رابط وخلّي الباقي عليي 🚀\nتيك توك - انستا - فيسبوك - يوتيوب\nبدون علامة مائية ✨"

def is_subscribed(user_id):
    try:
        m = bot.get_chat_member(CHANNEL, user_id)
        return m.status in ['member','administrator','creator']
    except:
        return True

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 قناتنا", url=CHANNEL_LINK))
    bot.send_message(message.chat.id, WELCOME, reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle(message):
    url = message.text.strip()
    if "http" not in url:
        bot.reply_to(message, "📥 ابعت رابط بس")
        return
    if not is_subscribed(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 اشترك بالقناة", url=CHANNEL_LINK))
        markup.add(types.InlineKeyboardButton("✅ تحققت", callback_data="check"))
        bot.reply_to(message, "اشترك ثانية وحدة بس 👇\n" + CHANNEL_LINK, reply_markup=markup)
        return
    status = bot.reply_to(message, "⏳ عم حملو...")
    path = f"/tmp/{message.from_user.id}.mp4"
    opts = {'outtmpl': path, 'format': 'best[ext=mp4]/best', 'quiet': True, 'noplaylist': True}
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 @BotKanal24", url=CHANNEL_LINK))
        with open(path, 'rb') as f:
            bot.send_video(message.chat.id, f, caption="تم ✅", reply_markup=markup)
        bot.delete_message(message.chat.id, status.message_id)
        if os.path.exists(path):
            os.remove(path)
    except:
        bot.edit_message_text("❌ ما قدرت حملو، تأكد الرابط عام", message.chat.id, status.message_id)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "check":
        if is_subscribed(call.from_user.id):
            bot.answer_callback_query(call.id, "تم ✅")
            bot.send_message(call.message.chat.id, "عاش! ابعت الرابط 🚀")
        else:
            bot.answer_callback_query(call.id, "لسه ما اشتركت ❌", show_alert=True)

bot.infinity_polling(skip_pending=True)
