import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@BotKanal24"
CHANNEL_LINK = "https://t.me/BotKanal24"

async def check_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(CHANNEL, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
    except Exception:
        pass
    return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_sub(update, context):
        keyboard = [
            [InlineKeyboardButton("اشترك بقناتي ✅", url=CHANNEL_LINK)],
            [InlineKeyboardButton("✅ تحققت اشتركت", callback_data="check")]
        ]
        await update.message.reply_text(
            f"⚠️ حتى تستخدم البوت لازم تشترك بقناتنا اولاً\n\n👉 {CHANNEL}\n\nاشترك وارجع اضغط تحققت",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    await update.message.reply_text("أهلاً! 🚀\nابعتلي رابط من تيك توك - انستا - فيسبوك - يوتيوب")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_sub(update, context):
        keyboard = [[InlineKeyboardButton("اشترك بقناتي ✅", url=CHANNEL_LINK)]]
        await update.message.reply_text(f"❌ لازم تشترك بقناتنا {CHANNEL} حتى تحمل", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    url = update.message.text.strip()
    if not url.startswith("http"):
        return
    
    msg = await update.message.reply_text("⏳ عم حمّل... ثواني")

    ydl_opts = {
        'outtmpl': 'video.%(ext)s',
        'format': 'best[ext=mp4]/best',
        'noplaylist': True,
        'quiet': True,
        'nocheckcertificate': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        
        await update.message.reply_video(video=open(filename, 'rb'), caption=f"تم التحميل ✅\nعبر {CHANNEL}")
        os.remove(filename)
        await msg.delete()
    except Exception as e:
        await update.message.reply_text(f"❌ ما قدرت حمّل\n{e}")

async def button_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if await check_sub(update, context):
        await query.edit_message_text("✅ ممتاز تم الاشتراك! هلا ابعت رابط الفيديو")
    else:
        await query.answer("❌ لساتك مو مشترك بالقناة", show_alert=True)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
    app.add_handler(CallbackQueryHandler(button_check))
    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
