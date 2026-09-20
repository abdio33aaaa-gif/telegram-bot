import os
import glob
import telebot
from telebot import types
import yt_dlp
import tempfile

TOKEN = os.getenv("TOKEN") or os.getenv("BOT_TOKEN") or os.getenv("BOT_TOK")
if not TOKEN:
    for k,v in os.environ.items():
        if "BOT" in k and ":" in str(v):
            TOKEN = v
            break
if not TOKEN:
    raise ValueError("TOKEN not found")

CHANNEL = "@BotKanal24"
bot = telebot.TeleBot(TOKEN.strip())
temp_data = {}

def is_subscribed(user_id):
    try:
        m = bot.get_chat_member(CHANNEL, user_id)
        return m.status in ['member', 'administrator', 'creator']
    except:
        return False

@bot.message_handler(commands=['start'])
def welcome(message):
    name = message.from_user.first_name
    if not is_subscribed(message.from_user.id):
        text = "🌟 اهلا " + name + " | الباشا 👑\n\n👑 بوت نزل الاسطوري\n🎬 تيك توك | 📸 انستا | 📘 فيسبوك | 🎥 يوتيوب\n\n🔒 يا " + name + " لازم تشترك بقناتنا اول 👇"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 اشترك بقناتنا", url="https://t.me/BotKanal24"))
        markup.add(types.InlineKeyboardButton("✅ تحققت", callback_data="check"))
        bot.send_message(message.chat.id, text, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "✅ اهلا " + name + " | الباشا\n📥 ابعت رابط الفيديو هلق")

@bot.callback_query_handler(func=lambda call: call.data == "check")
def check_sub(call):
    name = call.from_user.first_name
    if is_subscribed(call.from_user.id):
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        bot.send_message(call.message.chat.id, "✅ عاش يا " + name + "! تم التفعيل\n📥 ابعت رابط الفيديو هلق")
    else:
        bot.answer_callback_query(call.id, "❌ لسه ما اشتركت! اشترك اول", show_alert=True)

@bot.message_handler(func=lambda m: m.text and m.text.strip().startswith("http"))
def downloader(message):
    if not is_subscribed(message.from_user.id):
        welcome(message)
        return
    url = message.text.strip()
    wait = bot.reply_to(message, "🔍 جبت الفيديو")
    temp_data[message.chat.id] = url
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🎬 فيديو بدون علامة", callback_data="video"),
        types.InlineKeyboardButton("🎵 صوت MP3", callback_data="audio")
    )
    markup.add(
        types.InlineKeyboardButton("🖼️ صورة الغلاف", callback_data="thumb"),
        types.InlineKeyboardButton("❌ الغاء", callback_data="cancel")
    )
    bot.edit_message_text("✅ تم العثور على الفيديو\nشو بدك تحمل؟", message.chat.id, wait.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["video", "audio", "thumb", "cancel"])
def handle_choice(call):
    choice = call.data
    chat_id = call.message.chat.id
    if choice == "cancel":
        try:
            bot.delete_message(chat_id, call.message.message_id)
        except:
            pass
        return
    url = temp_data.get(chat_id)
    if not url:
        bot.answer_callback_query(call.id, "❌ ابعت الرابط مرة تانية")
        return
    bot.edit_message_text("⏳ جاري تحميل "
