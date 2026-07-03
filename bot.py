import os
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

from config import TOKEN
from downloader import download_video, download_audio, get_info
from database import add_user, increase, get_stats

user_links = {}
last_time = {}

# 🔒 Anti spam
def anti_spam(user_id):
    now = time.time()
    if user_id in last_time:
        if now - last_time[user_id] < 3:
            return False
    last_time[user_id] = now
    return True


# 🚀 START MENU
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_user(user_id)

    keyboard = [
        [InlineKeyboardButton("📥 تحميل فيديو", callback_data="video")],
        [InlineKeyboardButton("🎵 تحميل صوت", callback_data="audio")],
        [InlineKeyboardButton("📊 إحصائياتي", callback_data="stats")]
    ]

    await update.message.reply_text(
        "🔥 مرحباً بك في MediaX Bot\nأرسل رابط أو اختر من القائمة:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# 📩 استقبال الرابط
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not anti_spam(user_id):
        await update.message.reply_text("⛔ انتظر 3 ثواني قبل إرسال رابط جديد")
        return

    url = update.message.text
    user_links[user_id] = url

    try:
        info = get_info(url)
        title = info.get("title", "Unknown")

        keyboard = [
            [InlineKeyboardButton("🎬 فيديو", callback_data="video")],
            [InlineKeyboardButton("🎵 صوت", callback_data="audio")]
        ]

        await update.message.reply_text(
            f"🎥 {title}\nاختر نوع التحميل:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    except:
        await update.message.reply_text("❌ الرابط غير مدعوم أو غير صالح")


# 🎛️ الأزرار
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    # 📊 Stats
    if data == "stats":
        count = get_stats(user_id)
        await query.edit_message_text(f"📊 عدد التحميلات: {count}")
        return

    url = user_links.get(user_id)

    if not url:
        await query.edit_message_text("ارسل الرابط أولاً")
        return

    # 🎵 AUDIO
    if data == "audio":
        await query.edit_message_text("⏳ جاري تحميل الصوت...")
        file = download_audio(url)
        increase(user_id)

        await query.message.reply_audio(audio=open(file, "rb"))
        os.remove(file)
        return

    # 🎬 VIDEO MENU
    if data == "video":
        keyboard = [
            [InlineKeyboardButton("🔥 Best", callback_data="best")],
            [InlineKeyboardButton("1080p", callback_data="1080")],
            [InlineKeyboardButton("720p", callback_data="720")],
            [InlineKeyboardButton("360p", callback_data="360")]
        ]

        await query.edit_message_text(
            "🎬 اختر الجودة:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # ⬇️ تحميل الفيديو حسب الجودة
    await query.edit_message_text("⏳ جاري التحميل...")

    file = download_video(url, data)
    increase(user_id)

    await query.message.reply_video(video=open(file, "rb"))

    os.remove(file)


# ▶️ تشغيل البوت
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CallbackQueryHandler(buttons))

app.run_polling()
