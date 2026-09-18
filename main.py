import os, telebot, sqlite3
from telebot import types
from datetime import datetime

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
CHANNEL = "@BotKanal24" # غيره اذا قناتك غير

bot = telebot.TeleBot(TOKEN)

conn = sqlite3.connect('stats.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, source TEXT, first_seen TEXT)')
conn.commit()

WELCOME_TEXT = """✅ تحميل فيديوهات تيك توك بدون علامة مائية
✅ تحميل ريلز وستوري انستغرام بجودة عالية
✅ تحميل فيديوهات فيسبوك بضغطة واحدة
✅ تحميل من يوتيوب فيديو MP4 وصوت MP3
✅ سريع جداً ⚡ ويعمل 24 ساعة
✅ مجاني 100% وبدون اعلانات مزعجة

طريقة الاستخدام:
فقط انسخ رابط الفيديو وارسله هنا، وسأقوم بتحميله لك فوراً!

المطور: السيد شيخ أحمد 👨‍💻
القناة الرسمية: @BotKanal24 📢"""

def is_subscribed(user_id):
    try:
        m = bot.get_chat_member(CHANNEL, user_id)
        return m.status in ['member','administrator','creator']
    except:
        return True

@bot.message_handler(commands=['start'])
def start(m):
    source = m.text.split()[1] if len(m.text.split()) > 1 else "direct"
    c.execute('INSERT OR IGNORE INTO users VALUES (?,?,?,?)',
              (m.from_user.id, m.from_user.username or m.from_user.first_name, source, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()

    if not is_subscribed(m.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 اشترك", url=f"https://t.me/{CHANNEL.replace('@','')}"))
        markup.add(types.InlineKeyboardButton("✅ تحققت", callback_data="check"))
        bot.send_message(m.chat.id, f"🌟 اهلا {m.from_user.first_name} | البَاشَا | ALBASHA 🌟\n👑 بوت التحميل 👑", reply_markup=markup)
        return

    bot.send_message(m.chat.id, WELCOME_TEXT)

@bot.callback_query_handler(func=lambda call: call.data=="check")
def check(call):
    if is_subscribed(call.from_user.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, WELCOME_TEXT)
    else:
        bot.answer_callback_query(call.id, "❌ لسه ما اشتركت!")

@bot.message_handler(commands=['stats'])
def stats(m):
    if m.from_user.id!= ADMIN_ID: return
    c.execute('SELECT source, COUNT(*) FROM users GROUP BY source')
    rows = c.fetchall()
    msg = "📊 **من وين اجو الناس:**\n\n"
    for src, count in rows:
        msg += f"🔹 {src}: {count}\n"
    c.execute('SELECT COUNT(*) FROM users')
    msg += f"\n👥 المجموع: {c.fetchone()[0]}"
    bot.send_message(m.chat.id, msg)

@bot.message_handler(func=lambda x: True)
def handle(m):
    if "instagram.com" in m.text or "tiktok.com" in m.text or "facebook.com" in m.text or "youtu" in m.text:
        bot.reply_to(m, "⏳ عم حمّل...")
        # كود التحميل هون

bot.infinity_polling()
