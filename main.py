import os, re, telebot, yt_dlp
from telebot import types

BOT_TOKEN = os.getenv("BOT_TOKEN", "8977024211:AAG3OD86xIdCl7t13Oalk_Fy7X8xG1ZAOJs")
bot = telebot.TeleBot(BOT_TOKEN)
user_links = {}

def clean_url(text):
    m = re.search(r'https?://\S+', text)
    if not m: return None
    # خلي كامل الرابط لان تيك توك بيحتاج الباراميتر
    return m.group(0)

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, f"أهلا {m.from_user.first_name} 👋\nابعث رابط تيك توك / انستا / فيسبوك")

@bot.message_handler(func=lambda m: True)
def handle(m):
    url = clean_url(m.text)
    if not url: return
    user_links[m.chat.id] = url
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("🎬 فيديو", callback_data="video"), types.InlineKeyboardButton("🎵 صوت", callback_data="audio"))
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
            opts = {'format': 'mp4/best', 'outtmpl': 'video.%(ext)s', 'quiet': True, 'noplaylist': True}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                if not os.path.exists(filename):
                    for f in os.listdir('.'):
                        if f.startswith('video.'): filename = f; break
            with open(filename, 'rb') as f: bot.send_video(chat_id, f)
            os.remove(filename)
        else:
            opts = {'format': 'bestaudio/best', 'outtmpl': 'audio.%(ext)s', 'quiet': True, 'noplaylist': True, 'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]}
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
    try:
        text = inline.query.strip()
        url = clean_url(text)
        if not url:
            res = types.InlineQueryResultArticle('1', 'الصق رابط تيك توك', types.InputTextMessageContent('ابعت رابط وانا بحملو\n@MyDownload2026_bot'), description='مثال: https://vm.tiktok.com/...')
            return bot.answer_inline_query(inline.id, [res], cache_time=1, is_personal=True)

        # نجيب الرابط المباشر بدون ما نحمل
        ydl_opts = {'quiet': True, 'skip_download': True, 'noplaylist': True, 'format': 'mp4/best'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info: info = info['entries'][0]
            video_url = info.get('url')
            thumb = info.get('thumbnail', '')

        if not video_url:
            raise Exception("No url")

        result = types.InlineQueryResultVideo(
            id="1",
            video_url=video_url,
            mime_type="video/mp4",
            thumbnail_url=thumb,
            title="🎬 كبوس هون لارسال الفيديو",
            description="بدون علامة مائية",
            caption="تم التحميل عبر @MyDownload2026_bot"
        )
        bot.answer_inline_query(inline.id, [result], cache_time=1, is_personal=True)

    except Exception as e:
        print(f"Inline Error: {e}")
        res = types.InlineQueryResultArticle('1', '❌ الرابط خاص او مو شغال', types.InputTextMessageContent('جرب رابط تاني عام\n@MyDownload2026_bot'), description='جرب رابط تاني')
        bot.answer_inline_query(inline.id, [res], cache_time=1, is_personal=True)

bot.infinity_polling()
