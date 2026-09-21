import os, glob, tempfile, shutil
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
    if not is_subscribed(msg.from_user.id):
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("اشترك بقناتنا", url="https://t.me/BotKanal24"))
        mk.add(types.InlineKeyboardButton("تحققت ✅", callback_data="check"))
        bot.send_message(msg.chat.id, "اهلا منور\nلازم تشترك اول", reply_markup=mk)
    else:
        bot.send_message(msg.chat.id, "منور\nابعت رابط 📥")

@bot.callback_query_handler(func=lambda c: c.data=="check")
def check_sub(c):
    if is_subscribed(c.from_user.id):
        bot.send_message(c.message.chat.id, "تم ✅ ابعت رابط")
    else:
        bot.answer_callback_query(c.id, "لسه ما اشتركت!", show_alert=True)

@bot.message_handler(func=lambda m: m.text and m.text.startswith("http"))
def dl(msg):
    if not is_subscribed(msg.from_user.id):
        welcome(msg); return
    url = msg.text.strip()
    w = bot.reply_to(msg, "🔍 جاري البحث...")
    temp_data[msg.chat.id] = url
    mk = types.InlineKeyboardMarkup(row_width=2)
    mk.add(types.InlineKeyboardButton("🎥 فيديو", callback_data="video"), types.InlineKeyboardButton("🎵 صوت", callback_data="audio"))
    bot.edit_message_text("✅ اختار شو بدك تحمل", msg.chat.id, w.message_id, reply_markup=mk)

@bot.callback_query_handler(func=lambda c: c.data in ["video","audio","cancel"])
def handle(c):
    if c.data == "cancel": return
    cid = c.message.chat.id
    url = temp_data.get(cid)
    bot.edit_message_text("⏳ جاري التحميل...", cid, c.message.message_id)
    try:
        with tempfile.TemporaryDirectory() as tmp:
            # هاد السطر السحري يلي بيصلح المشكلة
            opts = {
                "format": "best[height<=720][ext=mp4]/best[ext=mp4]/best",
                "outtmpl": os.path.join(tmp, "file.%(ext)s"),
                "quiet": True,
                "extractor_args": {"youtube": {"player_client": ["android"]}}
            }
            if os.path.exists("cookies.txt"): opts["cookiefile"]="cookies.txt"
            with yt_dlp.YoutubeDL(opts) as y:
                info = y.extract_info(url, download=True)
                fn = y.prepare_filename(info)
                if not os.path.exists(fn):
                    fn = glob.glob(os.path.join(tmp, "*"))[0]

            with open(fn,"rb") as f:
                if c.data == "video":
                    bot.send_video(cid, f, caption=CHANNEL)
                else:
                    bot.send_audio(cid, f)
        bot.delete_message(cid, c.message.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ فشل: {e}", cid, c.message.message_id)

bot.infinity_polling()
