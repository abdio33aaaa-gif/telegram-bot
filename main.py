import requests
import telebot

BOT_TOKEN = "حط_توكن_بوتك_هون"
bot = telebot.TeleBot(BOT_TOKEN)

def get_link(url):
    try:
        r = requests.post("https://api.cobalt.tools/api/json",
            json={"url": url},
            headers={"Accept": "application/json"}, timeout=20)
        return r.json().get('url')
    except:
        return None

# 1. الترحيب
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, 
        f"أهلا {message.from_user.first_name} 👋\n"
        "أرسل رابط انستا / تيك توك / فيس وانا بحملو بأعلى جودة ✨")

# 2. التحميل + الرسائل القديمة
@bot.message_handler(func=lambda m: "http" in m.text)
def download(message):
    msg = bot.reply_to(message, "⏳ جاري التحميل... انتظر ثواني")
    try:
        direct = get_link(message.text.strip())
        if direct:
            bot.edit_message_text("✅ تم التحميل، جاري الإرسال...", message.chat.id, msg.message_id)
            bot.send_document(message.chat.id, direct) # يبعتا كملف بجودة كاملة
        else:
            bot.edit_message_text("❌ الرابط خاص او فيه مشكلة، جرب رابط تاني", message.chat.id, msg.message_id)
    except:
        bot.edit_message_text("⚠️ صار خطأ، حاول مرة تانية", message.chat.id, msg.message_id)

bot.polling()
