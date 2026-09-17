@bot.message_handler(commands=['start'])
def start(m):
    name = m.from_user.first_name
    welcome_text = f"""
أهلين يا {name} 👋🔥

أنا بوت التحميل السريع - بحملك من:

🎬 تيك توك بدون علامة مائية
📸 انستا - ريلز وستوري
👍 فيسبوك - فيديو بجودة عالية

**شلون بتحمل؟**
1️⃣ ابعتلي رابط الفيديو هون بالخاص
2️⃣ رح ابعتلك الفيديو فوراً بدون علامة

**حركة الكروبات الرهيبة 👇**
بتقدر تحمل باي كروب بدون ما تطلع منو!
اكتب بقلب الكروب:
`@MyDownload2026_bot + رابط الفيديو`
ورح ينبعت الفيديو بالكروب فوراً 😍

جرب هلق ابعتلي أي رابط!
"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("➕ ضيفني لكروبك", url=f"https://t.me/{bot.get_me().username}?startgroup=true"),
        types.InlineKeyboardButton("📢 قناتنا - فيديوهات جاهزة", url="https://t.me/your_channel"),
        types.InlineKeyboardButton("🎬 كيف استخدم الانلاين؟", callback_data="how_inline")
    )
    bot.send_message(m.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "how_inline")
def how_inline(call):
    text = """
🎬 **طريقة الانلاين بالكروبات:**

1. فوت على أي كروب
2. بمكان الكتابة اكتب:
@MyDownload2026_bot https://vm.tiktok.com/xxxx/

3. استنى ثانية رح يطلعلك الفيديو فوق الكيبورد
4. كبوس عليه ورح ينبعت بالكروب

لازم تكون باعت الرابط للبوت بالخاص مرة وحدة قبل، مشان يخزنو!

جرب هلق 👇
@MyDownload2026_bot
"""
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, text, parse_mode="Markdown")
