import os
import asyncio
import threading
import tempfile
import requests
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@BotKanal24"
CHANNEL_LINK = "https://t.me/BotKanal24"

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot OK - 61 Users"

async def is_subscribed(bot, user_id):
    try:
        m = await bot.get_chat_member(CHANNEL, user_id)
        return m.status in ['member','administrator','creator']
    except:
        return True

def get_sub_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 اشترك بالقناة", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ تحققت", callback_data="check_sub")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_subscribed(context.bot, update.effective_user.id):
        await update.message.reply_text("⚠️ يجب الاشتراك بالقناة أولاً", reply_markup=get_sub_keyboard())
        return
    await update.message.reply_text(
        "🚀 بوت التحميل السريع 2026\n\n"
        "⚡️ يحمل من:\n"
        "- TikTok بدون علامة\n"
        "- Instagram Reels & Story\n"
        "- Facebook\n"
        "- YouTube MP4/MP3\n\n"
        "📎 أرسل الرابط الآن ليبدأ التحميل\n\n"
        "👨‍💻 @BotKanal24"
    )

async def check_sub_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if await is_subscribed(context.bot, query.from_user.id):
        await query.edit_message_text("✅ تم التفعيل!")
        await context.bot.send_message(chat_id=query.from_user.id, text="📎 أرسل الرابط الآن")
    else:
        await query.answer("❌ لسه ما اشتركت", show_alert=True)

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_subscribed(context.bot, update.effective_user.id):
        await update.message.reply_text("⚠️ اشترك أولاً", reply_markup=get_sub_keyboard())
        return

    url = update.message.text.strip()
    if "http" not in url:
        return

    msg = await update.message.reply_text("⚡️ ثانية...")

    try:
        # هاد يلي بيرجعلك "يرسل مقطعاً مرئياً"
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="upload_video")

        if "vm.tiktok.com" in url or "vt.tiktok.com" in url:
            try:
                r = requests.get(url, allow_redirects=True, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                url = r.url
            except:
                pass

        async def keep_typing():
            while True:
                try:
                    await context.bot.send_chat_action(update.effective_chat.id, "
