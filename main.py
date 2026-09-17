import telebot
from telebot import types
import threading

TOKEN1 = "8977024211:AAG3OD86xIdCl7t13Oalk_Fy7X8xG1ZAOJs"
TOKEN2 = "8911586038:AAEJPLNv8dVdgKZL0n0qhqEMxvC9h_BeUp0"
CHANNEL = "@BotKanal24"
CHANNEL_LINK = "https://t.me/BotKanal24"

user_links = {}

def is_subscribed(bot, user_id):
    try:
        m = bot.get_chat_member(CHANNEL, user_id)
        return m.status in ['member','administrator','creator']
    except:
        return False

def create_bot(TOKEN):
    bot = telebot.TeleBot(TOKEN)

    @bot.message_handler(commands=['start'])
    def start(m):
        name = m.from_user.first_name
        txt = f"اهلا {name} \n\nبوت التحميل الاسطوري\nتيك توك | انستا | فيسبوك | يوتيوب\n\nيجب الاشتراك اولا"
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton('اشترك بالقناة', url=CHANNEL_LINK))
        kb.add(types.InlineKeyboardButton('تحققت', callback_data='check_sub'))
        kb.add(types.InlineKeyboardButton('قناتنا الرسمية', url=CHANNEL_LINK))
        bot.send_message(m.chat.id, txt, reply_markup=kb)

    @bot.message_handler(func=lambda m: True)
    def handle(m):
        if not is_subscribed(bot, m.from_user.id):
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton('اشترك اولا', url=CHANNEL_LINK))
            kb.add(types.InlineKeyboardButton('تحقق', callback_data='check_sub'))
            bot.reply_to(m, 'يجب الاشتراك اولا', reply_markup=kb)
            return

        url = m.text.strip()
        if 'http' not in url:
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton('قناتنا الرسمية', url=CHANNEL_LINK))
            bot.reply_to(m, 'ابعت رابط صحيح', reply_markup=kb)
            return

        user_links[m.from_user.id] = url
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(
            types.InlineKeyboardButton('فيديو', callback_data='video'),
            types.InlineKeyboardButton('موسيقى', callback_data='audio')
        )
        kb.add(types.InlineKeyboardButton('قناتنا الرسمية', url=CHANNEL_LINK))
        bot.reply_to(m, f'اختر: {url}', reply_markup=kb)

    @bot.callback_query_handler(func=lambda call: True)
    def cb(call):
        if call.data == 'check_sub':
            if is_subscribed(bot, call.from_user.id):
                bot.answer_callback_query(call.id, 'تم')
                kb = types.InlineKeyboardMarkup()
                kb.add(types.InlineKeyboardButton('قناتنا الرسمية', url=CHANNEL_LINK))
                bot.send_message(call.message.chat.id, 'تم الاشتراك ابعت الرابط', reply_markup=kb)
            else:
                bot.answer_callback_query(call.id, 'لم تشترك')
            return

        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton('قناتنا الرسمية', url=CHANNEL_LINK))
        bot.send_message(call.message.chat.id, 'جاري التحميل...', reply_markup=kb)

    return bot

bot1 = create_bot(TOKEN1)
bot2 = create_bot(TOKEN2)

threading.Thread(target=lambda: bot1.infinity_polling()).start()
threading.Thread(target=lambda: bot2.infinity_polling()).start()
print("running")
