import os, re, telebot, yt_dlp
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = "8977024211:AAG3OD86xIdCl7t13Oalk_Fy7X8xG1ZAOJs"
bot = telebot.TeleBot(BOT_TOKEN)

# نحفظ رابط كل مستخدم مؤقتا
user_links = {}

def clean_url(text):
    m = re.search(r'https?://\S+', text)
    if not m: return None
    url = m.group(0)
    url = url.split('?')[0]
    return url

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, f"أهلا {m.from_user.first_name} 👋\nابعث رابط عام وانا بخيرك فيديو ولا صوت.")

@bot.message_handler(func=lambda m: True)
def handle(m):
    url = clean_url(m.text)
    if not url: return

    user_links[m.chat.id] = url

    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🎬 فيديو", callback_data="video"),
        InlineKeyboardButton("🎵 صوت فقط", callback_data="audio")
    )
    bot.reply_to(m, f"شو بدك تنزل من هاد الرابط؟\n{url}", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id
    url = user_links.get(chat_id)
    if not url:
        return bot.answer_callback_query(call.id, "الرابط انتهى، ابعثو مرة تانية")

    choice = call.data
    bot.edit_message_text(f"⏳ جاري تحميل الـ {choice}...", chat_id, call.message.message_id)

    try:
        if choice == "video":
            ydl_opts = {'format': 'mp4/best', 'outtmpl': 'video.%(ext)s', 'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                # لاقي الملف
                if not os.path.exists(filename):
                    for f in os.listdir('.'):
                        if f.startswith('video.'): filename = f; break

            with open(filename, 'rb') as f:
                bot.send_video(chat_id, f, caption="✅ تفضل الفيديو\n@BotKanal24")
            os.remove(filename)

        else: # audio
            ydl_opts = {'format': 'bestaudio/best', 'outtmpl': 'audio.%(ext)s', 'quiet': True, 'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = "audio.mp3"
                if not os.path.exists(filename):
                    for f in os.listdir('.'):
                        if f.startswith('audio.'): filename = f; break

            with open(filename, 'rb') as f:
                bot.send_audio(chat_id, f, caption="✅ تفضل الصوت\n@BotKanal24")
            os.remove(filename)

        bot.delete_message(chat_id, call.message.message_id)

    except Exception as e:
        print(e)
        bot.send_message(chat_id, "❌ خطأ بالتحميل، تأكد الرابط عام بدون stkn")
        try: os.remove(filename)
        except: pass

bot.infinity_polling()
