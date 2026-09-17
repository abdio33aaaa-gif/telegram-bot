import telebot, threading, os, re, glob, requests
from telebot import types
import yt_dlp
import instaloader

TOKEN1 = "8977024211:AAG3OD86xIdCl7t13Oalk_Fy7X8xG1ZAOJs"
TOKEN2 = "8911586038:AAEJPLNv8dVdgKZL0n0qhqEMxvC9h_BeUp0"
CHANNEL = "@BotKanal24"
CHANNEL_LINK = "https://t.me/BotKanal24"
user_links = {}

def is_subscribed(bot, uid):
    try:
        m = bot.get_chat_member(CHANNEL, uid)
        return m.status in ['member','administrator','creator']
    except: return True

def create_bot(TOKEN):
    bot = telebot.TeleBot(TOKEN)

    @bot.message_handler(commands=['start'])
    def start(m):
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton('اشترك بالقناة', url=CHANNEL_LINK))
        kb.add(types.InlineKeyboardButton('تحققت', callback_data='check_sub'))
        kb.add(types.InlineKeyboardButton('قناتنا الرسمية', url=CHANNEL_LINK))
        bot.send_message(m.chat.id, "ارسل رابط", reply_markup=kb)

    @bot.message_handler(func=lambda m: True)
    def handle(m):
        if 'http' not in m.text: return
        user_links[m.from_user.id] = m.text.strip()
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(types.InlineKeyboardButton('فيديو', callback_data='video'), types.InlineKeyboardButton('موسيقى', callback_data='audio'))
        kb.add(types.InlineKeyboardButton('صور البوست 📸', callback_data='photo'))
        kb.add(types.InlineKeyboardButton('قناتنا الرسمية', url=CHANNEL_LINK))
        bot.reply_to(m, 'اختر نوع التحميل', reply_markup=kb)

    @bot.callback_query_handler(func=lambda call: True)
    def cb(call):
        if call.data == 'check_sub': return
        url = user_links.get(call.from_user.id)
        if not url: return
        bot.answer_callback_query(call.id, 'جاري...')
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton('قناتنا الرسمية', url=CHANNEL_LINK))
        bot.send_message(call.message.chat.id, '⏳ جاري التحميل...', reply_markup=kb)

        fid = call.from_user.id
        try:
            for f in glob.glob(f'/tmp/{fid}*'):
                try: os.remove(f)
                except: pass

            if call.data == 'photo':
                # --- تحميل صور انستا بـ instaloader ---
                shortcode = re.search(r'/(p|reel)/([^/?]+)', url)
                if not shortcode:
                    bot.send_message(call.message.chat.id, 'رابط غلط', reply_markup=kb)
                    return
                code = shortcode.group(2)
                L = instaloader.Instaloader(dirname_pattern=f'/tmp/{fid}_post', save_metadata=False, download_comments=False)
                L.download_pictures = True
                L.download_videos = False
                post = instaloader.Post.from_shortcode(L.context, code)
                L.download_post(post, target=f'{fid}_post')

                folder = f'/tmp/{fid}_post'
                if os.path.exists(folder):
                    for file in os.listdir(folder):
                        if file.endswith(('.jpg','.jpeg','.png')):
                            bot.send_photo(call.message.chat.id, open(os.path.join(folder,file),'rb'), reply_markup=kb)
                    # حذف
                    import shutil
                    shutil.rmtree(folder, ignore_errors=True)
                return

            elif call.data == 'video':
                opts = {'outtmpl': f'/tmp/{fid}.mp4', 'format': 'best', 'quiet': True}
                with yt_dlp.YoutubeDL(opts) as ydl: ydl.download([url])
                bot.send_video(call.message.chat.id, open(f'/tmp/{fid}.mp4','rb'), reply_markup=kb)
                os.remove(f'/tmp/{fid}.mp4')
            else:
                opts = {'outtmpl': f'/tmp/{fid}.mp3', 'format': 'bestaudio', 'quiet': True, 'postprocessors': [{'key':'FFmpegExtractAudio','preferredcodec':'mp3'}]}
                with yt_dlp.YoutubeDL(opts) as ydl: ydl.download([url])
                bot.send_audio(call.message.chat.id, open(f'/tmp/{fid}.mp3','rb'), reply_markup=kb)
                os.remove(f'/tmp/{fid}.mp3')

        except Exception as e:
            bot.send_message(call.message.chat.id, f'خطأ: {e}\nجرب رابط ريلز', reply_markup=kb)

    return bot

bot1 = create_bot(TOKEN1)
bot2 = create_bot(TOKEN2)
threading.Thread(target=lambda: bot1.infinity_polling()).start()
threading.Thread(target=lambda: bot2.infinity_polling()).start()
