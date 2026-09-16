import os, re, requests, yt_dlp
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters

TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TOKEN")

def clean_url(url):
    url = url.strip().split('?')[0].split('&')[0].split('=')[0]
    return url

async def start(update, context):
    kb = [[InlineKeyboardButton("📢 القناة الرسمية", url="https://t.me/BotKanal24")]]
    await update.message.reply_text(
        "🎉 **أهلاً يا بطل!**\n\n"
        "أرسل أي رابط من انستا / تيك توك / يوتيوب\n"
        "ورح حملو الك بأعلى جودة وبدون علامة مائية ✨\n\n"
        "@BotKanal24",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown"
    )

async def download(update, context):
    raw = update.message.text.strip()
    if not raw.startswith("http"):
        return

    url = clean_url(raw)
    m = re.search(r"/p/([^/=\s]+)", raw)
    if m:
        shortcode = m.group(1)[:11]
        url = f"https://www.instagram.com/p/{shortcode}/"

    # رسالة التحميل الحلوة الجديدة
    msg = await update.message.reply_text(
        "⏳ **لحظة يا غالي...**\n\n"
        "✨ عم جهزلك الفيديو بأعلى جودة\n"
        "💙 شكراً لصبرك، رغبة المستخدم تهمنا",
        parse_mode="Markdown"
    )

    # 1 - yt-dlp
    try:
        ydl_opts = {
            'outtmpl': '%(id)s.%(ext)s',
            'quiet': True,
            'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            fn = ydl.prepare_filename(info)
            if os.path.exists(fn):
                if fn.lower().endswith(('.jpg','.jpeg','.png','.webp')):
                    await update.message.reply_photo(photo=open(fn,'rb'), caption="✅ **تفضل، تم التحميل بنجاح!**\n\n@BotKanal24", parse_mode="Markdown")
                else:
                    await update.message.reply_video(video=open(fn,'rb'), caption="✅ **تفضل، تم التحميل بنجاح!**\n\n@BotKanal24", parse_mode="Markdown")
                os.remove(fn)
                await msg.delete()
                return
    except Exception as e:
        print(e)

    # 2 - طريقة بدون كوكيز
    try:
        sc_match = re.search(r"/p/([^/]+)", url)
        if sc_match:
            shortcode = sc_match.group(1)
            for site in [f"https://ddinstagram.com/p/{shortcode}/", f"https://www.picuki.com/media/{shortcode}"]:
                try:
                    r = requests.get(site, headers={'User-Agent':'Mozilla/5.0'}, timeout=15)
                    v = re.findall(r'https://[^"]+\.mp4[^"]*', r.text)
                    i = re.findall(r'https://[^"]+scontent[^"]+\.jpg[^"]*', r.text)
                    if v:
                        await update.message.reply_video(video=v[0], caption="✅ **تفضل، تم التحميل بنجاح!**\n\n@BotKanal24", parse_mode="Markdown")
                        await msg.delete()
                        return
                    if i:
                        await update.message.reply_photo(photo=i[0], caption="✅ **تفضل، تم التحميل بنجاح!**\n\n@BotKanal24", parse_mode="Markdown")
                        await msg.delete()
                        return
                except:
                    continue
    except Exception as e:
        print(e)

    # رسالة الخطأ الحلوة الجديدة - صلحت كلمة حل
    await msg.edit_text(
        "❌ **عذراً يا غالي، ما قدرت حمل الرابط**\n\n"
        "🔹 تأكد أن الحساب عام وليس خاص\n"
        "🔹 انسخ الرابط القصير فقط بدون إضافات\n"
        "🔹 جرب رابط تيك توك للتأكد أن البوت شغال\n\n"
        "مثال للرابط الصح:\n"
        "`https://www.instagram.com/p/DcoICWsl2Yk/`\n\n"
        "@BotKanal24",
        parse_mode="Markdown"
    )

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
app.run_polling()
