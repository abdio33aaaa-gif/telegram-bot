import telebot, threading, os, re, glob, shutil, json
from telebot import types
import yt_dlp
import instaloader

# يقرا التوكن من Railway Variables
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

def create_bot(TOKEN, BOT_NAME="الباشا"):
    bot = telebot.TeleBot(TOKEN)

    @bot.message_handler(commands=['start'])
    def start(m):
        name = m.from_user.first_name
        txt = (
            f"🌟 اهلا {name} | {BOT_NAME} 🌟\n"
            f"━━━━━━━━━━━━━━━\n"
            f"👑 بوت التحميل الاسطوري 👑\n"
            f"🎬 تيك توك | 📸 انستا | 📘 فيسبوك | 🎥 يوتيوب\n"
            f"💎 بدون علامة مائية - جودة عالية\n"
            f"━━━━━━━━━━━━━━━"
        )
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton('📢 اشترك بقناتنا', url=CHANNEL_LINK))
        kb.add(types.InlineKeyboardButton('✅ تحققت', callback_data='check_sub'))
        kb.add(types.InlineKeyboardButton('🔗 قناتنا الرسمية', url=CHANNEL_LINK))
        bot.send_message(m.chat.id, txt, reply_markup=kb)

    @bot.message_handler(func=lambda m: 'http' in m.text)
    def handle(m):
        if not is_subscribed(bot, m.from_user.id):
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton('📢 اشترك اولا', url=CHANNEL_LINK))
            kb.add(types.InlineKeyboardButton('✅ تحقق', callback_data='check_sub'))
            bot.reply_to(m, '❌ يجب الاشتراك بالقناة أولاً', reply_markup=kb)
            return

        user_links[m.from_user.id] = m.text.strip()
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(types.InlineKeyboardButton('فيديو 🎬', callback_data='video'),
               types.InlineKeyboardButton('صوت 🎵', callback_data='audio'))
        kb.add(types.InlineKeyboardButton('📸 صور البوست', callback_data='photo'))
        kb.add(types.InlineKeyboardButton('قناتنا الرسمية', url=CHANNEL_LINK))
        bot.reply_to(m, '✅ اختر نوع التحميل:', reply_markup=kb)

    @bot.callback_query_handler(func=lambda call: True)
    def cb(call):
        if call.data == 'check_sub':
            if is_subscribed(bot, call.from_user.id):
                bot.answer_callback_query(call.id, 'تم الاشتراك ✅')
                bot.send_message(call.message.chat.id, '✅ تمام! هلا ابعت الرابط')
            else:
                bot.answer_callback_query(call.id, 'لسا ما اشتركت ❌')
            return

        url = user_links.get(call.from_user.id)
        if not url:
            bot.answer_callback_query(call.id, 'ابعت رابط جديد')
            return

        bot.answer_callback_query(call.id, 'جاري التحميل...')
        fid = call.from_user.id

        try:
            if call.data == 'video':
                opts = {'outtmpl': f'/tmp/{fid}.mp4', 'format': 'best[ext=mp4]/best', 'quiet': True, 'no_warnings': True}
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([url])
                bot.send_video(call.message.chat.id, open(f'/tmp/{fid}.mp4','rb'), caption='🎬 تم ✅')
                os.remove(f'/tmp/{fid}.mp4')

            elif call.data == 'audio':
                opts = {'outtmpl': f'/tmp/{fid}.m4a', 'format': 'bestaudio/best', 'quiet': True, 'no_warnings': True}
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([url])
                f = glob.glob(f'/tmp/{fid}.*')[0]
                bot.send_audio(call.message.chat.id, open(f,'rb'), caption='🎵 تم ✅')
                os.remove(f)

            elif call.data == 'photo':
                short = re.search(r'/(p|reel|tv)/([^/?&]+)', url)
                if not short:
                    bot.send_message(call.message.chat.id, '❌ رابط انستا غير صحيح')
                    return
                code = short.group(2)
                folder = f'/tmp/{fid}_post'
                if os.path.exists(folder):
                    shutil.rmtree(folder, ignore_errors=True)
                L = instaloader.Instaloader(dirname_pattern=f'/tmp/{fid}_post', save_metadata=False, download_comments=False, download_geotags=False)
                post = instaloader.Post.from_shortcode(L.context, code)
                L.download_post(post, target=f'{fid}_post')
                if os.path.exists(folder):
                    for file in os.listdir(folder):
                        if file.endswith(('.jpg','.jpeg','.png')):
                            bot.send_photo(call.message.chat.id, open(os.path.join(folder,file),'rb'))
                    shutil.rmtree(folder, ignore_errors=True)

        except Exception as e:
            bot.send_message(call.message.chat.id, f'❌ خطأ: {e}')

    return bot

# شغل البوتات
if not TOKEN1:
    print("❌ ما لقيت BOT_TOKEN بالـ Variables")
else:
    b1 = create_bot(TOKEN1, "ALBASHA | الباشا")
    threading.Thread(target=lambda: b1.infinity_polling(skip_pending=True, timeout=60), daemon=True).start()
    print("Bot 1 Started")

    # شغل الت
