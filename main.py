import telebot

# ضع هنا توكن البوت الخاص بك
TOKEN = "8977024211:AAG3OD86xIdCl7t13Oalk_Fy7X8xG1ZAOJs"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "مرحباً بك في بوت التحميل السريع! 🤖\n"
        "أرسل لي رابطاً من (تيك توك، انستا، يوتيوب، فيسبوك) وسأقوم بتحميله لك بثانية 👇"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_links(message):
    user_message = message.text
    if "http://" in user_message or "https://" in user_message:
        bot.reply_to(message, "جاري معالجة الرابط وتحميل الفيديو، لطفاً انتظر قليلاً... ⏳")
    else:
        bot.reply_to(message, "يرجى إرسال رابط صالح من إحدى المنصات المدعومة.")

if __name__ == "__main__":
    print("البوت يعمل الآن...")
    bot.infinity_polling()
