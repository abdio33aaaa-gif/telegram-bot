import os, re, telebot, yt_dlp
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = "8977024211:AAG3OD86xIdCl7t13Oalk_Fy7X8xG1ZAOJs"
bot = telebot.TeleBot(BOT_TOKEN)
user_links = {}

def clean_url(text):
    m = re.search(r'https?://\S+', text)
    if not m: return None
    url = m.group(0).strip()
    # نشيل?is=?si=?stkn=?igsh= تلقائيا بدون ما نعطي خطأ
    url = url.split('?')[0]
    url = url.split('&')[0]
    return url

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, f"أهلا {m.from_user.first_name} 👋\nابعث اي رابط تيك توك، فيسبوك، انستا، يوتيوب")

@bot.message_handler(func=lambda m: True)
def handle(m):
    url = clean_url(m.text)
    if not url: return
    user_links[m.chat.id] = url
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🎬 فيديو", callback_data="video"),
        InlineKeyboardButton("🎵 صوت", callback_data="audio")
    )
    bot.reply_to(m, f"تم لقيت الرابط ✅\n{url}\n\nشو بدك تنزل؟", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id
    url = user_links.get(chat_id)
    choice = call.data
    bot.edit_message_text(f"⏳ جاري تحميل الـ {choice} ثواني...", chat_id, call.message.message_id)
    filename = None
    try:
        if choice == "video":
            ydl_opts = {'format': 'mp4/best/best', 'outtmpl': 'video_%(id)s.%(ext)s', 'quiet': True, 'noplaylist': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                if not os.path.exists(filename):
                    for f in os.listdir('.'):
                        if f.startswith('video_'): filename = f; break
            with open(filename, 'rb') as f:
                bot.send_video(chat_id, f, caption="✅ تفضل\n@BotKanal24")
        else:
            # صوت بدون ffmpeg مشان ما يفشل بـ Railway
            ydl_opts = {'format': 'bestaudio/best', 'outtmpl': 'audio_%(id)s.%(ext)s', 'quiet': True, 'noplaylist': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                if not os.path.exists(filename):
                    for f in os.listdir('.'):
                        if f.startswith('audio_'): filename = f; break
            with open(filename, 'rb') as f:
                bot.send_audio(chat_id, f, caption="✅ تفضل الصوت\n@BotKanal24")

        if filename and os.path.exists(filename): os.remove(filename)
        bot.delete_message(chat_id, call.message.message_id)

    except Exception as e:
        print("ERROR:", e)
        bot.send_message(chat_id, f"❌ ما قدرت حمل هاد الرابط\nجرب رابط تاني عام\nالسبب: {e}")
        if filename and os.path.exists(filename):
            try: os.remove(filename)
            except: pass

bot.infinity_polling()
