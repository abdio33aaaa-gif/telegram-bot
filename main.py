import os, re, telebot, yt_dlp
from telebot import types
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
user_urls = {}
def get_url(text):
    m = re.search(r'https?://\S+', text)
    return m.group(0) if m else None
@bot.message_handler(commands=['start'])
def start(m):
    name = m.from_user.first_name
    txt = f"أهلين يا {name} 👋🔥\n\nأنا بوت التحميل السريع\n🎬 تيك توك بدون علامة\n📸 انستا - ريلز وستوري\n👍 فيسبوك\n\n1️⃣ ابعتلي رابط\n2️⃣ اختار فيديو ولا صوت\n3️⃣ بحملك فوراً"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 اشترك بقناتي - BotKanal24", url="https://t.me/BotKanal24"))
    bot.send_message(m.chat.id, txt, reply_markup=markup)
@bot.message_handler(func=lambda m: True, content_types=['text'])
def ask_choice(m):
    url = get_url(m.text or "")
    if not url: return
    user_urls[m.chat.id] = url
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("🎬 فيديو", callback_data="video"), types.InlineKeyboardButton("🎵 موسيقى", callback_data="audio"))
    bot.reply_to(m, "شو بدك حملك ياه؟", reply_markup=markup)
@bot.callback_query_handler(func=lambda c: True)
def handle_choice(c):
    import os
    chat_id = c.message.chat.id
    url = user_urls.get(chat_id)
    if not url: return
    bot.edit_message_text("⏳ عم نزل...", chat_id, c.message.message_id)
    try:
        if c.data == "video":
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
        bot.delete_message(chat_id, c.message.message_id)
    except Exception as e:
        print(e)
        bot.edit_message_text("❌ خطأ بالرابط", chat_id, c.message.message_id)
bot.infinity_polling()
