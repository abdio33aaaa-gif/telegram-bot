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
        txt = "اهلا " + name + " | الباشا\n\nبوت التحميل الاسطوري\nلازم تشترك اول"
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("اشترك بقناتنا", url="https://t.me/BotKanal24"))
        mk.add(types.InlineKeyboardButton("تحققت", callback_data="check"))
        bot.send_message(msg.chat.id, txt, reply_markup=mk)
    else:
        bot.send_message(msg.chat.id, "اهلا " + name + " منور\nابعت رابط")

@bot.callback_query_handler(func=lambda c: c.data=="check")
def check_sub(c):
    if is_subscribed(c.from_user.id):
        try:
            bot.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass
        bot.send_message(c.message.chat.id, "تم التفعيل\nابعت رابط")
    else:
        bot.answer_callback_query(c.id, "لسه ما اشتركت!", show_alert=True)

@bot.message_handler(func=lambda m: m.text and m.text.startswith("http"))
def dl(msg):
    if not is_subscribed(msg.from_user.id):
        welcome(msg)
        return
    url = msg.text.strip()
    w = bot.reply_to(msg, "جبت الفيديو")
    temp_data[msg.chat.id] = url
    mk = types.InlineKeyboardMarkup(row_width=2)
    mk.add(types.InlineKeyboardButton("فيديو", callback_data="video"), types.InlineKeyboardButton("صوت", callback_data="audio"))
    mk.add(types.InlineKeyboardButton("صورة", callback_data="thumb"), types.InlineKeyboardButton("الغاء", callback_data="cancel"))
    bot.edit_message_text("تم العثور على الفيديو", msg.chat.id, w.message_id, reply_markup=mk)

@bot.callback_query_handler(func=lambda c: c.data in ["video","audio","thumb","cancel"])
def handle(c):
    choice = c.data
    cid = c.message.chat.id
    if choice == "cancel":
        try:
            bot.delete_message(cid, c.message.message_id)
        except:
            pass
        return
    url = temp_data.get(cid)
    if not url:
        bot.answer_callback_query(c.id, "ابعت الرابط مرة تانية")
        return
    bot.edit_message_text("جاري التحميل " + choice, cid, c.message.message_id)
    try:
        with tempfile.TemporaryDirectory() as tmp:
            if choice == "video":
                out = os.path.join(tmp, "video.%(ext)s")
                opts = {"format":"best","outtmpl":out,"quiet":True}
                with yt_dlp.YoutubeDL(opts) as y:
                    info = y.extract_info(url, download=True)
                    fn = y.prepare_filename(info)
                with open(fn,"rb") as f:
                    bot.send_video(cid, f, caption=CHANNEL)
            elif choice == "audio":
                out = os.path.join(tmp, "audio.%(ext)s")
                opts = {"format":"bestaudio/best","outtmpl":out,"quiet":True,"postprocessors":[{"key":"FFmpegExtractAudio","preferredcodec":"mp3","preferredquality":"192"}]}
                with yt_dlp.YoutubeDL(opts) as y:
                    info = y.extract_info(url, download=True)
                mp3 = glob.glob(os.path.join(tmp,"*.mp3"))[0]
                with open(mp3,"rb") as f:
                    bot.send_audio(cid, f)
            elif choice == "thumb":
                opts = {"quiet":True,"skip_download":True}
                with yt_dlp.YoutubeDL(opts) as y:
                    info = y.extract_info(url, download=False)
                    th = info.get("thumbnail")
                if th:
                    bot.send_photo(cid, th)
                else:
                    bot.send_message(cid, "ما لقيت صورة")
        try:
            bot.delete_message(cid, c.message.message_id)
        except:
            pass
    except Exception as e:
        print(e)
        bot.edit_message_text("فشل التحميل", cid, c.message.message_id)

bot.infinity_polling()
