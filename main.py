import telebot
from telebot import types
import yt_dlp

TOKEN = "حط توكن بوتك هون من BotFather"
CHANNEL = "@قناتك" # حط معرف قناتك بدون https

bot = telebot.TeleBot(TOKEN)

# رسالة الترحيب - نفس يلي بالصورة
WELCOME_TEXT = """🌟 اهلا ALBASHA | البَاشَا | ALBASHA {name} 🌟

👑 بوت التحميل الاسطوري 👑
🎬 تيك توك | 📸 انستا | 📘 فيسبوك | 🎥 يوتيوب
📥 ابعت الرابط وسيب الباقي علينا"""

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("📢 اشترك بقناتنا", url=f"https://t.me/{CHANNEL.replace('@','')}")
    btn2 = types.InlineKeyboardButton("✅ تحققت", callback_data="check")
    markup.add(btn1, btn2)
    
    bot.send_message(message.chat.id, WELCOME_TEXT.format(name=message.from_user.first_name), reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check")
def check_sub(call):
    try:
        check = bot.get_chat_member(CHANNEL, call.from_user.id)
        if check.status in ['member','administrator','creator']:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, "✅ تم التحقق بنجاح!\n\n📩 ابعت الرابط الآن!")
        else:
            bot.answer_callback_query(call.id, "❌ لسه ما اشتركت بالقناة!", show_alert=True)
    except:
        bot.send_message(call.message.chat.id, "✅ تم! ابعت الرابط الآن")

# التحميل من الروابط
@bot.message_handler(func=lambda m: True)
def download(message):
    url = message.text
    if "http" not in url:
        return bot.reply_to(message, "❌ ابعت رابط صحيح!")
    
    msg = bot.reply_to(message, "⏳ جاري التحميل...")
    
    try:
        ydl_opts = {'outtmpl': '%(title)s.%(ext)s', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file = ydl.prepare_filename(info)
        
        with open(file, 'rb') as f:
            if file.endswith('.mp3'):
                bot.send_audio(message.chat.id, f)
            else:
                bot.send_video(message.chat.id, f, caption="✅ تم التحميل بواسطة @MyDownload2026_bot")
        bot.delete_message(message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ خطأ: {e}", message.chat.id, msg.message_id)

bot.infinity_polling()
