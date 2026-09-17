import os, re, telebot, yt_dlp
from telebot import types

BOT_TOKEN = os.getenv("BOT_TOKEN", "ضع_التوكن_الجديد_هنا_بعد_ما_تعمل_revoke")
bot = telebot.TeleBot(BOT_TOKEN)

user_links = {}
cache_files = {}

def clean_url(text):
    m = re.search(r'https?://\S+', text)
    if not m: return None
    return m.group(0)

@bot.message_handler(commands=['start'])
def start(m):
    name = m.from_user.first_name
    welcome_text = f"""
أهلين يا {name} 👋🔥

أنا بوت التحميل السريع - بحملك من:

🎬 تيك توك بدون علامة مائية
📸 انستا - ريلز وستوري
👍 فيسبوك - فيديو بجودة عالية

**شلون بتحمل؟**
1️⃣ ابعتلي رابط الفيديو هون بالخاص
2️⃣ رح ابعتلك الفيديو فوراً بدون علامة

**حركة الكروبات الرهيبة 👇**
بتقدر تحمل باي كروب بدون ما تطلع منو!
اكتب بقلب الكروب:
`@MyDownload2026_bot + رابط الفيديو`
ورح ينبعت الفيديو بالكروب فوراً 😍

جرب هلق ابعتلي أي رابط!
"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("➕ ضيفني لكروبك", url=f"https://t.me/{bot.get_me().username}?startgroup=true"),
        types.InlineKeyboardButton("🎬 كيف استخدم الانلاين؟", callback_data="how_inline")
    )
    bot.send_message(m.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "how_inline")
def how_inline(call):
    text = """
🎬 **طريقة الانلاين:**

1. فوت على أي كروب
2. اكتب: @MyDownload2026_bot https://vm.tiktok.com/xxxx/
3. استنى ثانية رح يطلعلك الفيديو فوق
4. كبوس عليه

لازم تكون باعت الرابط هون بالخاص مرة وحدة قبل!
"""
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def handle(m):
    url = clean_url(m.text)
    if not url: return
    user_links[m.chat.id] = url
    msg_status = bot.reply_to(m, "⏳ عم نزل الفيديو...")
    try:
        fname = f"temp_{m.chat.id}.mp4"
        opts = {'format': 'mp4/best', 'outtmpl': fname, 'quiet': True, 'noplaylist': True, 'overwrites': True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.extract_info(url, download=True)
        if not os.path.exists(fname):
            for f in os.listdir('.'):
                if f.startswith(f"temp_{m.chat.id}"): fname = f; break
        with open(fname, 'rb') as f:
            sent = bot.send_video(m.chat.id, f, caption="✅ تخزن! هلق فيك تستخدمو بالكروبات:\n@MyDownload2026_bot + الرابط")
            cache_files[url] = sent.video.file_id
        os.remove(fname)
        bot.delete_message(m.chat.id, msg_status.message_id)
    except Exception as e:
        print(e)
        bot.edit_message_text("❌ خطأ، الرابط خاص أو مو مدعوم", m.chat.id, msg_status.message_id)

@bot.inline_handler(lambda query: True)
def inline_query(inline):
    try:
        url = clean_url(inline.query.strip())
        if not url:
            res = types.InlineQueryResultArticle('1', 'الصق رابط تيك توك', types.InputTextMessageContent('الصق الرابط هنا'), description='حمل بدون علامة')
            return bot.answer_inline_query(inline.id, [res], cache_time=1, is_personal=True)

        # اذا متخزن
        for k, fid in cache_files.items():
            if url in k or k in url:
                result = types.InlineQueryResultCachedVideo(id="1", video_file_id=fid, title="✅ جاهز - كبوس لارسالو بالكروب", description="بدون علامة", caption="عبر @MyDownload2026_bot")
                return bot.answer_inline_query(inline.id, [result], cache_time=10, is_personal=True)

        res = types.InlineQueryResultArticle('1', '⚠️ ابعت الرابط للبوت بالخاص أول', types.InputTextMessageContent(f'ابعت هاد الرابط للبوت بالخاص أول:\n{url}\n\nبعدين ارجع لهون واكتب @MyDownload2026_bot + الرابط'), description='لازم تخزين أول مرة')
        bot.answer_inline_query(inline.id, [res], cache_time=1, is_personal=True)
    except Exception as e:
        print(f"Inline Error: {e}")

bot.infinity_polling()
