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
    txt = f"""
أهلين يا {name} 👋🔥

أنا بوت التحميل السريع
🎬 تيك توك بدون علامة مائية
📸 انستا - ريلز وستوري  
👍 فيسبوك - فيديو بجودة عالية

شلون بتحمل؟
1️⃣ ابعتلي رابط الفيديو
2️⃣ اختار بدك ياه فيديو ولا أغنية
3️⃣ بحملك ياه فوراً

جرب هلق ابعتلي أي رابط!
"""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 اشترك بقناتي", url="https://t.me/BotKanal24"))
    bot.send_message(m.chat.id, txt, reply_markup=markup)

@bot.message_handler(func=lambda m: True, content_types=['text'])
def ask_choice(m):
    url = get_url(m.text or "")
    if not url:
        return
    if "tiktok.com" not in url and "instagram.com" not in url and "facebook.com" not in url and "fb.watch" not in url:
        return

    user_urls[m.chat.id] = url
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🎬 فيديو", callback_data="video"),
        types.InlineKeyboardButton("🎵 موسيقى", callback_data="audio")
    )
    bot.reply_to(m, "شو بدك حملك ياه؟", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_choice(call):
    chat_id = call.message.chat.id
    url = user_urls.get(chat_id)
    if not url:
        bot.answer_callback_query(call.id, "ابعت الرابط مرة تانية")
        return

    bot.edit_message_text("⏳ عم نزل...", chat_id, call.message.message_id)
    
    try:
        if call.data == "video":
            fname = f"/tmp/{chat_id}.mp4"
            opts = {'format': 'mp4/best', 'outtmpl': fname, 'quiet': True, 'noplaylist': True, 'overwrites': True, 'http_headers': {'User-Agent': 'Mozilla/5.0'}}
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.extract_info(url, download=True)
            with open(fname, 'rb') as f:
                bot.send_video(chat_id, f, caption="✅ تفضل\n@MyDownload2026_bot")
        else:
            fname = f"/tmp/{chat_id}.mp3"
            opts = {'format': 'bestaudio/best', 'outtmpl': f"/tmp/{chat_id}.%(ext)s", 'quiet': True, 'noplaylist': True, 'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}], 'overwrites': True}
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.extract_info(url, download=True)
            with open(fname, 'rb') as f:
                bot.send_audio(chat_id, f, caption="✅ تفضل الصوت\n@MyDownload2026_bot")

        if os.path.exists(fname):
            os.remove(fname)
        bot.delete_message(chat_id, call.message.message_id)
        bot.answer_callback_query(call.id, "تم ✅")
    except Exception as e:
        print(e)
        bot.edit_message_text("❌ ما قدرت حملو، جرب رابط تاني", chat_id, call.message.message_id)

print("Bot started...")
bot.infinity_polling()
