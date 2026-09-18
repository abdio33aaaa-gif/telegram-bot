import telebot, threading, os, re, glob, shutil, json
from telebot import types
import yt_dlp
import instaloader

TOKEN1 = os.getenv("BOT_TOKEN")
TOKEN2 = os.getenv("BOT_TOKEN2") or TOKEN1

CHANNEL = "@BotKanal24"
CHANNEL_LINK = "https://t.me/BotKanal24"
user_links = {}
STATS_FILE = "sources.json"

def log_source(source):
    try:
        with open(STATS_FILE, "r", encoding="utf-8") as f: data = json.load(f)
    except: data = {}
    data[source] = data.get(source, 0) + 1
    with open(STATS_FILE, "w", encoding="utf-8") as f: json.dump(data, f, indent=2, ensure_ascii=False)

def get_source(text):
    parts = text.split()
    return parts[1].lower() if len(parts) > 1 else "search_direct"

def is_subscribed(bot, uid):
    try:
        m = bot.get_chat_member(CHANNEL, uid)
        return m.status in ['member','administrator','creator']
    except: return False

def clean_tmp(fid):
    for f in glob.glob(f'/tmp/{fid}*'):
        try: os.remove(f)
        except: pass
    folder = f'/tmp/{fid}_post'
    if os.path.exists(folder): shutil.rmtree(folder, ignore_errors=True)

def create_bot(TOKEN):
    bot = telebot.TeleBot(TOKEN)
    @bot.message_handler(commands=['start'])
    def start(m):
        log_source(get_source(m.text))
        name = m.from_user.first_name
        txt = f"🌟 اهلا {name} 🌟\n👑 بوت التحميل الاسطوري 👑"
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton('📢 اشترك بقناتنا', url=CHANNEL_LINK))
        kb.add(types.InlineKeyboardButton('✅ تحققت', callback_data='check_sub'))
        bot.send_message(m.chat.id, txt, reply_markup=kb)

    @bot.message_handler(commands=['stats'])
    def stats(m):
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f: data = json.load(f)
            txt = "📊 من وين اجو:\n"
            for k,v in data.items(): txt += f"{k}: {v}\n"
            bot.send_message(m.chat.id, txt)
        except: bot.send_message(m.chat.id, "لسا ما في بيانات")

    @bot.message_handler(func=lambda m: True)
    def handle(m):
        if 'http' not in m.text: return
        if not is_subscribed(bot, m.from_user.id):
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton('📢 اشترك اولا', url=CHANNEL_LINK))
            kb.add(types.InlineKeyboardButton('✅ تحقق', callback_data='check_sub'))
            bot.reply_to(m, 'يجب الاشتراك اولا', reply_markup=kb)
            return
        user_links[m.from_user.id] = m.text.strip()
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(types.InlineKeyboardButton('فيديو 🎬', callback_data='video'), types.InlineKeyboardButton('موسيقى 🎵', callback_data='audio'))
        kb.add(types.InlineKeyboardButton('📸 صور', callback_data='photo'))
        bot.reply_to(m, '✅ اختر:', reply_markup=kb)

    @bot.callback_query_handler(func=lambda call: True)
    def cb(call):
        if call.data == 'check_sub':
            if is_subscribed(bot, call.from_user.id):
                bot.answer_callback_query(call.id, 'تم ✅')
                bot.send_message(call.message.chat.id, '✅ تم! ابعت الرابط')
            else: bot.answer_callback_query(call.id, 'لم تشترك ❌')
            return
        url = user_links.get(call.from_user.id)
        if not url: return
        fid = call.from_user.id
        clean_tmp(fid)
        try:
            if call.data == 'video':
                opts = {'outtmpl': f'/tmp/{fid}.mp4', 'format': 'best[ext=mp4]/best', 'quiet': True}
                with yt_dlp.YoutubeDL(opts) as ydl: ydl.download([url])
                bot.send_video(call.message.chat.id, open(f'/tmp/{fid}.mp4','rb'))
                os.remove(f'/tmp/{fid}.mp4')
            elif call.data == 'photo':
                short = re.search(r'/(p|reel|tv)/([^/?&]+)', url)
                code = short.group(2)
                L = instaloader.Instaloader(dirname_pattern=f'/tmp/{fid}_post', save_metadata=False, download_comments=False, download_geotags=False)
                L.download_pictures = True; L.download_videos = False
                post = instaloader.Post.from_shortcode(L.context, code)
                L.download_post(post, target=f'{fid}_post')
                folder = f'/tmp/{fid}_post'
                if os.path.exists(folder):
                    files = [os.path.join(folder,f) for f in os.listdir(folder) if f.endswith(('.jpg','.jpeg','.png'))]
                    for fl in files: bot.send_photo(call.message.chat.id, open(fl,'rb'))
                clean_tmp(fid)
            else:
                opts = {'outtmpl': f'/tmp/{fid}.%(ext)s', 'format': 'bestaudio/best', 'quiet': True}
                with yt_dlp.YoutubeDL(opts) as ydl: ydl.download([url])
                fpath = glob.glob(f'/tmp/{fid}.*')[0]
                bot.send_audio(call.message.chat.id, open(fpath,'rb'))
                os.remove(fpath)
        except Exception as e: bot.send_message(call.message.chat.id, f'❌ {e}')
    return bot

bot1 = create_bot(TOKEN1)
threading.Thread(target=lambda: bot1.infinity_polling(skip_pending=True)).start()
if TOKEN2
