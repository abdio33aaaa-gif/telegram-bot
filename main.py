import os, re, requests, telebot, time
from flask import Flask, request
from telebot import types
from urllib.parse import quote
import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL").rstrip("/") if os.getenv("WEBHOOK_URL") else ""
CHANNEL = "@BotKanal24"

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

def setup_webhook():
    try:
        bot.remove_webhook()
        time.sleep(1)
        bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
        print("Webhook OK")
    except Exception as e:
        print(e)

setup_webhook()

@app.route('/')
def home(): return "بوت التحميل السريع Live"
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
    bot.process_new_updates([update])
    return "ok", 200

def is_subscribed(user_id):
    try:
        m = bot.get_chat_member(CHANNEL, user_id)
        return m.status in ['member','administrator','creator']
    except:
        return True

def send_subscribe_message(chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 اشترك بالقناة", url="https://t.me/BotKanal24"))
    markup.add(types.InlineKeyboardButton("✅ تحققت اشتركت", callback_data="check_sub"))
    bot.send_message(chat_id, f"⚠️ لازم تشترك بالقناة أولاً {CHANNEL}\nاشترك وبعدين اضغط تحقق 👇", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_sub_callback(call):
    if is_subscribed(call.from_user.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "تم ✅ هلا ابعت رابط")
    else:
        bot.answer_callback_query(call.id, "لسا ما اشتركت", show_alert=True)

def expand_vm_link(short_url):
    try:
        r = requests.get(short_url, headers={"User-Agent":"Mozilla/5.0"}, allow_redirects=True, timeout=15)
        if "/video/" in r.url: return r.url
        m = re.search(r'https://www\.tiktok\.com/@[^/]+/video/\d+', r.text)
        if m: return m.group(0)
    except: pass
    return short_url

def get_tiktok_video(original_url):
    url = expand_vm_link(original_url)
    try:
        r = requests.post("https://www.tikwm.com/api/", json={"url": url, "hd":1}, headers={"User-Agent":"Mozilla/5.0","Referer":"https://www.tikwm.com/"}, timeout=20)
        d = r.json()
        if d.get("data",{}).get("play"): return d["data"]["play"]
    except: pass
    try:
        r = requests.get(f"https://api.tiklydown.eu.org/api/download?url={quote(url)}", timeout=20)
        d = r.json()
        if d.get("video",{}).get("noWatermark"): return d["video"]["noWatermark"]
    except: pass
    return None

@bot.message_handler(commands=['start'])
def start(message):
    if not is_subscribed(message.from_user.id):
        return send_subscribe_message(message.chat.id)
    text = "🚀 حل ستوري انستا بجودة HD\nسريع - آمن - بدون اعلانات\n\nابعت رابط الستوري او التيك توك 📩\nيدعم تيك توك + انستا + يوتيوب + فيس"
    bot.reply_to(message, text)

@bot.message_handler(func=lambda m: True)
def handle(message):
    if not is_subscribed(message.from_user.id):
        return send_subscribe_message(message.chat.id)
    url = message.text.strip().split()[0]
    if "http" not in url: return
    wait = bot.reply_to(message, "⏳ عم حمل...")
    try:
        video_url = None
        if "tiktok.com" in url:
            video_url = get_tiktok_video(url)
            if video_url:
                data = requests.get(video_url, headers={"User-Agent":"Mozilla/5.0"}, timeout=40).content
                bot.send_video(message.chat.id, data, caption="تم ✅", reply_to_message_id=message.message_id)
                bot.delete_message(message.chat.id, wait.message_id)
                return
        ydl_opts = {'format':'best[ext=mp4]/best','outtmpl':'video.%(ext)s','quiet':True,'no_warnings':True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        with open(filename, 'rb') as v:
            bot.send_video(message.chat.id, v, caption="تم ✅", reply_to_message_id=message.message_id)
        bot.delete_message(message.chat.id, wait.message_id)
        os.remove(filename)
    except Exception as e:
        print(e)
        bot.edit_message_text("❌ فشل التحميل تأكد الرابط عام", message.chat.id, wait.message_id)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 10000)))
