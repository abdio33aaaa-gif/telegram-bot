import os, re, telebot, yt_dlp
from telebot import types

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

CHANNEL = "@BotKanal24"
CHANNEL_LINK = "https://t.me/BotKanal24"
user_urls = {}

def get_url(text):
    m = re.search(r'https?://\S+', text)
    return m.group(0) if m else None

def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        # اذا البوت مو أدمن بالقناة رح يرجع True مشان ما يعلق
        return True

def send_force_sub(chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 اشترك بقناتي أولاً", url=CHANNEL_LINK))
    markup.add(types.InlineKeyboardButton("✅ اشتركت - جرب مرة تانية", callback_data="check_sub"))
    bot.send_message(chat_id, f"⚠️ لازم تشترك بقناتنا أولاً مشان تقدر تحمل\n\nاشترك هون 👉 {CHANNEL_LINK}\nوبعدين ارجع اكتب /start", reply_markup=markup)

@bot.message_handler(commands=['start'])
def start(m):
    if not is_subscribed(m.from_user.id):
        send_force_sub(m.chat.id)
        return
    name = m.from_user.first_name
    txt = f"أهلين يا {name} 👋🔥\n\nأنا بوت التحميل السريع\n🎬 تيك توك بدون علامة\n📸 انستا - ريلز وستوري\n👍 فيسبوك\n\n1️⃣ ابعتلي رابط\n2️⃣ اختار فيديو ولا صوت"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 قناتنا الرسمية", url=CHANNEL_LINK))
    bot.send_message(m.chat.id, txt, reply_markup=markup)

@bot.message_handler(func=lambda m: True, content_types=['text'])
def ask_choice(m):
    if not is_subscribed(m.from_user.id):
        send_force_sub(m.chat.id)
        return
    url = get_url(m.text or "")
    if not url: return
    user_urls[m.chat.id] = url
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("🎬 فيديو", callback_data="video"), types.InlineKeyboardButton("🎵 موسيقى", callback_data="audio"))
    bot.reply_to(m, "شو بدك حملك ياه؟", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_all(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id

    if call.data == "check_sub":
        if is_subscribed(user_id):
            bot.edit_message_text("✅ تم الاشتراك، فيك تحمل هلق! ابعت الرابط", chat_id, call.message.message_id)
        else:
            bot.answer_callback_query(call.id, "❌ لسا ما اشتركت!")
        return

    if not is_subscribed(user_id):
        bot.answer_callback_query(call.id, "اشترك أولاً!")
        send_force_sub(chat_id)
        return

    url = user_urls.get(chat_id)
    if not url: return
    bot.edit_message_text("⏳ عم نزل...", chat_id, call.message.message_id)
    try:
        if call.data == "video":
            fname = f"/tmp/{chat_id}.mp4"
            opts = {'format': 'mp4/best','outtmpl': fname,'quiet': True,'noplaylist': True,'overwrites': True}
            with yt_dlp.YoutubeDL(opts) as ydl: ydl.extract_info(url, download=True)
            with open(fname,'rb') as f: bot.send_video(chat_id, f)
        else:
            fname = f"/tmp/{chat_id}.mp3"
            opts = {'format': 'bestaudio/best','outtmpl': f"/tmp/{chat_id}.%(ext)s",'quiet': True,'noplaylist': True,'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}],'overwrites': True}
            with yt_dlp.YoutubeDL(opts) as ydl: ydl.extract_info(url, download=True)
            with open(fname,'rb') as f: bot.send_audio(chat_id, f)
        if os.path.exists(fname): os.remove(fname)
        bot.delete_message(chat_id, call.message.message_id)
    except Exception as e:
        print(e)
        bot.edit_message_text("❌ خطأ بالرابط", chat_id, call.message.message_id)

bot.infinity_polling()
