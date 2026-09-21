import telebot
from telebot import types
import os
import yt_dlp

TOKEN = os.getenv("TOKEN")
CHANNEL = "@BotKanal24"
CHANNEL_LINK = "https://t.me/BotKanal24"

if not TOKEN:
    raise ValueError("TOKEN مو موجود بالـ Variables!")

bot = telebot.TeleBot(TOKEN)

WELCOME = """ماذا يمكن لهذا البوت فعله؟

🚀 بوت التحميل الخارق - أسرع بوت تحميل

تيك توك - انستغرام - فيسبوك - يوتيوب

ماذا أقدم لك؟ 👇
تيك توك بدون علامة مائية ✅
انستا ريلز وستوري بجودة عالية ✅
فيسبوك بضغطة واحدة ✅
يوتيوب فيديو MP4 وصوت MP3 ✅
سريع جداً ويعمل 24 ساعة ✅

طريقة الاستخدام:
انسخ رابط الفيديو وارسله هنا فقط!

القناة الرسمية: @BotKanal24 📢
المطور: السيد شيخ أحمد 👨‍💻
"""

def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return True # اذا البوت مو مشرف لا توقف الناس

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 اشترك بالقناة", url=CHANNEL_LINK))
    markup.add(types.InlineKeyboardButton("✅ تحققت من الاشتراك", callback_data="check_sub"))
    bot.send_message(message.chat.id, WELCOME, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_sub(call):
    if is_subscribed(call.from_user.id):
        bot.answer_callback_query(call.id, "تم الاشتراك ✅")
        bot.send_message(call.message.chat.id, "✅ تم يا بطل! ابعت رابط الفيسبوك هلق وجرب 👇")
    else:
        bot.answer_callback_query(call.id, "❌ لسه ما اشتركت بالقناة", show_alert=True)

@bot.message_handler(func=lambda m: True)
def download_handler(message):
    text = message.text.strip()

    if "http" not in text:
        bot.reply_to(message, "📥 ابعت رابط")
        return

    if not is_subscribed(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 اشترك بالقناة", url=CHANNEL_LINK))
        markup.add(types.InlineKeyboardButton("✅ تحققت", callback_data="check_sub"))
        bot.reply_to(message, f"❌ يجب الاشتراك بالقناة اولاً\n{CHANNEL_LINK}", reply_markup=markup)
        return

    # رسالة التحميل
    msg = bot.reply_to(message, "⏳ جاري تحميل فيديو الفيسبوك... لا تغادر")

    file_path = f"/tmp/{message.from_user.id}.mp4"

    # اعدادات خاصة للفيسبوك
    ydl_opts = {
        'outtmpl': file_path,
        'format': 'best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([text])

        # زر القناة تحت كل فيديو
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 القناة الرسمية: @BotKanal24", url=CHANNEL_LINK))

        with open(file_path, 'rb') as video:
            bot.send_video(message.chat.id, video, caption="✅ تم التحميل من فيسبوك - @BotKanal24", reply_markup=markup)

        bot.delete_message(message.chat.id, msg.message_id)

        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        bot.edit_message_text(f"❌ فشل التحميل: {e}\nتأكد انو الرابط عام مو خاص", message.chat.id, msg.message_id)

print("Bot is running...")
bot.infinity_polling(skip_pending=True)
