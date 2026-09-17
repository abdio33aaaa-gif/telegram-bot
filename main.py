import telebot

TOKEN = "حط توكن البوت الاساسي هون"
CHANNEL = "@BotKanal24"  # قناتك
8911586038:AAEJPLNv8dVdgKZL0n0qhqEMxvC9h_BeUp0
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['nshr'])
def nshr_command(m):
    try:
        text = """📢 اعلان هام لأعضاء مجتمعنا الكرام

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
        bot.reply_to(m, "✅ تم النشر بقناة @BotKanal24 بنجاح")
    except Exception as e:
        bot.reply_to(m, f"❌ خطأ: {e}\nتأكد البوت ادمن بقناة @BotKanal24")

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "اكتب /nshr لنشر الاعلان")

print("Bot running for @BotKanal24")
bot.infinity_polling()
