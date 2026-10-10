async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_subscribed(context.bot, update.effective_user.id):
        await update.message.reply_text("⚠️ اشترك أولاً", reply_markup=get_sub_keyboard())
        return

    url = update.message.text.strip()
    if "http" not in url:
        return

    msg = await update.message.reply_text("⏳ عم حل الرابط...")
    
    try:
        # 1- فك الرابط المختصر vm.tiktok.com
        original_url = url
        if "vm.tiktok.com" in url or "vt.tiktok.com" in url:
            try:
                r = requests.get(url, allow_redirects=True, timeout=15, 
                                 headers={"User-Agent": "Mozilla/5.0"})
                url = r.url
                print(f"تم فك الرابط: {original_url} -> {url}")
            except Exception as e:
                print(f"فشل فك الرابط: {e}")

        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=msg.message_id,
            text="⚡️ عم نزّل الفيديو..."
        )
        await context.bot.send_chat_action(update.effective_chat.id, "upload_video")

        # --- المحاولة 1: API جديد قوي ---
        if "tiktok.com" in url:
            try:
                # API بديل ما بينحظر على Render
                headers = {"User-Agent": "Mozilla/5.0"}
                api_url = f"https://www.tikwm.com/api/?url={url}&hd=1"
                res = requests.get(api_url, headers=headers, timeout=20).json()
                
                if res.get("code") == 0:
                    video_url = res["data"].get("play") or res["data"].get("hdplay")
                    if video_url:
                        await context.bot.delete_message(update.effective_chat.id, msg.message_id)
                        await update.message.reply_video(
                            video=video_url,
                            caption="✅ بدون علامة مائية\n📢 @BotKanal24"
                        )
                        return
            except Exception as e:
                print(f"TikWM Fail: {e}")

            # --- المحاولة 2: API تاني احتياطي ---
            try:
                api2 = f"https://tikcdn.io/api/download?url={url}"
                res2 = requests.get(api2, timeout=20).json()
                if res2.get("video"):
                    await context.bot.delete_message(update.effective_chat.id, msg.message_id)
                    await update.message.reply_video(video=res2["video"], caption="✅ @BotKanal24")
                    return
            except Exception as e:
                print(f"API2 Fail: {e}")

        # --- المحاولة 3: yt-dlp (الحل الأخير) ---
        with tempfile.TemporaryDirectory() as tmpdir:
            opts = {
                'outtmpl': f'{tmpdir}/video.%(ext)s',
                'format': 'best[ext=mp4]/best',
                'quiet': True,
                'no_warnings': True,
                'noplaylist': True,
                'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                path = ydl.prepare_filename(info)
            
            await context.bot.delete_message(update.effective_chat.id, msg.message_id)
            with open(path, 'rb') as f:
                await update.message.reply_video(video=f, caption=f"✅ تم التحميل\n📢 {CHANNEL}")

    except Exception as e:
        print(f"FINAL ERROR: {e}")
        try:
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=msg.message_id,
                text=f"❌ ما قدرت حملو\nالسبب: {str(e)[:100]}\nجرب رابط تاني"
            )
        except:
            pass
