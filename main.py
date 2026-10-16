import os, threading, requests, tempfile, re
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@BotKanal24"
LINK = "https://t.me/BotKanal24"
app = Flask(__name__)
@app.route('/')
def home(): return "Bot V12 OK - TikTok FB Insta"

async def is_sub(bot, uid):
    try:
        m = await bot.get_chat_member(CHANNEL, uid)
        return m.status in ['member','administrator','creator']
    except: return True

def kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("📢 اشترك بالقناة", url=LINK)],[InlineKeyboardButton("✅ تحققت", callback_data="check")]])

WELCOME = "🚀 ارسل رابط تيك توك / فيسبوك / انستا"

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
    sess.headers.update({"User-Agent":"Mozilla/5.0"})
    if "vm.tiktok.com" in tiktok_url or "vt.tiktok.com" in tiktok_url:
        try:
            r = sess.get(tiktok_url, allow_redirects=True, timeout=15)
            tiktok_url = r.url
        except: pass
    try:
        main = sess.get("https://ssstik.io/en", timeout=15)
        tt_match = re.search(r'tt:\s*["\']([^"\']+)["\']', main.text)
        if not tt_match:
            tt_match = re.search(r'name="tt"\s+value="([^"]+)"', main.text)
        tt = tt_match.group(1) if tt_match else ""
        data = {"id": tiktok_url, "locale": "en", "tt": tt}
        res = sess.post("https://ssstik.io/abc?url=dl", data=data, timeout=20)
        m = re.search(r'href="([^"]+)"[^>]*>Without watermark', res.text)
        if not m:
            m = re.search(r'href="([^"]+\.mp4[^"]*)"', res.text)
        if m:
            return m.group(1)
    except Exception as e:
        print(f"ssstik error: {e}")
    return None

async def down(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_sub(context.bot, update.effective_user.id):
        await update.message.reply_text("⚠️ اشترك اولا", reply_markup=kb()); return
    url = update.message.text.strip()
    if "http" not in url: return
    msg = await update.message.reply_text("⚡️ جاري التحميل...")
    await context.bot.send_chat_action(update.effective_chat.id, "upload_video")
    try:
        dl_url = None
        if "tiktok.com" in url:
            dl_url = download_via_ssstik(url)
            if not dl_url:
                raise Exception("ما قدرت جيب رابط التيك توك - جرب رابط طويل جديد")
            with tempfile.TemporaryDirectory() as tmp:
                fp = os.path.join(tmp, "video.mp4")
                with requests.get(dl_url, stream=True, timeout=60) as r:
                    r.raise_for_status()
                    with open(fp, 'wb') as f:
                        for c in r.iter_content(1024*1024):
                            if c: f.write(c)
                await context.bot.delete_message(update.effective_chat.id, msg.message_id)
                with open(fp, 'rb') as f:
                    await update.message.reply_video(f, caption="✅ بدون علامة\n📢 @BotKanal24")
            return
        else:
            # فيسبوك وانستا
            import yt_dlp
            with tempfile.TemporaryDirectory() as tmp:
                opts = {'outtmpl': f'{tmp}/v.%(ext)s','format':'best','quiet':True,'noplaylist':True}
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    path = ydl.prepare_filename(info)
                await context.bot.delete_message(update.effective_chat.id, msg.message_id)
                with open(path,'rb') as f:
                    await update.message.reply_video(f, caption="✅ @BotKanal24")
    except Exception as e:
        print(f"ERROR: {e}")
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
