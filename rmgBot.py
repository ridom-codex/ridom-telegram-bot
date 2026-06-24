import os
import uuid
import tempfile
import logging
import telebot
from rembg import remove

# =====================
# BOT TOKEN
# =====================
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# =====================
# LOGGING
# =====================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# =====================
# STATS
# =====================
total_processed = 0
users = set()

# =====================
# START
# =====================
@bot.message_handler(commands=["start"])
def start(message):
    users.add(message.from_user.id)
    bot.reply_to(
        message,
        "👋 <b>Welcome!</b>\n\n📸 আমাকে ছবি পাঠাও\n🤖 আমি ব্যাকগ্রাউন্ড রিমুভ করে দিব"
    )

# =====================
# HELP
# =====================
@bot.message_handler(commands=["help"])
def help_cmd(message):
    bot.reply_to(
        message,
        "📌 শুধু ছবি পাঠাও\nআমি অটোমেটিক ব্যাকগ্রাউন্ড রিমুভ করব"
    )

# =====================
# IMAGE PROCESS FUNCTION
# =====================
def process_image(message, file_id):

    global total_processed

    wait_msg = bot.reply_to(message, "⏳ প্রসেস করা হচ্ছে...")

    try:
        file_info = bot.get_file(file_id)
        file_bytes = bot.download_file(file_info.file_path)

        uid = str(uuid.uuid4())

        input_path = os.path.join(tempfile.gettempdir(), uid + ".png")
        output_path = os.path.join(tempfile.gettempdir(), uid + "_out.png")

        with open(input_path, "wb") as f:
            f.write(file_bytes)

        with open(input_path, "rb") as inp:
            result = remove(inp.read())

        with open(output_path, "wb") as out:
            out.write(result)

        with open(output_path, "rb") as final:
            bot.send_document(
                message.chat.id,
                final,
                caption="✅ ব্যাকগ্রাউন্ড রিমুভ করা হয়েছে"
            )

        total_processed += 1

    except Exception as e:
        logging.error(e)
        bot.reply_to(message, f"❌ Error: {e}")

    finally:
        try:
            bot.delete_message(message.chat.id, wait_msg.message_id)
        except:
            pass

        for file in [input_path, output_path]:
            try:
                if os.path.exists(file):
                    os.remove(file)
            except:
                pass

# =====================
# PHOTO HANDLER
# =====================
@bot.message_handler(content_types=["photo"])
def photo(message):
    file_id = message.photo[-1].file_id
    process_image(message, file_id)

# =====================
# DOCUMENT HANDLER
# =====================
@bot.message_handler(content_types=["document"])
def doc(message):
    if message.document.mime_type.startswith("image/"):
        process_image(message, message.document.file_id)
    else:
        bot.reply_to(message, "❌ শুধু ছবি পাঠাও")

# =====================
# DEFAULT
# =====================
@bot.message_handler(func=lambda m: True)
def default(message):
    bot.reply_to(message, "📸 শুধু একটি ছবি পাঠাও")

# =====================
# START BOT
# =====================
print("Bot is running...")

bot.infinity_polling(skip_pending=True)
