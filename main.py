import telebot

# توكن البوت الاساسي - حطيت توكنك يلي بالصورة ولازم تحطو كامل
TOKEN = "8911586038:AAEJPLNv8dVdgKZL0XXXXXXXXXX"  # كمل باقي التوكن هون
CHANNEL = "@BotKanal24"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['nshr'])
def nshr_command(m):
    try:
        text = """📢 اعلان هام لاعضاء مجتمعنا الكرام

يسرنا ان نعلن انضمام بوت جديد لمساعدة البوت الاساسي 🤖

البوت المساعد الجديد: @Storiesa6d_bot
🔗 https://t.me/Storiesa6d_bot

البوت الاساسي: @MyDownload2026_bot
🔗 https://t.me/MyDownload2026_bot

الآن التحميل صار اسرع واقوى!
اذا كان البوت الاساسي مشغول، البوت الجديد جاهز يساعدكم فورا.

✅ نفس الميزات - نفس السرعة - نفس الجودة
📥 تيك توك - انستا - فيسبوك - يوتيوب

جربوا البوت الجديد الآن 👇
https://t.me/Storiesa6d_bot

مع تحيات المطور
السيد عبد الملك 💙
"""
        bot.send_message(CHANNEL, text)
        bot.reply_to(m, "✅
