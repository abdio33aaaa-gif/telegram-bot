import os, json, yt_dlp
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler, filters

TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TOKEN")
CHANNEL = "@BotKanal24"
CHANNEL_LINK = "https://t.me/BotKanal24"
USERS_FILE = "users.json"

users = set()
if os.path.exists(USERS_FILE):
    try:
        users = set(json.load(open(USERS_FILE)))
    except:
        users = set()

def save_users(u):
    json.dump(list(u), open(USERS_FILE, "w"))

async def check_sub(update, context):
    try:
        m = await context.bot.get_chat_member(CHANNEL, update.effective_user.id)
        return m.status in ["member", "administrator", "creator"]
    except:
        return True

async def start(update, context):
    users.add(update.effective_user.id)
    save_users(users)
    kb = [[InlineKeyboardButton("📢 القناة الرسمية", url=CHANNEL_LINK)],
          [InlineKeyboardButton("📖 كيفية الاستخدام", callback_data="help")]]
    await update.message.reply_text(f"🎉 أهلا بك في بوت التحميل الخارق\n\nأرسل أي رابط من تيك توك / انستا / يوتيوب وسأحمله لك صور أو فيديو بدون علامة ✅\n\n{CHANNEL}", reply_markup=InlineKeyboardMarkup(kb))

async def download(update, context):
    users.add(update.effective_user.id)
    save_users(users)
    if not await check_sub(update, context):
        kb = [[InlineKeyboardButton("📢 اشترك بالقناة", url=CHANNEL_LINK)]]
        await update.message.reply_text(f"⚠️ اشترك بالقناة أولاً {CHANNEL_LINK}", reply_markup=InlineKeyboardMarkup(kb))
        return

    url = update.message.text.strip()
    if not url.startswith("http"):
        return

    msg = await update.message.reply_text("⏳ جاري التحميل...")

    try:
        ydl_opts = {
            'outtmpl': '%(id)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'extractor_args': {'instagram': {'api': ['graphql']}},
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                await update.message.reply_photo(photo=open(filename, 'rb'), caption=f"✅ تم التحميل\n{CHANNEL} | @{context.bot.username}")
            else:
                await update.message.reply_video(video=open(filename, 'rb'), caption=f"✅ تم التحميل\n{CHANNEL} | @{context.bot.username}")

            os.remove(filename)
            await msg.delete()

    except Exception as e:
        await msg.edit_text(f"❌ ما قدرت حل الرابط\n{e}")

async def button_check(update, context):
    q = update.callback_query
    await q.answer()
    if q.data == "help":
        await q.edit_message_text(f"📖 أرسل رابط الفيديو أو الصورة فقط والبوت يحملها تلقائياً\n\nيدعم: TikTok, Instagram, YouTube, Facebook, Pinterest\n\n{CHANNEL}")
        return
    if await check_sub(update, context):
        await q.edit_message_text(f"✅ تم التحقق يا بطل!")
    else:
        await q.edit_message_text(f"❌ لسه ما اشتركت")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
app.add_handler(CallbackQueryHandler(button_check))
app.run_polling()
