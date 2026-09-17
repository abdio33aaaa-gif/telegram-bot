import telebot

TOKEN = "8911586038:AAEJPLNv8dVdgKZL0XXXXXXXXXX"  # كمل توكنك هون
CHANNEL = "@BotKanal24"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['nshr'])
def nshr_command(m):
    try:
        text = """📢 اعلان هام

البوت المساعد الجديد: @Storiesa6d_bot
https://t.me/Storiesa6d_bot

البوت الاساسي: @MyDownload2026_bot
https://t.me/MyDownload2026_bot

التحميل صار اسرع!
تيك توك - انستا - فيسبوك - يوتيوب

جربوه الآن
https://t.me/Storiesa6d_bot
"""
        bot.send_message(CHANNEL, text)
        bot.reply_to(m, "تم النشر")
    except Exception as e:
        bot.reply_to(m, f"خطا: {e}")

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "اكتب /nshr")

print("Bot running")
bot.infinity_polling()
