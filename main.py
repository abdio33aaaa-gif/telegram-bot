import telebot
import threading

TOKEN1 = "8977024211:AAG3OD86xIdCl7t13Oalk_Fy7X8xG1ZAOJs"
TOKEN2 = "8911586038:AAEJPLNv8dVdgKZL0n0qhqEMxvC9h_BeUp0"

bot1 = telebot.TeleBot(TOKEN1)
bot2 = telebot.TeleBot(TOKEN2)

@bot1.message_handler(commands=['start'])
def start1(m):
    bot1.reply_to(m, "اهلا! ابعت رابط للتحميل")

@bot2.message_handler(commands=['start'])
def start2(m):
    bot2.reply_to(m, "اهلا! ابعت رابط للتحميل")

@bot1.message_handler(func=lambda m: True)
def handle1(m):
    # هون حط كود التحميل تبعك القديم
    bot1.reply_to(m, f"تم: {m.text}")

@bot2.message_handler(func=lambda m: True)
def handle2(m):
    bot2.reply_to(m, f"تم: {m.text}")

def run_bot1():
    print("Bot1 @MyDownload2026_bot running")
    bot1.infinity_polling()

def run_bot2():
    print("Bot2 @Storiesa6d_bot running")
    bot2.infinity_polling()

threading.Thread(target=run_bot1).start()
threading.Thread(target=run_bot2).start()
