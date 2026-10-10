import os, threading, requests, tempfile, json
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@BotKanal24"
LINK = "https://t.me/BotKanal24"
app = Flask(__name__)
@app.route('/')
def home(): return "Bot V10 Cobalt OK"

async def is_sub(bot, uid):
    try:
        m = await bot.get_chat_member(CHANNEL, uid)
        return m.status in ['member','administrator','creator']
    except: return True

def kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("📢 اشترك بالقناة", url=LINK)],[InlineKeyboardButton("✅ تحققت", callback_data="check")]])

WELCOME = "🚀 بوت التحميل السريع 2026\n\n- TikTok بدون علامة\n- Instagram\n- Facebook\n- YouTube\n\n📎 ارسل الرابط الآن\n\n👨‍💻 @BotKanal24"

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

def get_tiktok_video_url(url):
    # فك رابط vm
    if "vm.tiktok.com" in url or "vt.tiktok.com" in url:
        try:
            r = requests.get(url, allow_redirects=True, timeout=15, headers={"User-Agent":"Mozilla/5.0"})
            url = r.url
        except: pass
    
    # محاولة 1: tikwm
    try:
        print(f"Trying tikwm: {url}")
        r = requests.post("https://www.tikwm.com/api/", data={"url": url, "hd": 1}, headers={"User-Agent":"Mozilla/5.0"}, timeout=15)
        print(r.text[:500])
        j = r.json()
        if j.get("code") == 0 and j.get("data", {}).get("play"):
            play = j["data"]["play"]
            if play.startswith("//"): play = "https:" + play
            return play, j["data"].get("title","")
    except Exception as e:
        print(f"tikwm fail: {e}")

    # محاولة 2: cobalt.tools - هاد يلي رح يشتغل
    try:
        print(f"Trying cobalt: {url}")
        r = requests.post("https://api.cobalt.tools/", json={"url": url}, headers={"Accept":"application/json","Content-Type":"application/json"}, timeout=20)
        print(f"cobalt response: {r.text[:500]}")
        j = r.json()
        if j.get("url"):
            return j["url"], ""
    except Exception as e:
        print(f"cobalt fail: {e}")

    return None, None

async def down(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_sub(context.bot, update.effective_user.id):
        await update.message.reply_text("⚠️ اشترك اولا", reply_markup=kb()); return
    url = update.message.text.strip()
    if "http" not in url: return

    msg = await update.message.reply_text("⚡️ ثانية...")
    await context.bot.send_chat_action(update.effective_chat.id, "upload_video")

    try:
        if "tiktok.com" in url:
            play_url, title = get_tiktok_video_url(url)
            if not play_url:
                raise Exception("ما قدرت جيب الرابط - جرب رابط تيك توك جديد طويل")

            with tempfile.TemporaryDirectory() as tmp:
                file_path = os.path.join(tmp, "video.mp4")
                print(f"Downloading {play_url}")
                with requests.get(play_url, stream=True, timeout=60, headers={"User-Agent":"Mozilla/5.0"}) as r:
                    r.raise_for_status()
                    with open(file_path, 'wb') as f:
                        for chunk in r.iter_content(1024*1024):
                            if chunk: f.write(chunk)
                
                try: await context.bot.delete_message(update.effective_chat.id, msg.message_id)
                except: pass
                
                await context.bot.send_chat_action(update.effective_chat.id, "upload_video")
                with open(file_path, 'rb') as f:
                    await update.message.reply_video(f, caption=f"✅ بدون علامة\n{title[:100]}\n📢 @BotKanal24")
            return

        # غير تيك توك
        import yt_dlp
        with tempfile.TemporaryDirectory() as tmp:
            opts = {'outtmpl': f'{tmp}/v.%(ext)s','format':'best[ext=mp4]/best','quiet':True,'noplaylist':True}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                path = ydl.prepare_filename(info)
            await context.bot.delete_message(update.effective_chat.id, msg.message_id)
            with open(path,'rb') as f:
                await update.message.reply_video(f, caption="✅ @BotKanal24")

    except Exception as e:
        print(f"FINAL ERROR: {e}")
        try:
            await context.bot.edit_message_text(update.effective_chat.id, msg.message_id, f"❌ فشل: {e}")
        except:
            await update.message.reply_text(f"❌ {e}")

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

threading.Thread(target=run_flask, daemon=True).start()
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(check, pattern="check"))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, down))
application.run_polling(drop_pending_updates=True)
