import os, re, glob, shutil, sqlite3, tempfile, threading, time, logging
from datetime import datetime, timezone
import telebot
import yt_dlp
from flask import Flask

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("storiesbot")

TOKEN = os.getenv("BOT_TOKEN")  # توكن @Storiesa6d_bot
ADMIN_IDS = {int(x) for x in os.getenv("ADMIN_ID", "").split(",") if x.strip().isdigit()}
CHANNEL = "@BotKanal24"
CHANNEL_LINK = "https://t.me/BotKanal24"
COOKIES_FILE = os.getenv("IG_COOKIES")
DB_PATH = os.getenv("DB_PATH", "bot.db")
MAX_SIZE = 49 * 1024 * 1024

IG_REGEX = re.compile(r"https?://(www\.)?instagram\.com/\S+", re.I)

bot = telebot.TeleBot(TOKEN, threaded=True)
app = Flask(__name__)


# ---------------- قاعدة البيانات ----------------
def db(query, args=(), fetch=None):
    conn = sqlite3.connect(DB_PATH, timeout=10)
    try:
        cur = conn.execute(query, args)
        conn.commit()
        if fetch == "one":
            return cur.fetchone()
        if fetch == "all":
            return cur.fetchall()
    finally:
        conn.close()


def init_db():
    db("""CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY, username TEXT, joined TEXT, banned INTEGER DEFAULT 0)""")
    db("""CREATE TABLE IF NOT EXISTS downloads(
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, ts TEXT, ok INTEGER)""")


def today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def register(user):
    db("INSERT OR IGNORE INTO users(user_id, username, joined) VALUES(?,?,?)",
       (user.id, user.username or "", now()))


def is_banned(user_id):
    r = db("SELECT banned FROM users WHERE user_id=?", (user_id,), "one")
    return bool(r and r[0])


def is_admin(user_id):
    return user_id in ADMIN_IDS


# ---------------- الويب ----------------
@app.route("/")
def home():
    return "Storiesa6d_bot is Running!"


# ---------------- الاشتراك ----------------
def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(CHANNEL, user_id).status
        return status in ("member", "administrator", "creator")
    except Exception as e:
        log.error("Subscription check failed: %s", e)
        return False


def sub_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("📢 اشترك في القناة", url=CHANNEL_LINK))
    markup.add(telebot.types.InlineKeyboardButton("✅ تحققت", callback_data="check_sub"))
    return markup


# ---------------- التحميل ----------------
def download_media(url, out_dir):
    opts = {
        "outtmpl": os.path.join(out_dir, "%(id)s.%(ext)s"),
        "format": "best",
        "quiet": True,
        "noplaylist": True,
        "max_filesize": MAX_SIZE,
    }
    if COOKIES_FILE and os.path.exists(COOKIES_FILE):
        opts["cookiefile"] = COOKIES_FILE
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
    return sorted(glob.glob(os.path.join(out_dir, "*")))


def send_file(chat_id, path):
    ext = os.path.splitext(path)[1].lower()
    with open(path, "rb") as f:
        if ext in (".mp4", ".mov", ".webm", ".mkv"):
            bot.send_video(chat_id, f, caption="✅ @Storiesa6d_bot", supports_streaming=True)
        elif ext in (".jpg", ".jpeg", ".png", ".webp"):
            bot.send_photo(chat_id, f,
