import telebot, threading, os, re, glob, shutil, json
from telebot import types
import yt_dlp
import instaloader

TOKEN1 = os.getenv("BOT_TOKEN")
TOKEN2 = os.getenv("BOT_TOKEN2")

CHANNEL = "@BotKanal24"
CHANNEL_LINK = "https://t.me/BotKanal24"
user_links = {}

def get_source(text):
    p = text.split()
    return p[1].lower() if len(p) > 1 else "search_direct"

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
        txt = f"🌟 اهلا {m.from_user.first_name} 🌟\n👑 بوت التحميل الاسطوري 👑"
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton('📢 اشترك بقناتنا', url=CHANNEL_LINK))
        kb.add(types.InlineKeyboardButton('✅ تحققت', callback_data='check_sub'))
        bot.send_message(m.chat.id, txt, reply_markup=kb)

    @bot.message_handler(func=lambda m: True)
    def handle(m):
        if 'http' not in m.text:
            return
        if not is_subscribed(bot, m.from_user.id):
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton('📢 اشترك اولا', url=CHANNEL_LINK))
            kb.add(types.InlineKeyboardButton('✅ تحقق', callback_data='check_sub'))
            bot.reply_to(m, 'اشترك اولا', reply_markup=kb)
            return
        user_links[m.from_user.id] = m.text.strip()
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(types.InlineKeyboardButton('فيديو 🎬', callback_data='video'))
        kb.add(types.InlineKeyboardButton('موسيقى 🎵', callback_data='audio'))
        kb.add(types.InlineKeyboardButton('📸 صور', callback_data='photo'))
        bot.reply_to(m, '✅ اختر نوع التحميل:', reply_markup=kb)

    @bot.callback_query_handler(func=lambda call: True)
    def cb(call):
        if call.data == 'check_sub':
            if is_subscribed(bot, call.from_user.id):
                bot.answer_callback_query(call.id, 'تم ✅')
                bot.send_message(call.message.chat.id, '✅ تم! ابعت الرابط')
            else:
                bot.answer_callback_query(call.id, 'لم تشترك ❌')
            return
        url = user_links.get(call.from_user.id)
        if not url:
            return
        fid = call.from_user.id
        try:
            if call.data == 'video':
                opts = {'outtmpl': f'/tmp/{fid}.mp4', 'format': 'best[ext=mp4]/best', 'quiet': True}
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([url])
                bot.send_video(call.message.chat.id, open(f'/tmp/{fid}.mp4','rb'))
                os.remove(f'/tmp/{fid}.mp4')
            elif call.data == 'audio':
                opts = {'outtmpl': f'/tmp/{fid}.m4a', 'format': 'bestaudio/best', 'quiet': True}
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([url])
                bot.send_audio(call.message.chat.id, open(f'/tmp/{fid}.m4a','rb'))
                os.remove(f'/tmp/{fid}.m4a')
            else:
                short = re.search(r'/(p|reel|tv)/([^/?&]+)', url)
                code = short.group(2)
                L = instaloader.Instaloader(dirname_pattern=f'/tmp/{fid}_post', save_metadata=False, download_comments=False, download_geotags=False)
                post = instaloader.Post.from_shortcode(L.context, code)
                L.download_post(post, target=f'{fid}_post')
        except Exception as e:
            bot.send_message(call.message.chat.id, f'❌ {e}')
    return bot

b1 = create_bot(TOKEN1)
threading.Thread(target=lambda: b1.infinity_polling(skip_pending=True)).start()

if TOKEN2:
    b2 = create_bot(TOKEN2)
    threading.Thread(target=lambda: b2.infinity_polling(skip_pending=True)).start()

print("Bots running...")
