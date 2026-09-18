import telebot, threading, os, re, glob, shutil, time
from telebot import types
import yt_dlp
import instaloader

TOKEN1 = os.getenv("BOT_TOKEN")
TOKEN2 = os.getenv("BOT_TOKEN2")

CHANNEL = "@BotKanal24"
CHANNEL_LINK = "https://t.me/BotKanal24"
user_links = {}

def is_subscribed(bot, uid):
    try:
        m = bot.get_chat_member(CHANNEL, uid)
        return m.status in ['member','administrator','creator']
    except:
        return False

def create_bot(TOKEN):
    bot = telebot.TeleBot(TOKEN)

    @bot.message_handler(commands=['start'])
    def start(m):
        txt = "🌟 اهلا " + m.from_user.first_name + " | ALBASHA 🌟\n👑 بوت التحميل الاسطوري 👑\n🎬 تيك توك | 📸 انستا | 📘 فيسبوك | 🎥 يوتيوب"
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton('📢 اشترك بقناتنا', url=CHANNEL_LINK))
        kb.add(types.InlineKeyboardButton('✅ تحققت', callback_data='check_sub'))
        bot.send_message(m.chat.id, txt, reply_markup=kb)

    @bot.message_handler(func=lambda m: 'http' in m.text)
    def handle(m):
        if not is_subscribed(bot, m.from_user.id):
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton('📢 اشترك اولا', url=CHANNEL_LINK))
            kb.add(types.InlineKeyboardButton('✅ تحقق', callback_data='check_sub'))
            bot.reply_to(m, '❌ اشترك بالقناة اولا', reply_markup=kb)
            return
        user_links[m.from_user.id] = m.text.strip()
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(types.InlineKeyboardButton('فيديو 🎬', callback_data='video'), types.InlineKeyboardButton('صوت 🎵', callback_data='audio'))
        kb.add(types.InlineKeyboardButton('📸 صور', callback_data='photo'))
        bot.reply_to(m, '✅ اختر نوع التحميل:', reply_markup=kb)

    @bot.callback_query_handler(func=lambda call: True)
    def cb(call):
        if call.data == 'check_sub':
            if is_subscribed(bot, call.from_user.id):
                bot.answer_callback_query(call.id, 'تم ✅')
                bot.send_message(call.message.chat.id, '✅ تمام! ابعت الرابط')
            else:
                bot.answer_callback_query(call.id, 'ما اشتركت ❌')
            return

        url = user_links.get(call.from_user.id)
        if not url:
            return
        fid = str(call.from_user.id)
        tmp_video = os.path.join("/tmp", fid + ".mp4")
        tmp_audio = os.path.join("/tmp", fid + ".m4a")
        tmp_post = os.path.join("/tmp", fid + "_post")

        try:
            if call.data == 'video':
                opts = {'outtmpl': tmp_video, 'format': 'best[ext=mp4]/best', 'quiet': True}
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([url])
                bot.send_video(call.message.chat.id, open(tmp_video,'rb'))
                if os.path.exists(tmp_video): os.remove(tmp_video)

            elif call.data == 'audio':
                opts = {'outtmpl': tmp_audio, 'format': 'bestaudio/best', 'quiet': True}
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([url])
                # يدور على اي ملف نزل
                files = glob.glob(os.path.join("/tmp", fid + ".*"))
                if files:
                    bot.send_audio(call.message.chat.id, open(files[0],'rb'))
                    os.remove(files[0])

            else: # صور
                short = re.search(r'/(p|reel|tv)/([^/?&]+)', url)
                code = short.group(2)
                if os.path.exists(tmp_post):
                    shutil.rmtree(tmp_post, ignore_errors=True)
                L = instaloader.Instaloader(dirname_pattern=tmp_post, save_metadata=False, download_comments=False, download_geotags=False)
                post = instaloader.Post.from_shortcode(L.context, code)
                L.download_post(post, target=fid + "_post")
                if os.path.exists(tmp_post):
                    for fl in os.listdir(tmp_post):
                        if fl.endswith(('.jpg','.jpeg','.png')):
                            bot.send_photo(call.message.chat.id, open(os.path.join(tmp_post,fl),'rb'))
                    shutil.rmtree(tmp_post, ignore_errors=True)

        except Exception as e:
            bot.send_message(call.message.chat.id, "❌ خطأ: " + str(e))

    return bot

def run_bot(token):
    bot = create_bot(token)
    bot.infinity_polling(skip_pending=True)

if TOKEN1:
    threading.Thread(target=run_bot, args=(TOKEN1,)).start()

if TOKEN2 and TOKEN2!= TOKEN1 and ":" in TOKEN2:
    threading.Thread(target=run_bot, args=(TOKEN2,)).start()

while True:
    time.sleep(3600)
