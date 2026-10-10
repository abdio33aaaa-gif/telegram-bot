import os, threading, requests, tempfile
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@BotKanal24"
LINK = "https://t.me/BotKanal24"

app = Flask(__name__)
@app.route('/')
def home(): return "Bot V9 - TikTok Fixed"

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

async def down(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_sub(context.bot, update.effective_user.id):
        await update.message.reply_text("⚠️ اشترك اولا", reply_markup=kb()); return
    url = update.message.text.strip()
    if "http" not in url: return

    msg = await update.message.reply_text("⚡️ ثانية...")
    await context.bot.send_chat_action(update.effective_chat.id, "upload_video")

    try:
        # --- تيك توك: فقط tikwm بدون yt-dlp ---
        if "tiktok.com" in url:
            # 1. فك رابط vm
            original_url = url
            if "vm.tiktok.com" in url or "vt.tiktok.com" in url:
                try:
                    r = requests.get(url, allow_redirects=True, timeout=15, headers={"User-Agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)"})
                    url = r.url
                    print(f"Expanded {original_url} -> {url}")
                except Exception as e:
                    print(f"Expand fail: {e}")

            # 2. جيب رابط التحميل من tikwm
            print(f"Calling tikwm for {url}")
            resp = requests.post(
                "https://www.tikwm.com/api/",
                data={"url": url, "count": 12, "cursor": 0, "web": 1, "hd": 1},
                headers={"User-Agent":"Mozilla/5.0", "Referer":"https://www.tikwm.com/"},
                timeout=20
            )
            data = resp.json()
            print(f"TikWM response: {data}")

            if data.get("code") != 0 or not data.get("data", {}).get("play"):
                raise Exception(f"TikTok API رفض الرابط: {data.get('msg','unknown')} - جرب رابط جديد")

            play_url = data["data"]["play"]
            title = data["data"].get("title","")
            if play_url.startswith("//"): play_url = "https:" + play_url

            # 3. حمّل الفيديو من سيرفر tikwm (مو سيرفر تيك توك المحظور)
            print(f"Downloading video from {play_url}")
            with tempfile.TemporaryDirectory() as tmp:
                file_path = os.path.join(tmp, "video.mp4")
                with requests.get(play_url, stream=True, timeout=40, headers={"User-Agent":"Mozilla/5.0"}) as r:
                    r.raise_for_status()
                    with open(file_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=1024*1024):
                            if chunk: f.write(chunk)
                
                await context.bot.delete_message(update.effective_chat.id, msg.message_id)
                await context.bot.send_chat_action(update.effective_chat.id, "upload_video")
                with open(file_path, 'rb') as f:
                    await update.message.reply_video(video=f, caption=f"✅ بدون علامة\n{title[:100]}\n📢 @BotKanal24")
            return

        # --- غير تيك توك: يوتيوب انستا ---
        import yt_dlp
        with tempfile.TemporaryDirectory() as tmp:
            opts = {'outtmpl': f'{tmp}/v.%(ext)s','format':'best[ext=mp4]/best','quiet':True,'noplaylist':True}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                path = ydl.prepare_filename(info)
            await context.bot.delete_message(update.effective_chat.id, msg.message_id)
            await context.bot.send_chat_action(update.effective_chat.id, "upload_video")
            with open(path,'rb') as f:
                await update.message.reply_video(f, caption="✅ @BotKanal24")

    except Exception as e:
        print(f"FINAL ERROR: {e}")
        try:
            await context.bot.edit_message_text(update.effective_chat.id, msg.message_id, f"❌ فشل: {e}\n\nملاحظة: روابط vm بتنتهي، افتح تيك توك وانسخ رابط جديد من زر المشاركة > نسخ الرابط")
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
