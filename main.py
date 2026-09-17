import telebot, threading, os, re, glob, shutil
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
    except:
        return True

def clean_tmp(fid):
    for f in glob.glob(f'/tmp/{fid}*'):
        try: os.remove(f)
        except: pass
    folder = f'/tmp/{fid}_post'
    if os.path.exists(folder):
        shutil.rmtree(folder, ignore_errors=True)

def create_bot(TOKEN):
    bot = telebot.TeleBot(TOKEN)

    @bot.message_handler(commands=['start'])
    def start(m):
        txt = f"""🌟 اهلا {m.from_user.first_name} 🌟
━━━━━━━━━━━━━━━
👑 بوت التحميل الاسطوري 👑
🎬 تيك توك | 📸 انستا | 📘 فيسبوك | 🎥 يوتيوب
💎 بدون علامة مائية - جودة عالية
━━━━━━━━━━━━━━━"""
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton('📢 اشترك بقناتنا', url=CHANNEL_LINK))
        kb.add(types.InlineKeyboardButton('✅ تحققت', callback_data='check_sub'))
        kb.add(types.InlineKeyboardButton('🔗 قناتنا الرسمية', url=CHANNEL_LINK))
        bot.send_message(m.chat.id, txt, reply_markup=kb)

    @bot.message_handler(func=lambda m: True)
    def handle(m):
        if 'http' not in m.text:
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton('قناتنا الرسمية', url=CHANNEL_LINK))
            bot.reply_to(m, '❌ ابعت رابط صحيح', reply_markup=kb)
            return
        if not is_subscribed(bot, m.from_user.id):
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton('📢 اشترك اولا', url=CHANNEL_LINK))
            kb.add(types.InlineKeyboardButton('✅ تحقق', callback_data='check_sub'))
            bot.reply_to(m, 'يجب الاشتراك بالقناة اولا', reply_markup=kb)
            return

        user_links[m.from_user.id] = m.text.strip()
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(types.InlineKeyboardButton('فيديو 🎬', callback_data='video'), types.InlineKeyboardButton('موسيقى 🎵', callback_data='audio'))
        kb.add(types.InlineKeyboardButton('📸 صور البوست', callback_data='photo'))
        kb.add(types.InlineKeyboardButton('قناتنا الرسمية', url=CHANNEL_LINK))
        bot.reply_to(m, '✅ اختر نوع التحميل:', reply_markup=kb)

    @bot.callback_query_handler(func=lambda call: True)
    def cb(call):
        if call.data == 'check_sub':
            if is_subscribed(bot, call.from_user.id):
                bot.answer_callback_query(call.id, 'تم الاشتراك ✅')
                kb = types.InlineKeyboardMarkup()
                kb.add(types.InlineKeyboardButton('قناتنا الرسمية', url=CHANNEL_LINK))
                bot.send_message(call.message.chat.id, '✅ تم! ابعت الرابط الآن', reply_markup=kb)
            else:
                bot.answer_callback_query(call.id, 'لم تشترك بعد ❌')
            return

        url = user_links.get(call.from_user.id)
        if not url:
            bot.answer_callback_query(call.id, 'ابعت الرابط اولا')
            return

        bot.answer_callback_query(call.id, 'جاري التحميل...')
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton('قناتنا الرسمية', url=CHANNEL_LINK))
        bot.send_message(call.message.chat.id, '⏳ جاري التحميل لا تغادر...', reply_markup=kb)

        fid = call.from_user.id
        clean_tmp(fid)

        try:
            if call.data == 'photo':
                short = re.search(r'/(p|reel|tv)/([^/?&]+)', url)
                if not short:
                    bot.send_message(call.message.chat.id, '❌ رابط غلط', reply_markup=kb)
                    return
                code = short.group(2)
                L = instaloader.Instaloader(dirname_pattern=f'/tmp/{fid}_post', save_metadata=False, download_comments=False, download_geotags=False)
                L.download_pictures = True
                L.download_videos = False
                post = instaloader.Post.from_shortcode(L.context, code)
                L.download_post(post, target=f'{fid}_post')
                folder = f'/tmp/{fid}_post'
                if os.path.exists(folder):
                    files = [os.path.join(folder,f) for f in os.listdir(folder) if f.endswith(('.jpg','.jpeg','.png'))]
                    for fl in files:
                        bot.send_photo(call.message.chat.id, open(fl,'rb'), reply_markup=kb)
                clean_tmp(fid)

            elif call.data == 'video':
                opts = {'outtmpl': f'/tmp/{fid}.mp4', 'format': 'best[ext=mp4]/best', 'quiet': True, 'no_warnings': True}
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([url])
                bot.send_video(call.message.chat.id, open(f'/tmp/{fid}.mp4','rb'), caption='🎬 تم التحميل', reply_markup=kb)
                os.remove(f'/tmp/{fid}.mp4')

            else: # موسيقى بدون ffmpeg
                opts = {'outtmpl': f'/tmp/{fid}.%(ext)s', 'format': 'bestaudio[ext=m4a]/bestaudio/best', 'quiet': True, 'no_warnings': True}
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([url])
                fpath = glob.glob(f'/tmp/{fid}.*')[0]
                bot.send_audio(call.message.chat.id, open(fpath,'rb'), caption='🎵 تم التحميل', reply_markup=kb)
                os.remove(fpath)

        except Exception as e:
            bot.send_message(call.message.chat.id, f'❌ خطأ: {e}', reply_markup=kb)

    return bot

bot1 = create_bot(TOKEN1)
bot2 = create_bot(TOKEN2)

threading.Thread(target=lambda: bot1.infinity_polling(skip_pending=True)).start()
threading.Thread(target=lambda: bot2.infinity_polling(skip_pending=True)).start()
print("Bots running...")
