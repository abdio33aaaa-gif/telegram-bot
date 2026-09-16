import os, re, telebot, yt_dlp

BOT_TOKEN = "8977024211:AAG3OD86xIdCl7t13Oalk_Fy7X8xG1ZAOJs"
bot = telebot.TeleBot(BOT_TOKEN)

def clean_url(text):
    # بيجيب اول رابط من الرسالة وبيشيل?is= و?stkn=
    m = re.search(r'https?://\S+', text)
    if not m: return None
    url = m.group(0)
    url = url.split('?')[0] # اهم سطر - بيشيل كلشي بعد?
    # يصلح روابط youtu.be
    if "youtu.be" in url:
        url = url.split('?')[0]
    return url

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, f"أهلا {m.from_user.first_name} 👋\nابعث رابط عام بدون مشاركة خاصة، وانا بحملو.")

@bot.message_handler(func=lambda m: True)
def handle(m):
    raw_url = m.text
    url = clean_url(raw_url)
    if not url:
        return

    wait = bot.reply_to(m, "⏳ جاري التحميل، ثواني...")
    try:
        ydl_opts = {
            'format': 'mp4/best',
            'outtmpl': 'video.%(ext)s',
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).replace('webm','mp4').replace('mkv','mp4')
            # دور على الملف
            if not os.path.exists(filename):
                for f in os.listdir('.'):
                    if f.startswith('video.'):
                        filename = f
                        break

        with open(filename, 'rb') as f:
            bot.send_video(m.chat.id, f, caption="✅ تفضل تم التحميل\n@BotKanal24")
        os.remove(filename)
        bot.delete_message(m.chat.id, wait.message_id)
    except Exception as e:
        print(e)
        bot.edit_message_text("❌ الرابط خاص (فيه stkn او is) أو محمي. جرب تنسخ الرابط من المتصفح مباشرة، مو من زر المشاركة.\nمثال رابط صحيح:\nhttps://www.tiktok.com/@user/video/123..\nhttps://www.instagram.com/reel/ABC123/", m.chat.id, wait.message_id)

bot.infinity_polling()
