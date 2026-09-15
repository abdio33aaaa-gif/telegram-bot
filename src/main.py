import os
import asyncio
from pyrogram import Client, filters

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

app = Client(
    "my_bot",
    api_id=int(os.environ.get("API_ID")),
    api_hash=os.environ.get("API_HASH"),
    bot_token=os.environ.get("BOT_TOKEN")
)

@app.on_message(filters.command("start"))
def start(client, message):
    message.reply_text("البوت يعمل بنجاح الآن 😍")

if __name__ == "__main__":
    print("البوت يعمل الآن...")
    app.run()
