import os, glob, tempfile
import telebot
from telebot import types
import yt_dlp

TOKEN = os.getenv("TOKEN") or os.getenv("BOT_TOKEN")
CHANNEL = "@BotKanal24"
bot = telebot.TeleBot(TOKEN.strip())
temp_data = {}

def is_subscribed(uid):
    try:
        m = bot.get_chat_member(CHANNEL, uid)
        return m.status in ['member','administrator','creator']
    except:
        return False

@bot.message_handler(commands=['start'])
def welcome(msg):
    name = msg.from_user.first_name
    uid = msg.from_user.id
    if not is_subscribed(uid):
        txt = f"اهلا {name} | الباشا منور\n\nبوت التحميل الاسطوري\nلازم تشترك اول"
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("اشترك بقناتنا", url="https://t.me/BotKanal24"))
        mk.add(types.InlineKeyboardButton("تحققت ✅", callback_data="check"))
        bot.send_message(msg.chat.id, txt, reply_markup=mk)
    else:
        bot.send_message(msg.chat.id, f"اهلا {name} منور\nابعت رابط 📥")

@bot.callback_query_handler(func=lambda c: c.data=="check")
def check_sub(c):
    if is_subscribed(c.from_user.id):
        try: bot.delete_message(c.message.chat.id, c.message.message_id)
        except: pass
        bot.send_message(c.message.chat.id, "تم التفعيل ✅\nابعت رابط")
    else:
        bot.answer_callback_query(c.id, "لسه ما اشتركت!", show_alert=True)

# --- الاعدادات الجديدة يلي بتصلح يوتيوب ---
def get_ydl_opts(tmp, choice="video"):
    base = {
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
        "geo_bypass": True,
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"], # اهم سطر لاصلاح يوتيوب
                "player_skip": ["webpage"]
            }
        },
    }
    # اذا عندك ملف cookies.txt حطو جنب البوت
    if os.path.exists("cookies.txt"):
        base["cookiefile"] = "cookies.txt"

    if choice == "video":
        base.update({
            "format": "bv*[height<=720][ext=mp4]+ba[ext=m4a]/best[height<=720]/best",
            "outtmpl": os.path.join(tmp, "video.%(ext)s"),
            "merge_output_format": "mp4"
        })
    elif choice == "audio":
        base.update({
            "format": "bestaudio/best",
            "outtmpl": os.path.join(tmp, "audio.%(ext)s"),
            "postprocessors": [{"key": "FFmpegExtractAudio","preferredcodec": "mp3","preferredquality": "192"}]
        })
    return base

@bot.message_handler(func=lambda m: m.text and m.text.startswith("http"))
def dl(msg):
    if not is_subscribed(msg.from_user.id):
        welcome(msg)
        return
    url = msg.text.strip()
    w = bot.reply_to(msg, "🔍 جاري البحث عن الفيديو...")
    temp_data[msg.chat.id] = url
    mk = types.InlineKeyboardMarkup(row_width=2)
    mk.add(types.InlineKeyboardButton("🎥 فيديو", callback_data="video"), types.InlineKeyboardButton("🎵 صوت", callback_data="audio"))
    mk.add(types.InlineKeyboardButton("🖼️ صورة", callback_data="thumb"), types.InlineKeyboardButton("❌ الغاء", callback_data="cancel"))
    bot.edit_message_text("✅ تم العثور على الفيديو", msg.chat.id, w.message_id, reply_markup=mk)

@bot.callback_query_handler(func=lambda c: c.data in ["video","audio","thumb","cancel"])
def handle(c):
    choice = c.data
    cid = c.message.chat.id
    if choice == "cancel":
        try: bot.delete_message(cid, c.message.message_id)
        except: pass
        return
    url = temp_data.get(cid)
    if not url:
        bot.answer_callback_query(c.id, "ابعت الرابط مرة تانية")
        return
    bot.edit_message_text(f"⏳ جاري التحميل {choice}...", cid, c.message.message_id)
    try:
        with tempfile.TemporaryDirectory() as tmp:
            if choice == "video":
                opts = get_ydl_opts(tmp, "video")
                with yt_dlp.YoutubeDL(opts) as y:
                    info = y.extract_info(url, download=True)
                    fn = y.prepare_filename(info)
                    # اذا الدمج خلق mp4
                    if not os.path.exists(fn):
                        fn = glob.glob(os.path.join(tmp, "video.*"))[0]
                with open(fn,"rb") as f:
                    bot.send_video(cid, f, caption=CHANNEL, supports_streaming=True)

            elif choice == "audio":
                opts = get_ydl_opts(tmp, "audio")
                with yt_dlp.YoutubeDL(opts) as y:
                    y.extract_info(url, download=True)
                mp3 = glob.glob(os.path.join(tmp,"*.mp3"))
                if mp3:
                    with open(mp3[0],"rb") as f:
                        bot.send_audio(cid, f, title="Audio")
                else:
                    raise Exception("MP3 not found - FFmpeg missing?")

            elif choice == "thumb":
                opts = {"quiet":True,"skip_download":True, "extractor_args": {"youtube": {"player_client": ["android"]}}}
                if os.path.exists("cookies.txt"): opts["cookiefile"]="cookies.txt"
                with yt_dlp.YoutubeDL(opts) as y:
                    info = y.extract_info(url, download=False)
                    th = info.get("thumbnail")
                if th: bot.send_photo(cid, th)
                else: bot.send_message(cid, "ما لقيت صورة")

        try: bot.delete_message(cid, c.message.message_id)
        except: pass

    except Exception as e:
        print(f"ERROR: {e}")
        # رسالة اوضح الك
        bot.edit_message_text(f"❌ فشل التحميل\nالسبب: {str(e)[:200]}", cid, c.message.message_id)

bot.infinity_polling()
