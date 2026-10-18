import os
import requests
import yt_dlp
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "@BotKanal24"  # قناتك الرسمية
CHANNEL_LINK = "https://t.me/BotKanal24"

app = Flask(__name__)
bot = telebot.TeleBot(BOT_TOKEN)

def resolve_url(url):
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, allow_redirects=True, timeout=10)
        return r.url
    except:
        return url

def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['creator', 'administrator', 'member']
    except:
        return False  # اذا البوت مو ادمن بالقناة رح يرجع False

@bot.message_handler(commands=['start'])
def start(message):
    if not is_subscribed(message.from_user.id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📢 اشترك بالقناة الرسمية", url=CHANNEL_LINK))
        markup.add(InlineKeyboardButton("✅ تحققت، اشتركت", callback_data="check_sub"))
        bot.send_message(message.chat.id, 
            "يا هلا! 🔥\n\nلازم تشترك بقناتنا @BotKanal24 أول شي مشان يشتغل البوت معك:",
            reply_markup=markup)
        return

    text = "اهلا بيك بـ بوت التحميل السريع\n\nيحمل بجودة HD - بدون علامة مائية\nتيك توك | انستا | يوتيوب | فيسبوك\n\nبس ابعت الرابط وانا بجيبو بثانية"
    bot.send_message(message.chat.id, text)

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_sub_callback(call):
    if is_subscribed(call.from_user.id):
        bot.answer_callback_query(call.id, "تم الاشتراك بنجاح ✅")
        bot.send_message(call.message.chat.id, "تمام اشتركت! هلا ابعت الرابط وبحملو فوراً 🚀")
    else:
        bot.answer_callback_query(call.id, "لسا ما اشتركت 😅", show_alert=True)

@bot.message_handler(func=lambda m: True)
def handle(message):
    # تشييك الاشتراك قبل التحميل
    if not is_subscribed(message.from_user.id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📢 اشترك بالقناة", url=CHANNEL_LINK))
        bot.send_message(message.chat.id, "❗️ لازم تشترك أولاً @BotKanal24", reply_markup=markup)
        return

    url = message.text.strip()
    if not url.startswith("http"):
        return
    url = resolve_url(url)
    wait = bot.reply_to(message, "عم حمل...")
    try:
        ydl_opts = {'format': 'best', 'outtmpl': '%(id)s.%(ext)s', 'quiet': True, 'http_headers': {'User-Agent': 'Mozilla/5.0'}}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file = ydl.prepare_filename(info)
        with open(file, 'rb') as f:
            bot.send_video(message.chat.id, f)
        os.remove(file)
        bot.delete_message(message.chat.id, wait.message_id)
    except Exception as e:
        bot.edit_message_text("فشل: " + str(e), message.chat.id, wait.message_id)

@app.route(f"/{BOT_TOKEN}", methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "ok"

@app.route("/")
def home():
    return "Bot is running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
