import telebot

TOKEN = "8911586038:AAEJPLNv8dVdgKZL0..."  # حط توكنك الكامل هون
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "اهلا! ابعتلي رابط تيك توك او انستا او فيسبوك")

@bot.message_handler(func=lambda m: True)
def handle(m):
    url = m.text.strip()
    if "tiktok.com" in url or "vm.tiktok.com" in url or "instagram.com" in url or "facebook.com" in url or "youtu" in url:
        bot.reply_to(m, "جاري التحميل... ⏳")
        # هون كان كود التحميل تبعك القديم - اذا عندك كود ytdl قديم رجعه هون
        # اذا ما عندك، هذا يخلي البوت يرد بس
        try:
            # مثال بسيط: اذا تيك توك استخدم tikwm مباشرة
            import requests
            api = requests.post("https://www.tikwm.com/api/",
                data={"url": url, "count": 12, "cursor": 0, "web": 1, "hd": 1},
                headers={'User-Agent': 'Mozilla/5.0'}, timeout=20).json()
            if api.get("code") == 0:
                video_url = api["data"].get("play")
                bot.send_message(m.chat.id, f"رابط التحميل: {video_url}")
            else:
                bot.reply_to(m, "ما قدرت اجيب الفيديو")
        except Exception as e:
            bot.reply_to(m, f"خطأ: {e}")
    else:
        bot.reply_to(m, "ابعت رابط صحيح")

print("Bot is running...")
bot.infinity_polling()
