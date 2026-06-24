import os
import uuid
import tempfile
import requests
import telebot

# =====================
# CONFIG
# =====================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CLIPDROP_API_KEY = os.getenv("CLIPDROP_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# =====================
# START
# =====================
@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "👋 <b>Welcome!</b>\n\n📸 ছবি পাঠাও\n🤖 আমি background remove করে দিব (Clipdrop API)"
    )

# =====================
# PROCESS IMAGE
# =====================
def process_image(message, file_id):

    wait_msg = bot.reply_to(message, "⏳ প্রসেস করা হচ্ছে...")

    input_path = None
    output_path = None

    try:
        # get image from telegram
        file_info = bot.get_file(file_id)
        file_bytes = bot.download_file(file_info.file_path)

        uid = str(uuid.uuid4())
        input_path = os.path.join(tempfile.gettempdir(), uid + ".jpg")
        output_path = os.path.join(tempfile.gettempdir(), uid + "_out.png")

        # save input image
        with open(input_path, "wb") as f:
            f.write(file_bytes)

        # =====================
        # CLIPDROP API CALL
        # =====================
        with open(input_path, "rb") as img:
            response = requests.post(
                "https://clipdrop-api.co/remove-background/v1",
                files={"image_file": img},
                headers={"x-api-key": CLIPDROP_API_KEY},
                timeout=60
            )

        # error check
        if response.status_code != 200:
            bot.reply_to(
                message,
                f"❌ API Error:\n{response.text}"
            )
            return

        # save result
        with open(output_path, "wb") as out:
            out.write(response.content)

        # send result
        with open(output_path, "rb") as photo:
            bot.send_document(
                message.chat.id,
                photo,
                caption="✅ Background সফলভাবে remove করা হয়েছে (Clipdrop)"
            )

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

    finally:
        try:
            bot.delete_message(message.chat.id, wait_msg.message_id)
        except:
            pass

        for file in [input_path, output_path]:
            try:
                if file and os.path.exists(file):
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
    if message.document.mime_type and message.document.mime_type.startswith("image/"):
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
# RUN BOT
# =====================
print("Bot is running...")

bot.infinity_polling(skip_pending=True)
