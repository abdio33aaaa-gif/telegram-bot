import os, asyncio, threading, tempfile, requests
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@BotKanal24"
LINK = "https://t.me/BotKanal24"
app = Flask(__name__)
@app.route('/')
def home(): return "Bot OK"

async def is_sub(bot, uid):
    try:
        m = await bot.get_chat_member(CHANNEL, uid)
        return m.status in ['member','administrator','creator']
    except: return True

def kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("📢 اشترك بالقناة", url=LINK)],[InlineKeyboardButton("✅ تحققت", callback_data="check")]])

WELCOME = "🚀 بوت التحميل السريع 2026\n\n⚡️ يحمل من:\n- TikTok بدون علامة\n- Instagram Reels & Story\n- Facebook\n- YouTube MP4/MP3\n\n📎 ارسل الرابط الآن ليبدأ التحميل\n\n👨‍💻 @BotKanal24"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_sub(context.bot, update.effective_user.id):
        await update.message.reply_text("⚠️ اشترك اولا", reply_markup=kb())
        return
    await update.message.reply_text(WELCOME)

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if await is_sub(context.bot, q.from_user.id):
        await q.edit_message_text("✅ تم التفعيل!")
        await context.bot.send_message(q.from_user.id, WELCOME)
    else:
        await q.answer("❌ لسه ما اشتركت", show_alert=True)

def download_tiktok_api(tiktok_url):
    """يجرب يحمل من API خارجي"""
    try:
        # حل رابط vm
        if "vm.tiktok" in tiktok_url or "vt.tiktok" in tiktok_url:
            r = requests.get(tiktok_url, allow_redirects=True, timeout=10, headers={"User-Agent":"Mozilla/5.0"})
            tiktok_url = r.url
        
        # جرب tikwm API
        api = requests.post(
            "https://www.tikwm.com/api/",
            data={"url": tiktok_url, "count": 12, "cursor": 0, "web": 1, "hd": 1},
            headers={"User-Agent":"Mozilla/5.0", "Referer":"https://www.tikwm.com/"},
            timeout=15
        )
        data = api.json()
        if data.get("code") == 0 and data["data"].get("play"):
            return data["data"]["play"]
    except Exception as e:
        print(f"TikWM fail: {e}")
    return None

async def down(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_sub(context.bot, update.effective_user.id):
        await update.message.reply_text("⚠️ اشترك اولا", reply_markup=kb())
        return
    url = update.message.text.strip()
    if "http" not in url: return
    msg = await update.message.reply_text("⚡️ ثانية...")
    
    # هاي يلي بترجعلك "يرسل مقطعاً مرئياً"
    await context.bot.send_chat_action(update.effective_chat.id, "upload_video")

    async def keep_typing():
        while True:
            try:
                await context.bot.send_chat_action(update.effective_chat.id, "upload_video")
                await asyncio.sleep(3)
            except: break
    task = asyncio.create_task(keep_typing())

    file_path = None
    try:
        with tempfile.TemporaryDirectory() as tmp:
            final_path = None
            
            # اذا تيك توك جرب API أول
            if "tiktok.com" in url:
                direct_url = download_tiktok_api(url)
                if direct_url:
                    print(f"Got direct URL: {direct_url}")
                    final_path = tmp + "/video.mp4"
                    r = requests.get(direct_url, headers={"User-Agent":"Mozilla/5.0"}, timeout=30)
                    open(final_path, 'wb').write(r.content)
            
            # اذا مو تيك توك او فشل الـ API جرب yt-dlp
            if not final_path or not os.path.exists(final_path):
                print("Trying yt-dlp...")
                opts = {'outtmpl': tmp + '/video.%(ext)s','format':'best[ext=mp4]/best','quiet':True,'noplaylist':True}
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    final_path = ydl.prepare_filename(info)
            
            task.cancel()
            try: await context.bot.delete_message(update.effective_chat.id, msg.message_id)
            except: pass
            
            await context.bot.send_chat_action(update.effective_chat.id, "upload_video")
            with open(final_path, 'rb') as f:
                await update.message.reply_video(f, caption="✅ بدون علامة\n📢 @BotKanal24")

    except Exception as e:
        task.cancel()
        print(f"ERROR FINAL: {e}")
        try:
            await context.bot.edit_message_text(update.effective_chat.id, msg.message_id, f"❌ ما قدرت حملو\nالسبب: {str(e)[:100]}")
        except: pass

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

threading.Thread(target=run_flask, daemon=True).start()

if not TOKEN:
    print("BOT_TOKEN MISSING!")

application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(check, pattern="check"))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, down))
application.run_polling(drop_pending_updates=True)
