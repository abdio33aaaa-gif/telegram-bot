import os, asyncio, threading, tempfile, requests
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")
print(f"TOKEN FOUND: {bool(TOKEN)}")

CHANNEL = "@BotKanal24"
LINK = "https://t.me/BotKanal24"

app = Flask(__name__)
@app.route('/')
def home(): return "Bot OK - Live"

async def is_sub(bot, uid):
    try:
        m = await bot.get_chat_member(CHANNEL, uid)
        return m.status in ['member','administrator','creator']
    except: return True

def kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("اشترك بالقناة", url=LINK)],[InlineKeyboardButton("تحققت", callback_data="check")]])

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

async def down(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_sub(context.bot, update.effective_user.id):
        await update.message.reply_text("⚠️ اشترك اولا", reply_markup=kb())
        return
    url = update.message.text.strip()
    if "http" not in url: return
    msg = await update.message.reply_text("⚡️ ثانية...")
    await context.bot.send_chat_action(update.effective_chat.id, "upload_video")
    try:
        if "vm.tiktok" in url or "vt.tiktok" in url:
            try:
                r = requests.get(url, allow_redirects=True, timeout=10, headers={"User-Agent":"Mozilla/5.0"})
                url = r.url
            except: pass
        async def typing():
            while True:
                try:
                    await context.bot.send_chat_action(update.effective_chat.id, "upload_video")
                    await asyncio.sleep(4)
                except: break
        task = asyncio.create_task(typing())
        with tempfile.TemporaryDirectory() as tmp:
            opts = {'outtmpl': tmp + '/v.%(ext)s','format':'best[ext=mp4]/best','quiet':True,'noplaylist':True}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                path = ydl.prepare_filename(info)
        task.cancel()
        try: await context.bot.delete_message(update.effective_chat.id, msg.message_id)
        except: pass
        await context.bot.send_chat_action(update.effective_chat.id, "upload_video")
        with open(path, 'rb') as f:
            await update.message.reply_video(f, caption="✅ @BotKanal24")
    except Exception as e:
        print(f"Download error: {e}")
        try: await context.bot.edit_message_text(update.effective_chat.id, msg.message_id, "❌ ما قدرت حملو")
        except: pass

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    if not TOKEN:
        print("ERROR: BOT_TOKEN is missing in Render Environment!")
    threading.Thread(target=run_flask, daemon=True).start()
    print("Starting bot...")
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(check, pattern="check"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, down))
    application.run_polling(drop_pending_updates=True)
