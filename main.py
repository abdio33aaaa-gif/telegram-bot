import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@BotKanal24"
CHANNEL_LINK = "https://t.me/BotKanal24"
ADMIN_ID = 8914058991
ADMIN_NAME = "السيد أحمد العمدة"

users = set()

async def check_sub(update, context):
    try:
        m = await context.bot.get_chat_member(CHANNEL, update.effective_user.id)
        return m.status in ['member','administrator','creator']
    except:
        return False

async def start(update, context):
    users.add(update.effective_user.id)
    if not await check_sub(update, context):
        kb = [[InlineKeyboardButton("اشترك بقناتي ✅", url=CHANNEL_LINK)],
              [InlineKeyboardButton("✅ تحققت من الاشتراك", callback_data="check")]]
        await update.message.reply_text(f"⚠️ اهلا يا {update.effective_user.first_name}!\n\nلازم تشترك بقناتنا {CHANNEL} اولاً حتى تقدر تستخدم البوت", reply_markup=InlineKeyboardMarkup(kb))
        return
    await update.message.reply_text("🚀 أهلا! ابعت رابط الفيديو من تيك توك او انستا او يوتيوب وانا بحملو الك")

async def download(update, context):
    users.add(update.effective_user.id)
    if not await check_sub(update, context):
        await update.message.reply_text(f"❌ اشترك اولاً {CHANNEL} {CHANNEL_LINK}")
        return
    url = update.message.text.strip()
    if not url.startswith("http"): return
    msg = await update.message.reply_text("⏳ عم حمّل ثواني...")
    try:
        ydl_opts = {'outtmpl': 'video.%(ext)s', 'format': 'best[ext=mp4]/best', 'quiet': True, 'noplaylist': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        await update.message.reply_video(video=open(filename, 'rb'), caption=f"تم التحميل ✅\nعبر {CHANNEL}")
        os.remove(filename)
        await msg.delete()
    except Exception as e:
        await msg.edit_text(f"❌ ما قدرت حمّل الفيديو\n{e}")

async def button_check(update, context):
    q = update.callback_query
    await q.answer()
    if await check_sub(update, context):
        await q.edit_message_text("✅ ممتاز! هلا ابعت رابط الفيديو")
    else:
        await q.answer("❌ لسه مو مشترك، اشترك اولاً", show_alert=True)

async def broadcast(update, context):
    if update.effective_user.id != ADMIN_ID: 
        await update.message.reply_text("❌ هاد الامر للمالك فقط")
        return
    if not context.args:
        await update.message.reply_text("طريقة الاستخدام:\n/broadcast رسالتك هنا")
        return
    text = " ".join(context.args)
    c = 0
    await update.message.reply_text(f"⏳ عم ابعت لـ {len(users)} شخص...")
    for uid in users:
        try:
            await context.bot.send_message(uid, f"{text}\n\n— مع تحيات {ADMIN_NAME} ❤️\n{CHANNEL_LINK}")
            c+=1
        except: pass
    await update.message.reply_text(f"✅ تم الارسال لـ {c} شخص بنجاح")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
    app.add_handler(CallbackQueryHandler(button_check))
    app.run_polling()

if __name__ == "__main__":
    main()
