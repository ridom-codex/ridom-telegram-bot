import os
import uuid
import tempfile
import telebot
from rembg import remove
from PIL import Image

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# =====================
# PROCESS IMAGE (FIXED)
# =====================
def process_image(message, file_id):

    wait = bot.reply_to(message, "⏳ Processing...")

    input_path = None
    output_path = None

    try:
        file_info = bot.get_file(file_id)
        file_bytes = bot.download_file(file_info.file_path)

        uid = str(uuid.uuid4())
        input_path = os.path.join(tempfile.gettempdir(), uid + ".jpg")
        output_path = os.path.join(tempfile.gettempdir(), uid + ".png")

        # save file
        with open(input_path, "wb") as f:
            f.write(file_bytes)

        # =====================
        # 🔥 MEMORY SAFE FIX
        # =====================
        img = Image.open(input_path).convert("RGBA")

        # reduce size (VERY IMPORTANT)
        img.thumbnail((600, 600))

        # background remove
        result = remove(img)

        # save output
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
            bot.delete_message(message.chat.id, wait.message_id)
        except:
            pass

        for f in [input_path, output_path]:
            try:
                if f and os.path.exists(f):
                    os.remove(f)
            except:
                pass


@bot.message_handler(content_types=["photo"])
def photo(message):
    file_id = message.photo[-1].file_id
    process_image(message, file_id)

print("Bot running...")
bot.infinity_polling(skip_pending=True)
