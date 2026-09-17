import telebot
from telebot import types
import threading, os, glob
import yt_dlp

TOKEN1 = "8977024211:AAG3OD86xIdCl7t13Oalk_Fy7X8xG1ZAOJs"
TOKEN2 = "8911586038:AAEJPLNv8dVdgKZL0n0qhqEMxvC9h_BeUp0"
CHANNEL = "@BotKanal24"
CHANNEL_LINK = "https://t.me/BotKanal24"

user_links = {}

def is_subscribed(bot, uid):
    try:
        m = bot.get_chat_member(CHANNEL, uid)
        return m.status in ['member','administrator','creator']
    except:
        return True

def create_bot(TOKEN):
    bot = telebot.TeleBot(TOKEN)

    @bot.message_handler(commands=['start'])
    def start(m):
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton('اشترك بالقناة', url=CHANNEL_LINK))
        kb.add(types.InlineKeyboardButton('تحققت', callback_data='check_sub'))
        kb.add(types.InlineKeyboardButton('قناتنا الرسمية', url=CHANNEL_LINK))
        bot.send_message(m.chat.id, f"اهلا {m.from_user.first_name}\nارسل رابط انستا", reply_markup=kb)

    @bot.message_handler(func=lambda m: True)
    def handle(m):
        if 'http' not in m.text: return
        if not is_subscribed(bot, m.from_user.id):
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton('اشترك اولا', url=CHANNEL_LINK))
            kb.add(types.InlineKeyboardButton('تحقق', callback_data='check_sub'))
            bot.reply_to(m, 'اشترك اولا', reply_markup=kb)
            return
        user_links[m.from_user.id] = m.text.strip()
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(types.InlineKeyboardButton('فيديو', callback_data='video'), types.InlineKeyboardButton('موسيقى', callback_data='audio'))
        kb.add(types.InlineKeyboardButton('صور البوست', callback_data='photo'))
        kb.add(types.InlineKeyboardButton('قناتنا الرسمية', url=CHANNEL_LINK))
        bot.reply_to(m, 'اختر نوع التحميل', reply_markup=kb)

    @bot.callback_query_handler(func=lambda call: True)
    def cb(call):
        if call.data == 'check_sub':
            bot.answer_callback_query(call.id, 'تم')
            return
        if call.from_user.id not in user_links:
            return
        url = user_links[call.from_user.id]
        bot.answer_callback_query(call.id, 'جاري التحميل')

        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton('قناتنا الرسمية', url=CHANNEL_LINK))
        bot.send_message(call.message.chat.id, 'جاري التحميل...', reply_markup=kb)

        fid = call.from_user.id
        try:
            # تنظيف قديم
            for f in glob.glob(f'/tmp/{fid}.*'): os.remove(f)

            if call.data == 'photo':
                # تحميل صور
                opts = {'outtmpl': f'/tmp/{fid}_%(id)s.%(ext)s', 'quiet': True, 'no_warnings': True}
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([url])
                files = glob.glob(f'/tmp/{fid}_*')
                for fl in files:
                    bot.send_photo(call.message.chat.id, open(fl,'rb'), reply_markup=kb)
                    os.remove(fl)
                return

            if call.data == 'video':
                opts = {'outtmpl': f'/tmp/{fid}.mp4', 'format': 'best', 'quiet': True}
            else:
                opts = {'outtmpl': f'/tmp/{fid}.mp3', 'format': 'bestaudio', 'quiet': True, 'postprocessors': [{'key':'FFmpegExtractAudio','preferredcodec':'mp3'}]}

            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])

            if call.data == 'video':
                bot.send_video(call.message.chat.id, open(f'/tmp/{fid}.mp4','rb'), reply_markup=kb)
            else:
                bot.send_audio(call.message.chat.id, open(f'/tmp/{fid}.mp3','rb'), reply_markup=kb)

        except Exception as e:
            if 'no video' in str(e).lower():
                bot.send_message(call.message.chat.id, 'هذا البوست صور فقط! دوس زر صور البوست', reply_markup=kb)
            else:
                bot.send_message(call.message.chat.id, f'خطأ: {e}', reply_markup=kb)

    return bot

bot1 = create_bot(TOKEN1)
bot2 = create_bot(TOKEN2)
threading.Thread(target=lambda: bot1.infinity_polling()).start()
threading.Thread(target=lambda: bot2.infinity_polling()).start()
