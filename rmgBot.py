import os
import uuid
import tempfile
import telebot
from rembg import remove
from PIL import Image

# =====================
# BOT TOKEN
# =====================
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# =====================
# START
# =====================
@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "👋 Welcome!\n\n📸 ছবি পাঠাও\n🤖 আমি background remove করে দিব"
    )

# =====================
# PROCESS IMAGE
# =====================
def process_image(message, file_id):

    wait_msg = bot.reply_to(message, "⏳ Processing...")

    input_path = None
    output_path = None

    try:
        file_info = bot.get_file(file_id)
        file_bytes = bot.download_file(file_info.file_path)

        uid = str(uuid.uuid4())
        input_path = os.path.join(tempfile.gettempdir(), uid + ".jpg")
        output_path = os.path.join(tempfile.gettempdir(), uid + ".png")

        # save input
        with open(input_path, "wb") as f:
            f.write(file_bytes)

        # =====================
        # SAFE IMAGE PROCESS
        # =====================
        img = Image.open(input_path).convert("RGBA")

        # memory safe resize
        img.thumbnail((600, 600))

        result = remove(img)
        result.save(output_path)

        # send result
        with open(output_path, "rb") as out:
            bot.send_document(
                message.chat.id,
                out,
                caption="✅ Background removed successfully"
            )

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

    finally:
        try:
            bot.delete_message(message.chat.id, wait_msg.message_id)
        except:
            pass

        for f in [input_path, output_path]:
            try:
                if f and os.path.exists(f):
                    os.remove(f)
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
# RUN BOT (NO PORT NEEDED)
# =====================
print("Bot running...")

bot.infinity_polling(skip_pending=True)
