import os, telebot, glob, re, requests
from telebot import types
import yt_dlp

TOKEN = os.getenv("TOKEN")
CHANNEL = "@BotKanal24"
CHANNEL_LINK = "https://t.me/BotKanal24"
bot = telebot.TeleBot(TOKEN)

WELCOME = "اهلا ابعت رابط وخلّي الباقي عليي"

PIPED_APIS = [
    "https://pipedapi.kavin.rocks",
    "https://pipedapi.adminforge.de",
    "https://api.piped.private.coffee"
]

def is_subscribed(uid):
    try:
        m = bot.get_chat_member(CHANNEL, uid)
        return m.status in ['member', 'administrator', 'creator']
    except Exception:
        return True

def get_yt_id(url):
    m = re.search(r'(?:youtu\.be/|shorts/|v=)([A-Za-z0-9_-]{11})', url)
    return m.group(1) if m else None

def download_via_piped(yt_id, user_id):
    for api in PIPED_APIS:
        try:
            r = requests.get(f"{api}/streams/{yt_id}", timeout=15).json()
            if "videoStreams" not in r:
                continue
            best = None
            for st in r["videoStreams"]:
                mime = st.get("mimeType", "")
                if "mp4" in mime and not st.get("videoOnly"):
                    best = st["url"]
                    break
            if not best:
                best = r["videoStreams"][0]["url"]
            file_path = f"/tmp/{user_id}.mp4"
            with requests.get(best, stream=True, timeout=60, headers={"User-Agent": "Mozilla/5.0"}) as rr:
                rr.raise_for_status()
                with open(file_path, 'wb') as f:
                    for chunk in rr.iter_content(1024*1024):
                        if chunk:
                            f.write(chunk)
            if os.path.getsize(file_path) > 10000:
                return file_path
        except Exception as e:
            print(f"PIPED {api} FAIL:", e)
            continue
    return None

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
        kb.add(types.InlineKeyboardButton("اشترك", url=CHANNEL_LINK))
        kb.add(types.InlineKeyboardButton("تحققت", callback_data="check"))
        bot.reply_to(m, "اشترك ثانية بس", reply_markup=kb)
        return
    s = bot.reply_to(m, "عم حملو...")
    for f in glob.glob(f"/tmp/{m.from_user.id}.*"):
        try:
            os.remove(f)
        except Exception:
            pass
    opts = {
        "outtmpl": f"/tmp/{m.from_user.id}.%(ext)s",
        "format": "best[ext=mp4]/best",
        "quiet": True,
        "noplaylist": True,
        "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
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
        yt_id = get_yt_id(url)
        if yt_id:
            try:
                bot.edit_message_text("عم جرب طريقة تانية...", m.chat.id, s.message_id)
                file = download_via_piped(yt_id, m.from_user.id)
            except Exception as e2:
                print("PIPED ALL FAIL:", e2)
    try:
        if file and os.path.exists(file):
            with open(file, 'rb') as f:
                bot.send_video(m.chat.id, f, caption="تم @BotKanal24")
            bot.delete_message(m.chat.id, s.message_id)
            os.remove(file)
        else:
            bot.edit_message_text("ما قدرت حملو، جرب رابط تاني", m.chat.id, s.message_id)
    except Exception as e:
        bot.edit_message_text(f"خطأ: {e}", m.chat.id, s.message_id)

@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    if is_subscribed(c.from_user.id):
        bot.send_message(c.message.chat.id, "تم! ابعت الرابط هلق")
    else:
        bot.answer_callback_query(c.id, "لسه ما اشتركت", show_alert=True)

bot.infinity_polling()
