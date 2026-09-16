import os, re, telebot, yt_dlp
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent

# رح يقرأ التوكن من المتغيرات، اذا ما لقى بياخد يلي تحت
BOT_TOKEN = os.getenv("BOT_TOKEN", "8977024211:AAG3OD86xIdCl7t13Oalk_Fy7X8xG1ZAOJs")
bot = telebot.TeleBot(BOT_TOKEN)
user_links = {}

def clean_url(text):
    m = re.search(r'https?://\S+', text)
    if not m: return None
    return m.group(0).split('?')[0]

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, f"أهلا {m.from_user.first_name} 👋\nابعث رابط تيك توك / انستا / فيسبوك")

@bot.message_handler(func=lambda m: True)
def handle(m):
    url = clean_url(m.text)
    if not url: return
    user_links[m.chat.id] = url
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("🎬 فيديو", callback_data="video"), InlineKeyboardButton("🎵 صوت", callback_data="audio"))
    bot.reply_to(m, f"شو بدك تنزل؟\n{url}", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id
    url = user_links.get(chat_id)
    if not url: return bot.answer_callback_query(call.id, "ابعث الرابط مرة تانية")
    choice = call.data
    bot.edit_message_text(f"⏳ جاري تحميل {choice}...", chat_id, call.message.message_id)
    try:
        if choice == "video":
            opts = {'format': 'mp4/best', 'outtmpl': 'video.%(ext)s', 'quiet': True}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                if not os.path.exists(filename):
                    for f in os.listdir('.'):
                        if f.startswith('video.'): filename = f; break
            with open(filename, 'rb') as f: bot.send_video(chat_id, f)
            os.remove(filename)
        else:
            opts = {'format': 'bestaudio/best', 'outtmpl': 'audio.%(ext)s', 'quiet': True, 'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]}
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.extract_info(url, download=True)
                filename = "audio.mp3"
                if not os.path.exists(filename):
                    for f in os.listdir('.'):
                        if f.startswith('audio.'): filename = f; break
            with open(filename, 'rb') as f: bot.send_audio(chat_id, f)
            os.remove(filename)
        bot.delete_message(chat_id, call.message.message_id)
    except Exception as e:
        print(e)
        bot.send_message(chat_id, "❌ خطأ، الرابط خاص")

@bot.inline_handler(lambda query: True)
def inline_query(inline):
    text = inline.query.strip()
    url = clean_url(text)
    if not url:
        res = InlineQueryResultArticle('1', 'حل من تيك توك', InputTextMessageContent('ابعت رابط وانا بحملو'), description='الصق الرابط هنا')
        return bot.answer_inline_query(inline.id, [res], cache_time=1)
    results = [InlineQueryResultArticle('1', f'🎬 حمل فيديو', InputTextMessageContent(f'{url}'), description=url), InlineQueryResultArticle('2', f'🎵 حمل صوت', InputTextMessageContent(f'{url}'), description=url)]
    bot.answer_inline_query(inline.id, results, cache_time=1)

bot.infinity_polling()
