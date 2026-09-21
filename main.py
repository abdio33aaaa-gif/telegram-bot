import os, telebot, glob, re, requests
from telebot import types
import yt_dlp

TOKEN = os.getenv("TOKEN")
CHANNEL = "@BotKanal24"
CHANNEL_LINK = "https://t.me/BotKanal24"
bot = telebot.TeleBot(TOKEN)

WELCOME = "اهلا 😍 ابعت رابط وخلّي الباقي عليي 🚀"

def is_subscribed(uid):
    try:
        m = bot.get_chat_member(CHANNEL, uid)
        return m.status in ['member','administrator','creator']
    except:
        return True

def get_yt_id(url):
    m = re.search(r'(?:youtu\.be/|v=)([A-Za-z0-9_-]{11})', url)
    return m.group(1) if m else None

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, WELCOME)

@bot.message_handler(func=lambda m: True)
def handle(m):
    url = m.text.strip()
    if "http" not in url:
        return
    if not is_subscribed(m.from_user.id):
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("📢 اشترك", url=CHANNEL_LINK))
        kb.add(types.InlineKeyboardButton("✅ تحققت", callback_data="check"))
        bot.reply_to(m, "اشترك ثانية بس 👇", reply_markup=kb)
        return

    s = bot.reply_to(m, "⏳ عم حملو...")
    for f in glob.glob(f"/tmp/{m.from_user.id}.*"):
        try: os.remove(f)
        except: pass

    # المحاولة 1: الطريقة العادية (بتشتغل لفيسبوك وتيك توك وانستا)
    opts = {
        "outtmpl": f"/tmp/{m.from_user.id}.%(ext)s",
        "format": "best[ext=mp4]/best",
        "quiet": True,
        "noplaylist": True,
        "extractor_args": {"youtube": {"player_client": ["android"]}},
    }
    if os.path.exists("cookies.txt"):
        opts["cookiefile"] = "cookies.txt"

    file = None
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file = ydl.prepare_filename(info)
            if not os.path.exists(file):
                files = glob.glob(f"/tmp/{m.from_user.id}.*")
                file = files[0] if files else None
    except Exception as e:
        print("YT-DLP FAIL:", e)
        # المحاولة 2: لليوتيوب فقط - عن طريق Piped
        yt_id = get_yt_id(url)
        if yt_id:
            try:
                bot.edit_message_text("⏳ عم جرب طريقة تانية لليوتيوب...", m.chat.id, s.message_id)
                # نجيب رابط مباشر من Piped
                r = requests.get(f"https://api.piped.private.coffee/streams/{yt_id}", timeout=15).json()
                # ناخد احسن جودة mp4
                streams = r.get("videoStreams", []) or r.get("audioStreams", [])
                best = None
                for st in r.get("videoStreams", []):
                    if st.get("mimeType") == "video/mp4":
                        best = st["url"]
                        break
                if best:
                    # نحمل الملف
                    file_path = f"/tmp/{m.from_user.id}.mp4"
                    with requests.get(best, stream=True, timeout=30) as rr:
                        with open(file_path, 'wb') as f:
                            for chunk in rr.iter_content(1024*1024):
                                f.write(chunk)
                    file = file_path
            except Exception as e2:
                print("PIPED FAIL:", e2)

    try:
        if file and os.path.exists(file):
            with open(file, 'rb') as f:
                bot.send_video(m.chat.id, f, caption="تم ✅ @BotKanal24")
            bot.delete_message(m.chat.id, s.message_id)
            os.remove(file)
        else:
            bot.edit_message_text("❌ ما قدرت حلو، يوتيوب حاظر السيرفر حاليا، جرب تيك توك او فيسبوك بيشتغلو فورا", m.chat.id, s.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ خطأ: {e}", m.chat.id, s.message_id)

@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    if is_subscribed(c.from_user.id):
        bot.send_message(c.message.chat.id, "تم! ابعت الرابط هلق 🚀")
    else:
        bot.answer_callback_query(c.id, "لسه ما اشتركت ❌", show_alert=True)

bot.infinity_polling()
