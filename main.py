import os, asyncio, threading, tempfile, requests, json
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@BotKanal24"
LINK = "https://t.me/BotKanal24"

app = Flask(__name__)
@app.route('/')
def home(): return "Bot Running - V7 TikWM"

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
        await update.message.reply_text("⚠️ اشترك اولا", reply_markup=kb()); return
    await update.message.reply_text(WELCOME)

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if await is_sub(context.bot, q.from_user.id):
        await q.edit_message_text("✅ تم التفعيل!")
        await context.bot.send_message(q.from_user.id, WELCOME)
    else: await q.answer("❌ لسه ما اشتركت", show_alert=True)

async def down(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_sub(context.bot, update.effective_user.id):
        await update.message.reply_text("⚠️ اشترك اولا", reply_markup=kb()); return
    url = update.message.text.strip()
    if "http" not in url: return

    msg = await update.message.reply_text("⚡️ ثانية... بجيب الرابط")
    await context.bot.send_chat_action(update.effective_chat.id, "upload_video")

    async def keep_typing():
        while True:
            try:
                await context.bot.send_chat_action(update.effective_chat.id, "upload_video")
                await asyncio.sleep(3)
            except: break
    task = asyncio.create_task(keep_typing())

    try:
        with tempfile.TemporaryDirectory() as tmp:
            video_file = None

            # --- للتيك توك: استخدم tikwm API (شغال مع vm.tiktok) ---
            if "tiktok.com" in url:
                try:
                    # فك رابط vm
                    if "vm.tiktok.com" in url or "vt.tiktok.com" in url:
                        try:
                            r = requests.get(url, allow_redirects=True, timeout=10, headers={"User-Agent":"Mozilla/5.0"})
                            url = r.url
                        except: pass

                    print(f"Trying tikwm for {url}")
                    api_res = requests.post(
                        "https://www.tikwm.com/api/",
                        data={"url": url, "count": 12, "cursor": 0, "web": 1, "hd": 1},
                        headers={"User-Agent":"Mozilla/5.0","Referer":"https://www.tikwm.com/"},
                        timeout=20
                    )
                    j = api_res.json()
                    print(j)
                    if j.get("code") == 0 and j.get("data") and j["data"].get("play"):
                        direct = j["data"]["play"]
                        # احيانا بيرجع بدون https
                        if direct.startswith("//"): direct = "https:" + direct
                        video_file = os.path.join(tmp, "tt.mp4")
                        vd = requests.get(direct, headers={"User-Agent":"Mozilla/5.0"}, timeout=40, stream=True)
                        with open(video_file, 'wb') as f:
                            for chunk in vd.iter_content(1024*1024):
                                f.write(chunk)
                        print("TikWM success")
                    else:
                        print(f"TikWM fail response: {j}")
                except Exception as e:
                    print(f"TikWM exception: {e}")

            # --- اذا مو تيك توك او فشل API جرب yt-dlp ---
            if not video_file or not os.path.exists(video_file) or os.path.getsize(video_file) < 10000:
                print("Fallback to yt-dlp")
                opts = {'outtmpl': os.path.join(tmp, 'video.%(ext)s'), 'format': 'best[ext=mp4]/best', 'quiet': True, 'noplaylist': True, 'no_warnings': True}
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    video_file = ydl.prepare_filename(info)

            task.cancel()
            try: await context.bot.delete_message(update.effective_chat.id, msg.message_id)
            except: pass

            await context.bot.send_chat_action(update.effective_chat.id, "upload_video")
            with open(video_file, 'rb') as f:
                await update.message.reply_video(f, caption="✅ بدون علامة\n📢 @BotKanal24")

    except Exception as e:
        task.cancel()
        print(f"FINAL ERROR: {e}")
        try:
            await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=msg.message_id, text=f"❌ فشل التحميل\nالسبب: {e}\n\nجرب رابط تاني طويل مو vm")
        except: pass

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

threading.Thread(target=run_flask, daemon=True).start()
if not TOKEN: print("BOT_TOKEN MISSING!")
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(check, pattern="check"))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, down))
application.run_polling(drop_pending_updates=True)
