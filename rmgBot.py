import os
import uuid
import requests
import telebot
from PIL import Image
import tempfile

# =====================
# CONFIG
# =====================
BOT_TOKEN = os.getenv("BOT_TOKEN")
REMOVE_BG_API = os.getenv("REMOVE_BG_API")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# =====================
# START
# =====================
@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "👋 Welcome!\n\n📸 আমাকে ছবি পাঠাও\n🤖 আমি background remove করে দিব"
    )

# =====================
# PROCESS IMAGE (API)
# =====================
def process_image(message, file_id):

    wait = bot.reply_to(message, "⏳ প্রসেস করা হচ্ছে...")

    try:
        file_info = bot.get_file(file_id)
        file_bytes = bot.download_file(file_info.file_path)

        uid = str(uuid.uuid4())

        input_path = os.path.join(tempfile.gettempdir(), uid + ".jpg")
        output_path = os.path.join(tempfile.gettempdir(), uid + ".png")

        # save image
        with open(input_path, "wb") as f:
            f.write(file_bytes)

        # =====================
        # CALL REMOVE.BG API
        # =====================
        response = requests.post(
            "https://api.remove.bg/v1.0/removebg",
            files={"image_file": open(input_path, "rb")},
            data={"size": "auto"},
            headers={"X-Api-Key": REMOVE_BG_API},
        )

        if response.status_code != 200:
            bot.reply_to(message, "❌ API Error: Limit বা Key সমস্যা")
            return

        with open(output_path, "wb") as out:
            out.write(response.content)

        # send result
        with open(output_path, "rb") as photo:
            bot.send_document(
                message.chat.id,
                photo,
                caption="✅ Background removed successfully"
            )

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

    finally:
        try:
            bot.delete_message(message.chat.id, wait.message_id)
        except:
            pass

# =====================
# PHOTO
# =====================
@bot.message_handler(content_types=["photo"])
def photo(message):
    file_id = message.photo[-1].file_id
    process_image(message, file_id)

# =====================
# DOCUMENT
# =====================
@bot.message_handler(content_types=["document"])
def doc(message):
    if message.document.mime_type.startswith("image/"):
        process_image(message, message.document.file_id)
    else:
        bot.reply_to(message, "❌ শুধু ছবি পাঠাও")

# =====================
# RUN
# =====================
print("Bot running...")
bot.infinity_polling(skip_pending=True)
