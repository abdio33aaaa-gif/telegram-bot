import os
import telebot
from telebot import types
import yt_dlp
import tempfile

TOKEN = os.getenv("TOKEN") or os.getenv("BOT_TOKEN") or os.getenv("BOT_T") or os.getenv("BOT_TOK")
if not TOKEN:
    for k,v in os.environ.items():
        if "BOT" in k and ":" in str(v):
            TOKEN = v
            break

CHANNEL = os.getenv("CHANNEL") or "@BotKanal24"
if not TOKEN:
    raise ValueError("TOKEN not found!")

bot = telebot.TeleBot(TOKEN.strip())

# نخزن معلومات الفيديو مؤقتا
temp_data = {}

@bot.message_handler(commands=['start'])
def welcome(message):
    name = message.from_user.first_name
    text = f"""🌟 اهلا {name} 🌟

👑 بوت نزّل الاسطوري 👑
🎬 تيك توك | 📸 انستا | 📘 فيسبوك | 🎥 يوتيوب

📩 ابعت رابط الفيديو ورح خيرك شو بدك تحمل"""

    markup = types.InlineKeyboardMarkup(row_width=1)
    channel_url = f"https://t.me/{CHANNEL.replace('@','')}"
    btn1 = types.InlineKeyboardButton("📢 اشترك بقناتنا", url=channel_url)
    btn2 = types.InlineKeyboardButton("✅ تحققت", callback_data="check")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check")
def check(call):
    bot.send_message(call.message.chat.id, "✅ تم! ابعت الرابط الآن")

@bot.message_handler(func=lambda m: True)
def downloader(message):
    url = message.text.strip()
    if not url.startswith("http"):
        return

    wait = bot.reply_to(message, "🔍 جبت الفيديو، شو بدك تحمل؟")

    # نحفظ الرابط ونعطي خيارات
    temp_data[message.chat.id] = url

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🎬 فيديو بدون علامة", callback_data="video"),
        types.InlineKeyboardButton("🎵 صوت MP3", callback_data="audio")
    )
    markup.add(
        types.InlineKeyboardButton("🖼️ صورة الغلاف", callback_data="thumb"),
        types.InlineKeyboardButton("❌ الغاء", callback_data="cancel")
    )

    bot.edit_message_text("✅ تم العثور على الفيديو\nشو بدك تحمل؟", message.chat.id, wait.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_choice(call):
    choice = call.data
    chat_id = call.message.chat.id

    if choice == "cancel":
        bot.delete_message(chat_id, call.message.message_id)
        return

    url = temp_data.get(chat_id)
    if not url:
        bot.answer_callback_query(call.id, "❌ ابعت الرابط مرة تانية")
        return

    bot.edit_message_text(f"⏳ جاري تحميل {choice}...", chat_id, call.message.message_id)

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            if choice == "video":
                ydl_opts = {'format': 'best', 'outtmpl': f'{tmpdir}/video.%(ext)s', 'quiet': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                with open(filename, 'rb') as f:
                    bot.send_video(chat_id, f, caption=f"✅ تم التحميل عبر {CHANNEL}\n🤖 @MyDownload2026_bot")

            elif choice == "audio":
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': f'{tmpdir}/audio.%(ext)s',
                    'quiet': True,
                    'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    # اسم الملف بعد التحويل
                    filename = f"{tmpdir}/audio.mp3"
                with open(filename, 'rb') as f:
                    bot.send_audio(chat_id, f, title=info.get('title','audio'))

            elif choice == "thumb":
                ydl_opts = {'quiet': True, 'skip_download': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    thumb_url = info.get('thumbnail')
                if thumb_url:
                    bot.send_photo(chat_id, thumb_url, caption=f"🖼️ صورة الغلاف\n{CHANNEL}")
                else:
                    bot.send_message(chat_id, "❌ ما لقيت صورة")

        bot.delete_message(chat_id, call.message.message_id)

    except Exception as e:
        print(e)
        bot.edit_message_text("❌ فشل التحميل، جرب رابط تاني", chat_id, call.message.message_id)

bot.infinity_polling()
