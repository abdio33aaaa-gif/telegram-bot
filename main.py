import os, requests, telebot

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda m: True)
def all(message):
    url = message.text
    if "tiktok.com" in url:
        try:
            data = requests.post("https://www.tikwm.com/api/", json={"url": url}).json()
            video = data["data"]["play"]
            bot.send_video(message.chat.id, video)
        except:
            bot.reply_to(message, "ما قدرت اجيبه")

bot.infinity_polling()
