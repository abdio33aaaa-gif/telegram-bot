import os, re, telebot, yt_dlp, time
from telebot import types

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TOKEN_HERE")
bot = telebot.TeleBot(BOT_TOKEN)
user_links = {}

def clean_url(text):
    m = re.search(r'https?://\S+', text)
    if not m: return None
    return m.group(0)

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, f"أهلا {m.from_user.first_name} 👋\nابعث رابط")

@bot.message_handler(func=lambda m: True)
def handle(m):
    url = clean_url(m.text)
    if not url: return
    user_links[m.chat.id] = url
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("🎬 فيديو", callback_data="video"))
    bot.reply_to(m, f"شو بدك تنزل؟\n{url}", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    # نفس كودك القديم بيشتغل
    chat_id = call.message.chat.id
    url = user_links.get(chat_id)
    try:
        opts = {'format': 'mp4/best', 'outtmpl': 'video.%(ext)s', 'quiet': True, 'noplaylist': True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if not os.path.exists(filename):
                for f in os.listdir('.'):
                    if f.startswith('video.'): filename = f; break
        with open(filename, 'rb') as f: bot.send_video(chat_id, f)
        os.remove(filename)
        bot.delete_message(chat_id, call.message.message_id)
    except Exception as e:
        print(e)
        bot.send_message(chat_id, "❌ خطأ")

@bot.inline_handler(lambda query: True)
def inline_query(inline):
    try:
        url = clean_url(inline.query.strip())
        if not url:
            res = types.InlineQueryResultArticle('1', 'الصق رابط تيك توك هنا', types.InputTextMessageContent('الصق الرابط\nمثال: https://vm.tiktok.com/ZGdQ5Ws1y/'), description='حمل بدون علامة')
            return bot.answer_inline_query(inline.id, [res], cache_time=1, is_personal=True)

        # 1. نزل الفيديو على سيرفر البوت
        fname = f"inline_{inline.from_user.id}.mp4"
        opts = {'format': 'mp4/best', 'outtmpl': fname, 'quiet': True, 'noplaylist': True, 'overwrites': True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.extract_info(url, download=True)

        if not os.path.exists(fname):
            for f in os.listdir('.'):
                if f.startswith(f"inline_{inline.from_user.id}"): fname = f; break

        # 2. ارفعو على تيليجرام مشان ناخد file_id
        with open(fname, 'rb') as f:
            msg = bot.send_video(inline.from_user.id, f, disable_notification=True)
            file_id = msg.video.file_id

        os.remove(fname)

        # 3. رجعو كفيديو جاهز للانلاين
        result = types.InlineQueryResultCachedVideo(
            id="1",
            video_file_id=file_id,
            title="✅ جاهز - كبوس لارسالو بالكروب",
            description="بدون علامة مائية",
            caption="تم التحميل عبر @MyDownload2026_bot"
        )
        bot.answer_inline_query(inline.id, [result], cache_time=1, is_personal=True)

    except Exception as e:
        print(f"Inline Error: {e}")
        # اذا المستخدم مو عامل start للبوت، ما بنقدر نبعتلو
        res = types.InlineQueryResultArticle('1', '⚠️ اول شي فوت على البوت واضغط /start', types.InputTextMessageContent(f'لازم تفوت على البوت اول شي وتكتب /start مشان اقدر ابعتلك الفيديو\n@MyDownload2026_bot'), description='اضغط هون')
        bot.answer_inline_query(inline.id, [res], cache_time=1, is_personal=True)

bot.infinity_polling()
