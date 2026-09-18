import os, telebot, sqlite3, yt_dlp, re
from telebot import types
from datetime import datetime

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
CHANNEL = "@BotKanal24"

bot = telebot.TeleBot(TOKEN)

conn = sqlite3.connect('stats.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, source TEXT)')
conn.commit()

WELCOME = """✅ تحميل فيديوهات تيك توك بدون علامة مائية
✅ تحميل ريلز وستوري انستغرام بجودة عالية
✅ تحميل فيديوهات فيسبوك بضغطة واحدة
✅ تحميل من يوتيوب فيديو MP4 وصوت MP3
✅ سريع جداً ⚡ ويعمل 24 ساعة
✅ مجاني 100% وبدون اعلانات مزعجة

طريقة الاستخدام:
فقط انسخ رابط الفيديو وارسله هنا، وسأقوم بتحميله لك فوراً!

المطور: السيد شيخ أحمد 👨‍💻
القناة الرسمية: @BotKanal24 📢"""

def is_subbed(uid):
    try:
        s = bot.get_chat_member(CHANNEL, uid).status
        return s in ['member','administrator','creator']
    except: return True

@bot.message_handler(commands=['start'])
def start(m):
    src = m.text.split()[1] if len(m.text.split())>1 else "direct"
    c.execute('INSERT OR IGNORE INTO users VALUES (?,?)', (m.from_user.id, src))
    conn.commit()
    if not is_subbed(m.from_user.id):
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("📢 اشترك", url=f"https://t.me/{CHANNEL[1:]}"))
        kb.add(types.InlineKeyboardButton("✅ تحققت", callback_data="chk"))
        bot.send_message(m.chat.id, f"🌟 اهلا {m.from_user.first_name} | البَاشَا 🌟\n👑 بوت التحميل 👑", reply_markup=kb)
        return
    bot.send_message(m.chat.id, WELCOME)

@bot.callback_query_handler(func=lambda x: x.data=="chk")
def chk(call):
    if is_subbed(call.from_user.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, WELCOME)
    else:
        bot.answer_callback_query(call.id, "❌ اشترك اول")

# هون الخيارات الجديدة
@bot.message_handler(func=lambda m: "instagram.com" in m.text or "tiktok.com" in m.text or "youtu" in m.text or "facebook.com" in m.text)
def ask_options(m):
    # نضف الرابط من البراميترات الزيادة
    url = m.text.strip().split()[0].split('?')[0] if '?' not in m.text or 'tiktok' not in m.text else m.text.strip().split()[0]
    # للانستا بدنا الرابط كامل بس بدون stkn
    url = re.sub(r'\?stkn=.*', '', m.text.strip())

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🎥 فيديو MP4", callback_data=f"vid|{url}"),
        types.InlineKeyboardButton("🎵 صوت MP3", callback_data=f"aud|{url}"),
        types.InlineKeyboardButton("🖼️ صورة / غلاف", callback_data=f"img|{url}")
    )
    bot.reply_to(m, "📥 اختر نوع التحميل:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: "|" in call.data)
def downloader(call):
    typ, url = call.data.split("|",1)
    bot.edit_message_text(f"⏳ عم حمّل {'الفيديو' if typ=='vid' else 'الصوت' if typ=='aud' else 'الصورة'}... انتظر", call.message.chat.id, call.message.message_id)
    try:
        opts = {'quiet': True, 'no_warnings': True}
        if typ == 'aud':
            opts.update({'format':'bestaudio/best', 'outtmpl':'audio.%(ext)s',
                         'postprocessors':[{'key':'FFmpegExtractAudio','preferredcodec':'mp3'}]})
        elif typ == 'vid':
            opts.update({'format':'best', 'outtmpl':'video.%(ext)s'})
        else:
            opts.update({'skip_download':True})

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=(typ!='img'))
            if typ == 'img':
                thumb = info.get('thumbnail')
                bot.send_photo(call.message.chat.id, thumb, caption="🖼️ هاي الصورة")
            elif typ == 'aud':
                bot.send_audio(call.message.chat.id, open('audio.mp3','rb'), title=info.get('title',''))
                os.remove('audio.mp3')
            else:
                fname = ydl.prepare_filename(info)
                bot.send_video(call.message.chat.id, open(fname,'rb'), caption="✅ تفضل")
                os.remove(fname)
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ خطأ: {e}")

@bot.message_handler(commands=['stats'])
def stats(m):
    if m.from_user.id!= ADMIN_ID: return
    c.execute('SELECT source, COUNT(*) FROM users GROUP BY source')
    txt="📊 من وين اجو:\n"
    for s,n in c.fetchall(): txt+=f"{s}: {n}\n"
    bot.send_message(m.chat.id, txt)

bot.infinity_polling()
