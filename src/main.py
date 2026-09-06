import os
from pyrogram import Client, filters

app = Client(
    "my_bot",
    api_id=int(os.environ.get("API_ID", 0)),
    api_hash=os.environ.get("API_HASH", ""),
    bot_token=os.environ.get("BOT_TOKEN", "")
)

@app.on_message(filters.command("start"))
def start(client, message):
    message.reply_text("أهلاً بك! البوت يعمل بنجاح الآن.")

if __name__ == "__main__":
    print("البوت يعمل الآن...")
    app.run()
