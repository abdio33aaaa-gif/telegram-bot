import os
import telebot
import yt_dlp

TOKEN = "8977024211:AAG3OD86xIdCl7t13Oalk_Fy7X8xG1ZAOJs"

bot = telebot.TeleBot(TOKEN)

# إيقاف أي جلسة أو ويب هوك قديم لمنع حدوث خطأ التعارض 409
try:
    bot.remove_webhook()
except Exception:
    pass

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "مرحباً بك في بوت التحميل السريع! 🤖\n"
        "أرسل لي رابطاً من (تيك توك، انستا، يوتيوب، فيسبوك) وسأقوم بتحميله لك بثانية 👇"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_links(message):
    url = message.text.strip()
    
    if "http://" in url or "https://" in url:
        msg = bot.reply_to(message, "جاري معالجة الرابط وتحميل الفيديو، لطفاً انتظر قليلاً... ⏳")
        
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': 'downloaded_video.%(ext)s',
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
            
            with open(filename, 'rb') as video:
                bot.send_video(message.chat.id, video, reply_to_message_id=message.message_id)
            
            bot.delete_message(message.chat.id, msg.message_id)
            
            if os.path.exists(filename):
                os.remove(filename)

        except Exception as e:
            bot.edit_message_text("عذراً، حدث خطأ أثناء تحميل الفيديو. تأكد من أن الرابط عام وصحيح.", message.chat.id, msg.message_id)
            if 'filename' in locals() and os.path.exists(filename):
                os.remove(filename)
    else:
        bot.reply_to(message, "يرجى إرسال رابط صالح من إحدى المنصات المدعومة.")

if __name__ == "__main__":
    print("البوت يعمل الآن...")
    bot.infinity_polling(skip_pending=True)
