import os, sys
from flask import Flask
from threading import Thread
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_USERNAME = "BotKanal24"
CHANNEL_LINK = f"https://t.me/{CHANNEL_USERNAME}"

print(f"TOKEN FOUND: {bool(BOT_TOKEN)}", flush=True)
if BOT_TOKEN:
    print(f"TOKEN STARTS WITH: {BOT_TOKEN[:10]}...", flush=True)

app = Flask('')
@app.route('/')
def home(): return "Bot is Alive! Go to Telegram"
def run():
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting Flask on {port}", flush=True)
    app.run(host='0.0.0.0', port=port)
def keep_alive():
    Thread(target=run).start()

# ... نفس دوال start و check_callback و downloader تبعك خليها ...

if __name__ == '__main__':
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN NOT SET!", flush=True)
        keep_alive()
        while True: pass
    else:
        print("Starting bot polling...", flush=True)
        keep_alive()
        try:
            bot = ApplicationBuilder().token(BOT_TOKEN).build()
            # ضيف الهاندلرز تبعك هون
            bot.add_handler(CommandHandler("start", start))
            bot.add_handler(CallbackQueryHandler(check_callback))
            bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, downloader))
            print("Bot handlers added, polling...", flush=True)
            bot.run_polling()
        except Exception as e:
            print(f"CRITICAL BOT ERROR: {e}", flush=True)
            import traceback
            traceback.print_exc()
