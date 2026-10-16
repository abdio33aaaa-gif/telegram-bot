import os, re, html, glob, shutil, sqlite3, tempfile, threading, time, logging
from datetime import datetime, timezone
import telebot
import yt_dlp
from flask import Flask

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("fastbot")

TOKEN = os.getenv("BOT_TOKEN")  # توكن بوت التحميل السريع
ADMIN_IDS = {int(x) for x in os.getenv("ADMIN_ID", "").split(",") if x.strip().isdigit()}
CHANNEL = os.getenv("CHANNEL", "@BotKanal24")
CHANNEL_LINK = os.getenv("CHANNEL_LINK", "https://t.me/BotKanal24")
COOKIES_FILE = os.getenv("COOKIES_FILE")      # مسار cookies.txt (اختياري)
DB_PATH = os.getenv("DB_PATH", "fastbot.db")
MAX_SIZE = 49 * 1024 * 1024

URL_REGEX = re.compile(
    r"https?://(?:[\w-]+\.)*(?:tiktok\.com|instagram\.com|facebook\.com|fb\.watch|fb\.com|youtube\.com|youtu\.be)/\S*",
    re.I,
)

def welcome_text(user):
    name = html.escape(user.first_name or "صديقي")
    return (
        "┏━━━━━━━━━━━━━━━━━━┓\n"
        "  🚀 <b>بوت التحميل السريع 2026</b>\n"
        "┗━━━━━━━━━━━━━━━━━━┛\n\n"
        f"👋 أهلاً بك <b>{name}</b>\n\n"
        "✨ <b>حمّل أي مقطع بضغطة وحدة:</b>\n\n"
        "🎵 <b>TikTok</b> ⟵ بدون علامة مائية\n"
        "📸 <b>Instagram</b> ⟵ ريلز • ستوري • منشورات\n"
        "📘 <b>Facebook</b> ⟵ فيديوهات وريلز\n"
        "▶️ <b>YouTube</b> ⟵ فيديوهات وشورتس\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "⚡ سريع  •  🔒 آمن  •  🚫 بدون إعلانات\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "📎 <b>أرسل الرابط الآن</b> وأنا أرسل لك المقطع 👇"
    )


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
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, platform TEXT, ts TEXT, ok INTEGER)""")


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


def platform_of(url):
    u = url.lower()
    if "tiktok" in u:
        return "tiktok"
    if "instagram" in u:
        return "instagram"
    if "facebook" in u or "fb." in u:
        return "facebook"
    return "youtube"


# ---------------- الويب ----------------
@app.route("/")
def home():
    return "Fast Download Bot is Running!"


# ---------------- الاشتراك (إجباري) ----------------
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


def ask_subscribe(chat_id):
    bot.send_message(
        chat_id,
        "🔒 <b>الاشتراك إجباري</b>\n\n"
        "لاستخدام البوت لازم تشترك أولاً في قناتنا الرسمية:\n"
        f"📢 {CHANNEL}\n\n"
        "اشترك ثم اضغط <b>✅ تحققت</b>",
        reply_markup=sub_markup(),
        parse_mode="HTML",
    )


# ---------------- التحميل ----------------
def download_media(url, out_dir):
    opts = {
        "outtmpl": os.path.join(out_dir, "%(id)s.%(ext)s"),
        # ملف واحد جاهز (بدون ffmpeg) وبحجم مناسب لتيليجرام
        "format": "b[filesize<49M]/b[filesize_approx<49M]/b[height<=480]/b",
        "quiet": True,
        "noplaylist": True,
        "max_filesize": MAX_SIZE,
        "socket_timeout": 30,
    }
    if COOKIES_FILE and os.path.exists(COOKIES_FILE):
        opts["cookiefile"] = COOKIES_FILE
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
    return sorted(glob.glob(os.path.join(out_dir, "*")))


def send_file(chat_id, path):
    ext = os.path.splitext(path)[1].lower()
    caption = "✅ تم التحميل"
    with open(path, "rb") as f:
        if ext in (".mp4", ".mov", ".webm", ".mkv"):
            bot.send_video(chat_id, f, caption=caption, supports_streaming=True)
        elif ext in (".jpg", ".jpeg", ".png", ".webp"):
            bot.send_photo(chat_id, f, caption=caption)
        elif ext in (".mp3", ".m4a"):
            bot.send_audio(chat_id, f, caption=caption)
        else:
            bot.send_document(chat_id, f, caption=caption)


def process_link(chat_id, user_id, url):
    wait = bot.send_message(chat_id, "⏳ جاري تحليل الرابط...")
    bot.send_chat_action(chat_id, "typing")
    tmp = tempfile.mkdtemp()
    ok = 0
    try:
        files = download_media(url, tmp)
        if not files:
            raise RuntimeError("no files")
        try:
            bot.edit_message_text("📤 جاري إرسال المقطع المرئي...", chat_id, wait.message_id)
        except Exception:
            pass
        bot.send_chat_action(chat_id, "upload_video")
        for p in files:
            send_file(chat_id, p)
        ok = 1
    except Exception as e:
        log.error("Download failed: %s", e)
        bot.send_message(
            chat_id,
            "❌ ما قدرت أحمل الرابط.\n"
            "تأكد إن الرابط صحيح والفيديو عام، وإن حجمه أقل من 50MB.",
        )
    finally:
        db("INSERT INTO downloads(user_id, platform, ts, ok) VALUES(?,?,?,?)",
           (user_id, platform_of(url), now(), ok))
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
    per = db("SELECT platform, COUNT(*) FROM downloads WHERE ok=1 GROUP BY platform", fetch="all")
    names = {"tiktok": "TikTok", "instagram": "Instagram", "facebook": "Facebook", "youtube": "YouTube"}
    per_txt = "\n".join(f"   • {names.get(p, p)}: {c}" for p, c in per) or "   —"
    bot.send_message(
        m.chat.id,
        "📊 إحصائيات البوت\n\n"
        f"👥 المستخدمين: {total}\n"
        f"🆕 جدد اليوم: {new}\n"
        f"🔥 نشطين اليوم: {active}\n"
        f"🚫 محظورين: {banned}\n\n"
        f"📥 تحميلات ناجحة: {dl_total}\n"
        f"📅 تحميلات اليوم: {dl_today}\n"
        f"❌ تحميلات فاشلة: {failed}\n\n"
        f"📱 حسب المنصة:\n{per_txt}",
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
        time.sleep(0.05)
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
        ask_subscribe(m.chat.id)
        return
    bot.send_message(m.chat.id, welcome_text(m.from_user), parse_mode="HTML")


@bot.callback_query_handler(func=lambda c: c.data == "check_sub")
def check(c):
    if is_subscribed(c.from_user.id):
        bot.answer_callback_query(c.id)
        try:
            bot.delete_message(c.message.chat.id, c.message.message_id)
        except Exception:
            pass
        bot.send_message(c.message.chat.id, "✅ <b>تم الاشتراك بنجاح!</b>\n\n" + welcome_text(c.from_user), parse_mode="HTML")
    else:
        bot.answer_callback_query(c.id, f"❌ لسا ما اشتركت في {CHANNEL}", show_alert=True)


@bot.message_handler(func=lambda m: True, content_types=["text"])
def handle(m):
    register(m.from_user)
    if is_banned(m.from_user.id):
        return
    if not is_subscribed(m.from_user.id):
        ask_subscribe(m.chat.id)
        return
    match = URL_REGEX.search(m.text or "")
    if not match:
        bot.send_message(m.chat.id, "⚠️ ابعت رابط صحيح من TikTok أو Instagram أو Facebook أو YouTube")
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
