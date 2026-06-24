import os
import telebot
from rembg import remove

# এখানে নিজের Telegram Bot Token বসাও
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "📸 একটি ছবি পাঠাও, আমি ব্যাকগ্রাউন্ড রিমুভ করে PNG পাঠিয়ে দেব।"
    )

@bot.message_handler(content_types=['photo'])
def remove_background(message):
    try:
        # সবচেয়ে বড় সাইজের ছবিটি নেওয়া
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        input_path = "input.jpg"
        output_path = "output.png"

        # ইনপুট ছবি সেভ
        with open(input_path, "wb") as f:
            f.write(downloaded_file)

        # ব্যাকগ্রাউন্ড রিমুভ
        with open(input_path, "rb") as inp:
            input_data = inp.read()

        output_data = remove(input_data)

        with open(output_path, "wb") as out:
            out.write(output_data)

        # PNG পাঠানো
        with open(output_path, "rb") as photo:
            bot.send_document(
                message.chat.id,
                photo,
                visible_file_name="background_removed.png"
            )

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

    finally:
        # অস্থায়ী ফাইল ডিলিট
        for file in ["input.jpg", "output.png"]:
            if os.path.exists(file):
                os.remove(file)

print("Bot is running...")
bot.infinity_polling()