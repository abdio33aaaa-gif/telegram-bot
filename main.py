import os, threading, requests, tempfile, re
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@BotKanal24"
LINK = "https://t.me/BotKanal24"
app = Flask(__name__)
@app.route('/')
def home(): return "Bot V11 SSSTik OK"

async def is_sub(bot, uid):
    try:
        m = await bot.get_chat_member(CHANNEL, uid)
        return m.status in ['member','administrator','creator']
    except: return True

def kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("📢 اشترك بالقناة", url=LINK)],[InlineKeyboardButton("✅ تحققت", callback_data="check")]])

WELCOME = "🚀 بوت التحميل السريع 2026\n\n- TikTok بدون علامة\n- Instagram\n- Facebook\n- YouTube\n\n📎 ارسل الرابط الآن"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_sub(context.bot, update.effective_user.id):
        await update.message.reply_text("⚠️ اشترك اولا", reply_markup=kb()); return
    await update.message.reply_text(WELCOME)

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if await is_sub(context.bot, q.from_user.id):
        await q.edit_message_text("✅ تم التفعيل!")
        await context.bot.send_message(q.from_user.id, WELCOME)
    else: await q.answer("❌ لسه ما اشتركت", show_alert=True)

def download_via_ssstik(tiktok_url):
    sess = requests.Session()
    sess.headers.update({"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
    # 1. فك vm
    if "vm.tiktok.com" in tiktok_url or "vt.tiktok.com" in tiktok_url:
        try:
            r = sess.get(tiktok_url, allow_redirects=True, timeout=15)
            tiktok_url = r.url
        except: pass
    print(f"SSSTik for {tiktok_url}")
    # 2. جيب صفحة ssstik وخد tt token
    try:
        main = sess.get("https://ssstik.io/en", timeout=15)
        tt_match = re.search(r'tt:\s*["\']([^"\']+)["\']', main.text)
        if not tt_match:
            tt_match = re.search(r'name="tt"\s+value="([^"]+)"', main.text)
        tt = tt_match.group(1) if tt_match else ""
        print(f"tt token: {tt[:20]}")
        # 3. ابعت رابط التحميل
        data = {"id": tiktok_url, "locale": "en", "tt": tt}
        res = sess.post("https://ssstik.io/abc?url=dl", data=data, timeout=20)
        print(res.text[:1000])
        # 4. طلع رابط بدون علامة
        m = re.search(r'href="([^"]+)"[^>]*>Without watermark', res.text)
        if not m:
            m = re.search(r'href="([^"]+\.mp4[^"]*)"', res.text)
        if m:
            dl_url = m.group(1)
            print(f"Found dl_url: {dl_url}")
            return dl_url
    except Exception as e:
        print(f"ssstik error: {e}")
    return None

async def down(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_sub(context.bot, update.effective_user.id):
        await update.message.reply_text("⚠️ اشترك اولا", reply_markup=kb()); return
    url = update.message.text.strip()
    if "http" not in url: return
    msg = await update.message.reply_text("⚡️ ثانية...")
    await context.bot.send_chat_action(update.effective_chat.id, "upload_video")
    try:
        if "tiktok.com" in url:
            dl_url = download_via_ssstik(url)
            if not dl_url:
                raise Exception("ssstik ما رجع رابط - جرب رابط تيك توك جديد من زر مشاركة > نسخ الرابط")
            with tempfile.TemporaryDirectory() as tmp:
                fp = os.path.join(tmp, "video.mp4")
                with requests.get(dl_url, stream=True, timeout=60, headers={"User-Agent":"Mozilla/5.0"}) as r:
                    r.raise_for_status()
                    with open(fp, 'wb') as f:
                        for c in r.iter_content(1024*1024):
                            if c: f.write(c)
                try: await context.bot.delete_message(update.effective_chat.id, msg.message_id)
                except: pass
                await context.bot.send_chat_action(update.effective_chat.id, "upload_video")
                with open(fp, 'rb') as f:
                    await update.message.reply_video(f, caption="✅ بدون علامة\n📢 @BotKanal24")
            return
        # يوتيوب وانستا
        import yt_dlp
        with tempfile.TemporaryDirectory() as tmp:
            opts = {'outtmpl': f'{tmp}/v.%(ext)s','format':'best[ext=mp4]/best','quiet':True}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                path = ydl.prepare_filename(info)
            await context.bot.delete_message(update.effective_chat.id, msg.message_id)
            with open(path,'rb') as f:
                await update.message.reply_video(f, caption="✅ @BotKanal24")
    except Exception as e:
        print(f"FINAL ERROR: {e}")
        try: await context.bot.edit_message_text(update.effective_chat.id, msg.message_id, f"❌ {e}")
        except: await update.message.reply_text(f"❌ {e}")

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

threading.Thread(target=run_flask, daemon=True).start()
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(check, pattern="check"))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, down))
application.run_polling(drop_pending_updates=True)
