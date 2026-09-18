import telebot
from telebot import types
import yt_dlp
import os

TOKEN = "حط التوكن هون من BotFather"
CHANNEL = "@اسم_قناتك"  # مثلا @NazzilChannel

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def welcome(message):
    name = message.from_user.first_name
    text = f"""🌟 اهلا {name} 🌟

👑 بوت نزّل الاسطوري 👑
🎬 تيك توك | 📸 انستا | 📘 فيسبوك | 🎥 يوتيوب

📩 ابعت رابط الفيديو ورح حملك ياه بدون علامة مائية وبجودة عالية"""

    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("📢 اشترك بقناتنا", url=f"https://t.me/{CHANNEL.replace('@','')}")
    btn2 = types.InlineKeyboardButton("✅ تحققت", callback_data="check")
    markup.add(btn1, btn2)
    
    bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check")
def check(call):
    try:
        member = bot.get_chat_member(CHANNEL, call.from_user.id)
        if member.status in ['member','administrator','creator']:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, "✅ تم التحقق!\n\n📩 ابعت الرابط الآن")
        else:
            bot.answer_callback_query(call.id, "❌ لازم تشترك بالقناة أولاً", show_alert=True)
    except:
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
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        with open(filename, 'rb') as f:
            bot.send_video(message.chat.id, f, caption="✅ تم بواسطة @MyDownload2026_bot\n🔗 نزّل - بوت التحميل السريع")
        
        os.remove(filename)
        bot.delete_message(message.chat.id, wait.message_id)
        
    except Exception as e:
        bot.edit_message_text(f"❌ فشل التحميل، جرب رابط تاني\n{e}", message.chat.id, wait.message_id)

print("البوت شغال...")
bot.infinity_polling()
