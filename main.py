import os
import telebot
from telebot import types
import yt_dlp

# يقرأ من Variables في Railway - ما في داعي تكتب التوكن هون
TOKEN = os.getenv("TOKEN")
CHANNEL = os.getenv("CHANNEL") # مثلا @NazzilChannel

if not TOKEN:
    raise ValueError("TOKEN not found in Environment Variables!")

bot = telebot.TeleBot(TOKEN.strip()) # strip يشيل أي فراغ بالغلط

@bot.message_handler(commands=['start'])
def welcome(message):
    name = message.from_user.first_name
    text = f"""🌟 اهلا {name} 🌟

👑 بوت نزّل الاسطوري 👑
🎬 تيك توك | 📸 انستا | 📘 فيسبوك | 🎥 يوتيوب

📩 ابعت رابط الفيديو ورح حملك ياه بدون علامة مائية"""

    markup = types.InlineKeyboardMarkup(row_width=1)
    channel_url = f"https://t.me/{CHANNEL.replace('@','')}" if CHANNEL else "https://t.me/telegram"
    btn1 = types.InlineKeyboardButton("📢 اشترك بقناتنا", url=channel_url)
    btn2 = types.InlineKeyboardButton("✅ تحققت", callback_data="check")
    markup.add(btn1, btn2)
    
    bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check")
def check(call):
    try:
        if not CHANNEL:
            return bot.send_message(call.message.chat.id, "✅ تمام! ابعت الرابط الآن")
            
        member = bot.get_chat_member(CHANNEL, call.from_user.id)
        if member.status in ['member','administrator','creator']:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, "✅ تم التحقق!\n\n📩 ابعت الرابط الآن")
        else:
            bot.answer_callback_query(call.id, "❌ لازم تشترك بالقناة أولاً", show_alert=True)
    except Exception as e:
        print(f"Check error: {e}")
        bot.send_message(call.message.chat.id, "✅ تمام! ابعت الرابط الآن")

@bot.message_handler(func=lambda m: True)
def downloader(message):
    url = message.text.strip()
    if not url.startswith("http"):
        return
    
    wait = bot.reply_to(message, "⏳ جاري التحميل... لا تطلع")
    
    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'video.%(ext)s',
            'quiet': True,
            'noplaylist': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        with open(filename, 'rb') as f:
            bot.send_video(message.chat.id, f, caption="✅ تم بواسطة @MyDownload2026_bot")

        if os.path.exists(filename):
            os.remove(filename)
        bot.delete_message(message.chat.id, wait.message_id)
        
    except Exception as e:
        print(f"Download error: {e}")
        bot.edit_message_text(f"❌ فشل التحميل، جرب رابط تاني", message.chat.id, wait.message_id)

print("البوت شغال...")
bot.infinity_polling()
