import os
import telebot
from telebot import types
import yt_dlp

# يقرأ التوكن بأي اسم انت مسميه
TOKEN = os.getenv("TOKEN") or os.getenv("BOT_TOKEN") or os.getenv("BOT_T") or os.getenv("BOT_TOK")
# اذا الاسم مقصوص بالصورة، جيب الاسم الكامل:
# اضغط على 3 نقاط حد BOT_T... > Edit > انسخ الاسم الكامل وحطو هون
if not TOKEN:
    # محاولة اخيرة: دور على أي متغير فيه كلمة BOT
    for k,v in os.environ.items():
        if "BOT" in k and ":" in str(v):
            TOKEN = v
            break

CHANNEL = os.getenv("CHANNEL") or "@telegram"

if not TOKEN:
    raise ValueError("TOKEN not found! Rename variable to TOKEN")

bot = telebot.TeleBot(TOKEN.strip())

@bot.message_handler(commands=['start'])
def welcome(message):
    name = message.from_user.first_name
    text = f"""🌟 اهلا {name} 🌟

👑 بوت نزّل الاسطوري 👑
🎬 تيك توك | 📸 انستا | 📘 فيسبوك | 🎥 يوتيوب

📩 ابعت رابط الفيديو ورح حملك ياه بدون علامة مائية"""

    markup = types.InlineKeyboardMarkup(row_width=1)
    channel_url = f"https://t.me/{CHANNEL.replace('@','')}"
    btn1 = types.InlineKeyboardButton("📢 اشترك بقناتنا", url=channel_url)
    btn2 = types.InlineKeyboardButton("✅ تحققت", callback_data="check")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check")
def check(call):
    bot.send_message(call.message.chat.id, "✅ تم! ابعت الرابط الآن")

@bot.message_handler(func=lambda m: True)
def downloader(message):
    url = message.text.strip()
    if not url.startswith("http"): return
    wait = bot.reply_to(message, "⏳ جاري التحميل...")
    try:
        ydl_opts = {'format': 'best', 'outtmpl': 'video.%(ext)s', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        with open(filename, 'rb') as f:
            bot.send_video(message.chat.id, f)
        os.remove(filename)
        bot.delete_message(message.chat.id, wait.message_id)
    except Exception as e:
        bot.edit_message_text("❌ فشل، جرب رابط تاني", message.chat.id, wait.message_id)

bot.infinity_polling()
