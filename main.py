import os, json, re, requests, yt_dlp
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters

TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TOKEN")
CHANNEL = "@BotKanal24"

def clean_url(url):
    # يحذف?stkn و?img_index تلقائياً
    url = url.strip().split('?')[0].split('&')[0]
    # يحول https://www.instagram.com/reel/xxx/ ل /p/xxx/
    url = url.replace("/reel/", "/p/").replace("/reels/", "/p/")
    return url

async def start(update, context):
    kb = [[InlineKeyboardButton("📢 القناة", url="https://t.me/BotKanal24")]]
    await update.message.reply_text("🎉 أرسل أي رابط، البوت لحالو بينضفو ويحملو", reply_markup=InlineKeyboardMarkup(kb))

async def download(update, context):
    raw_url = update.message.text.strip()
    if not raw_url.startswith("http"):
        return
    url = clean_url(raw_url)
    msg = await update.message.reply_text(f"⏳ عم حمل:\n{url}")

    # 1. جرب yt-dlp أول شي (تيك توك ويوتيوب وفيديوهات انستا)
    try:
        ydl_opts = {'outtmpl': '%(id)s.%(ext)s', 'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if os.path.exists(filename):
                if filename.lower().endswith(('.jpg','.jpeg','.png','.webp')):
                    await update.message.reply_photo(photo=open(filename,'rb'))
                else:
                    await update.message.reply_video(video=open(filename,'rb'))
                os.remove(filename)
                await msg.delete()
                return
    except Exception as e:
        print(f"yt-dlp failed: {e}")

    # 2. إذا فشل وكان انستا صورة - جرب طريقة الصور المباشرة
    if "instagram.com" in url:
        try:
            shortcode_match = re.search(r"/p/([^/]+)/?", url)
            if shortcode_match:
                shortcode = shortcode_match.group(1)
                # استخدم ddinstagram اللي بيحل صور انستا
                dd_url = f"https://www.ddinstagram.com/p/{shortcode}/"
                r = requests.get(dd_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
                # دور على رابط الصورة أو الفيديو بـ og
                m_video = re.search(r'"og:video" content="([^"]+)"', r.text)
                m_image = re.search(r'"og:image" content="([^"]+)"', r.text)
                if m_video:
                    v_url = m_video.group(1)
                    await update.message.reply_video(video=v_url, caption="✅ تم التحميل")
                    await msg.delete()
                    return
                elif m_image:
                    i_url = m_image.group(1)
                    await update.message.reply_photo(photo=i_url, caption="✅ تم التحميل - صورة")
                    await msg.delete()
                    return
        except Exception as e2:
            print(f"insta fallback failed: {e2}")

    await msg.edit_text("❌ ما قدرت حل الرابط حتى بعد التنضيف\nجرب رابط تيك توك للتأكد، وانستا انسخ الرابط القصير فقط بدون?stkn")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
app.run_polling()
