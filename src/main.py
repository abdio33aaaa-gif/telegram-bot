import os
import asyncio
from pyrogram import Client, filters

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

app = Client(
    "my_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("أهلاً بك! البوت يعمل بنجاح الآن.")

if __name__ == "__main__":
    print("جاري تشغيل البوت...")
    app.start()
    print("البوت يعمل بنجاح ويمكنه استقبال الرسائل.")
    asyncio.idle()
