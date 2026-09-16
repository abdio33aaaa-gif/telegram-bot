import os, json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@BotKanal24"
CHANNEL_LINK = "https://t.me/BotKanal24"
ADMIN_ID = 8914058991
ADMIN_NAME = "السيد أحمد"
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        try: return set(json.load(open(USERS_FILE)))
        except: return set()
    return set()

def save_users(users):
    json.dump(list(users), open(USERS_FILE, "w"))

users = load_users()

async def check_sub(update, context):
    try:
        m = await context.bot.get_chat_member(CHANNEL, update.effective_user.id)
        return m.status in ['member','administrator','creator']
    except: return False

async def start(update, context):
    users.add(update.effective_user.id)
    save_users(users)
    if not await check_sub(update, context):
        kb = [[InlineKeyboardButton("📢 اشترك بقناتنا ✅", url=CHANNEL_LINK)],
              [InlineKeyboardButton("✅ تحققت من الاشتراك", callback_data="check")]]
        await update.message.reply_text(f"👋 أهلا يا {update.effective_user.first_name}!\n\n⚠️ لازم تشترك بقناتنا {CHANNEL} عشان تستخدم البوت\n\nبعد الاشتراك اضغط تحققت 👇", reply_markup=InlineKeyboardMarkup(kb))
        return
    kb = [[InlineKeyboardButton("📢 قناتنا الرسمية", url=CHANNEL_LINK)],
          [InlineKeyboardButton("📖 طريقة الاستخدام", callback_data="help")]]
    await update.message.reply_text(f"🎉 أهلا يا {update.effective_user.first_name}!\n\n🚀 مرحبا بك في بوت التحميل الخارق\n\n✅ انت الآن مشترك ويمكنك التحميل مباشرة!\n\n📌 أرسل لي رابط من:\n• تيك توك (بدون علامة)\n• انستغرام - ريلز وستوري\n• فيسبوك\n• يوتيوب\n\nوسأحمله لك بثواني ⚡\n\n👨‍💻 المطور: {ADMIN_NAME}", reply_markup=InlineKeyboardMarkup(kb))

async def download(update, context):
    users.add(update.effective_user.id)
    save_users(users)
    if not await check_sub(update, context):
        kb = [[InlineKeyboardButton("📢 اشترك بقناتنا ✅", url=CHANNEL_LINK)]]
        await update.message.reply_text(f"⚠️ اشترك بقناتنا أولاً {CHANNEL}", reply_markup=InlineKeyboardMarkup(kb))
        return
    url = update.message.text.strip()
    if not url.startswith("http"): return
    msg = await update.message.reply_text("⏳ جاري التحميل...")
    try:
        ydl_opts = {'outtmpl': 'video.%(ext)s', 'format': 'best'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        await update.message.reply_video(video=open(filename, 'rb'))
        os.remove(filename)
        await msg.delete()
    except Exception as e:
        await msg.edit_text(f"❌ ما قدرت حمل: {e}")

async def button_check(update, context):
    q = update.callback_query
    await q.answer()
    if q.data == "help":
        await q.edit_message_text(f"📖 طريقة الاستخدام:\n\n1️⃣ انسخ رابط الفيديو\n2️⃣ الصقه هنا\n3️⃣ انتظر ثواني\n\n💡 لازم الفيديو يكون عام\n\n📢 قناتنا: {CHANNEL_LINK}")
        return
    if await check_sub(update, context):
        await q.edit_message_text(f"✅ ممتاز يا {q.from_user.first_name}!\nيمكنك الآن ارسال أي رابط للتحميل 🚀")
    else:
        await q.answer("❌ لسه مو مشترك، اشترك أولاً", show_alert=True)

async def broadcast(update, context):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args:
        await update.message.reply_text("استخدم: /broadcast رسالتك")
        return
    text = " ".join(context.args)
    c=0
    await update.message.reply_text(f"⏳ جاري الاذاعة لـ {len(users)} مشترك...")
    for uid in users:
        try:
            await context.bot.send_message(uid, text)
            c+=1
        except: pass
    await update.message.reply_text(f"✅ تم الارسال لـ {c} شخص")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
    app.add_handler(CallbackQueryHandler(button_check))
    app.run_polling()

if __name__ == "__main__":
    main()
