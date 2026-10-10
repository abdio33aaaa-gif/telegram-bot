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
    return InlineKeyboardMarkup([[InlineKeyboardButton("اشترك بالقناة", url=LINK)],[InlineKeyboardButton("تحققت", callback_data="check")]])

WELCOME = "🚀 بوت التحميل السريع 2026\n\n⚡️ يحمل من:\n- TikTok بدون علامة\n- Instagram Reels & Story\n- Facebook\n- YouTube MP4/MP3\n\n📎 ارسل الرابط الآن ليبدأ التحميل\n\n👨‍💻 @BotKanal24"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_sub(context.bot, update.effective_user.id):
        await update.message.reply_text("⚠️ اشترك اولا", reply_markup=kb())
        return
    await update.message.reply_text(WELCOME)

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
   
