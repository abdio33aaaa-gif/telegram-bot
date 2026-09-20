import os
import glob
import telebot
from telebot import types
import yt_dlp
import tempfile

# ========= الاعدادات =========
TOKEN = os.getenv("TOKEN") or os.getenv("BOT_TOKEN") or os.getenv("BOT_TOK")
if not TOKEN:
    for k,v in os.environ.items():
        if "BOT" in k and ":" in str(v):
            TOKEN = v
            break
if not TOKEN:
    raise ValueError("TOKEN not found! حط التوكن بالـ Environment")

CHANNEL = "@BotKanal24"  # قناتك
bot = telebot.TeleBot(TOKEN.strip())

temp_data = {}

def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"check sub error: {e}")
        return False

# ========= START =========
@bot.message_handler(commands=['start'])
def welcome(message):
    name = message.from_user.first_name
    user_id = message.from_user.id

    if not is_subscribed(user_id):
        text = f"""🌟 اهلا {name} | الباشا 👑

👑 بوت نزّل الاسطوري
🎬 تيك توك | 📸 انستا | 📘 فيسبوك | 🎥 يوتيوب

🔒 يا {name} لازم تشترك بقناتنا بالأول مشان فعل البوت الك 👇"""
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("📢 اشترك بقناتنا", url=f"https://t.me/{CHANNEL.replace('@','')}"))
        markup.add(types.InlineKeyboardButton("✅ تحققت", callback_data="check"))
        bot.send_message(message.chat.id, text, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, f"✅ اهلا {name} | الباشا منور\n📥 ابعت رابط الفيديو هلق وجرب")

# ========= زر التحقق =========
@bot.callback_query_handler(func=lambda call: call.data == "check")
def check_sub(call):
    user_id = call.from_user.id
    name = call.from_user.first_name
    if is_subscribed(user_id):
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        bot.send_message(call.message.chat.id, f"✅ عاش يا {name}! تم التفعيل يا بطل\n📥 ابعت رابط الفيديو هلق")
    else:
        bot.answer_callback_query(call.id, "❌ لسه ما اشتركت بقناتنا! اشترك وبعدين دوس تحققت", show_alert=True)

# ========= استقبال الرابط =========
@bot.message_handler(func=lambda m: m.text and m.text.strip().startswith("http"))
def downloader(message):
    # حماية - اذا مو مشترك رجعو لرسالة الاشتراك
    if not is_subscribed(message.from_user.id):
        welcome(message)
        return

    url = message.text.strip()
    wait = bot.reply_to(message, "🔍 جبت الفيديو، شو بدك تحمل؟")
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

# ========= خيارات التحميل =========
@bot.callback_query_handler(func=lambda call: call.data in ["video", "audio", "thumb", "cancel"])
def handle_choice(call):
    choice = call.data
    chat_id = call.message.chat.id

    if choice == "cancel":
        try:
            bot.delete_message(chat_id, call.message.message_id)
        except:
            pass
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
                    bot.send_video(chat_id, f, caption=f"✅ عبر {CHANNEL}\n🤖 @MyDownload2026_bot")

            elif choice == "audio":
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': f'{tmpdir}/audio.%(ext)s',
                    'quiet': True
