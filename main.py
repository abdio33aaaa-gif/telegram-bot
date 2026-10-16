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
            bot.send_photo(chat_id, f, caption="✅ @Storiesa6d_bot")
        else:
            bot.send_document(chat_id, f, caption="✅ @Storiesa6d_bot")


def process_link(chat_id, user_id, url):
    wait = bot.send_message(chat_id, "⏳ جاري التحميل...")
    tmp = tempfile.mkdtemp()
    ok = 0
    try:
        files = download_media(url, tmp)
        if not files:
            raise RuntimeError("no files")
        for p in files:
            send_file(chat_id, p)
        ok = 1
    except Exception as e:
        log.error("Download failed: %s", e)
        bot.send_message(
            chat_id,
            "❌ ما قدرت أحمل الرابط.\n"
            "تأكد إن الحساب عام وإن الستوري لسا موجود (ما انتهت 24 ساعة).",
        )
    finally:
        db("INSERT INTO downloads(user_id, ts, ok) VALUES(?,?,?)", (user_id, now(), ok))
        shutil.rmtree(tmp, ignore_errors=True)
        try:
            bot.delete_message(chat_id, wait.message_id)
        except Exception:
            pass


# ---------------- أوامر الأدمن ----------------
@bot.message_handler(commands=["admin"])
def admin_help(m):
    if not is_admin(m.from_user.id):
        return
    bot.send_message(
        m.chat.id,
        "🛠 لوحة الأدمن\n\n"
        "/stats - إحصائيات البوت\n"
        "/broadcast نص - إرسال رسالة لكل المستخدمين (أو رد على رسالة بالأمر)\n"
        "/ban ID - حظر مستخدم\n"
        "/unban ID - فك الحظر",
    )


@bot.message_handler(commands=["stats"])
def stats(m):
    if not is_admin(m.from_user.id):
        return
    t = today()
    total = db("SELECT COUNT(*) FROM users", fetch="one")[0]
    new = db("SELECT COUNT(*) FROM users WHERE joined LIKE ?", (t + "%",), "one")[0]
    banned = db("SELECT COUNT(*) FROM users WHERE banned=1", fetch="one")[0]
    dl_total = db("SELECT COUNT(*) FROM downloads WHERE ok=1", fetch="one")[0]
    dl_today = db("SELECT COUNT(*) FROM downloads WHERE ok=1 AND ts LIKE ?", (t + "%",), "one")[0]
    failed = db("SELECT COUNT(*) FROM downloads WHERE ok=0", fetch="one")[0]
    active = db("SELECT COUNT(DISTINCT user_id) FROM downloads WHERE ts LIKE ?", (t + "%",), "one")[0]
    bot.send_message(
        m.chat.id,
        "📊 إحصائيات البوت\n\n"
        f"👥 المستخدمين: {total}\n"
        f"🆕 جدد اليوم: {new}\n"
        f"🔥 نشطين اليوم: {active}\n"
        f"🚫 محظورين: {banned}\n\n"
        f"📥 تحميلات ناجحة: {dl_total}\n"
        f"📅 تحميلات اليوم: {dl_today}\n"
        f"❌ تحميلات فاشلة: {failed}",
    )


def do_broadcast(admin_chat, text=None, copy_from=None):
    users = db("SELECT user_id FROM users WHERE banned=0", fetch="all")
    sent = failed = 0
    for (uid,) in users:
        try:
            if copy_from:
                bot.copy_message(uid, copy_from[0], copy_from[1])
            else:
                bot.send_message(uid, text)
            sent += 1
        except Exception:
            failed += 1
        time.sleep(0.05)  # تجنب حدود تيليجرام
    bot.send_message(admin_chat, f"✅ انتهى الإرسال\nوصلت: {sent}\nفشلت (حاظرين البوت غالباً): {failed}")


@bot.message_handler(commands=["broadcast"])
def broadcast(m):
    if not is_admin(m.from_user.id):
        return
    parts = m.text.split(maxsplit=1)
    if m.reply_to_message:
        src = (m.chat.id, m.reply_to_message.message_id)
        threading.Thread(target=do_broadcast, args=(m.chat.id, None, src), daemon=True).start()
    elif len(parts) == 2:
        threading.Thread(target=do_broadcast, args=(m.chat.id, parts[1]), daemon=True).start()
    else:
        bot.send_message(m.chat.id, "اكتب: /broadcast نص الرسالة\nأو رد على رسالة بـ /broadcast")
        return
    bot.send_message(m.chat.id, "📣 بدأ الإرسال...")


def set_ban(m, value):
    if not is_admin(m.from_user.id):
        return
    parts = m.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        bot.send_message(m.chat.id, "الاستخدام: /ban 123456789")
        return
    uid = int(parts[1])
    db("INSERT OR IGNORE INTO users(user_id, username, joined) VALUES(?,?,?)", (uid, "", now()))
    db("UPDATE users SET banned=? WHERE user_id=?", (value, uid))
    bot.send_message(m.chat.id, ("🚫 تم حظر " if value else "✅ تم فك الحظر عن ") + str(uid))


@bot.message_handler(commands=["ban"])
def ban(m):
    set_ban(m, 1)


@bot.message_handler(commands=["unban"])
def unban(m):
    set_ban(m, 0)


# ---------------- أوامر المستخدمين ----------------
@bot.message_handler(commands=["start"])
def start(m):
    register(m.from_user)
    if is_banned(m.from_user.id):
        return
    if not is_subscribed(m.from_user.id):
        bot.send_message(
            m.chat.id,
            f"🚀 لتحميل ستوري انستا بجودة HD وبدون اعلانات\n\n"
            f"⚠️ يجب ان تشترك اولاً في قناتنا الرسمية:\n{CHANNEL}\n\nاشترك وبعدها اضغط تحققت",
            reply_markup=sub_markup(),
        )
        return
    bot.send_message(
        m.chat.id,
        "🚀 حمّل ستوري انستا بجودة HD | سريع - آمن - بدون اعلانات\n\n"
        "ابعت رابط الستوري العام\n\n@Storiesa6d_bot",
    )


@bot.callback_query_handler(func=lambda c: c.data == "check_sub")
def check(c):
    if is_subscribed(c.from_user.id):
        bot.answer_callback_query(c.id)
        try:
            bot.delete_message(c.message.chat.id, c.message.message_id)
        except Exception:
            pass
        bot.send_message(c.message.chat.id, "✅ تم الاشتراك بنجاح! ابعت رابط الستوري هلق")
    else:
        bot.answer_callback_query(c.id, f"❌ لسا ما اشتركت في {CHANNEL}", show_alert=True)


@bot.message_handler(func=lambda m: True, content_types=["text"])
def handle(m):
    register(m.from_user)
    if is_banned(m.from_user.id):
        return
    if not is_subscribed(m.from_user.id):
        bot.send_message(m.chat.id, f"❌ لازم تشترك اولاً: {CHANNEL}", reply_markup=sub_markup())
        return
    match = IG_REGEX.search(m.text or "")
    if not match:
        bot.send_message(m.chat.id, "⚠️ ابعت رابط انستغرام صحيح، مثال:\nhttps://www.instagram.com/stories/username/123456789/")
        return
    threading.Thread(
        target=process_link, args=(m.chat.id, m.from_user.id, match.group(0)), daemon=True
    ).start()


def run_bot():
    bot.infinity_polling(skip_pending=True)


def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    init_db()
    threading.Thread(target=run_bot, daemon=True).start()
    run_web()
