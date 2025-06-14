import telebot
from telebot import types
import os
import whisper

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

# Используем лёгкую модель
model = whisper.load_model("tiny")

start_text = """🎙 Отправь голосовое — я превращу его в текст!
Send me a voice message — I'll transcribe it."""

@bot.message_handler(commands=["start"])
def send_start(message):
    bot.send_message(message.chat.id, start_text)

@bot.message_handler(content_types=["voice"])
def handle_voice(message):
    bot.send_message(message.chat.id, "🕐 Распознаю...")

    try:
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        ogg_file = f"voice_{message.message_id}.ogg"
        mp3_file = f"voice_{message.message_id}.mp3"

        with open(ogg_file, 'wb') as f:
            f.write(downloaded_file)

        import ffmpeg
        ffmpeg.input(ogg_file).output(mp3_file).run(overwrite_output=True)

        result = model.transcribe(mp3_file)
        text = result["text"]

        bot.send_message(message.chat.id, f"📝 Вот что я услышал:\n{text}")

        os.remove(ogg_file)
        os.remove(mp3_file)

    except Exception as e:
        print("Ошибка:", e)
        bot.send_message(message.chat.id, "❌ Что-то пошло не так. Попробуй ещё раз.")

@bot.message_handler(func=lambda m: True)
def fallback(message):
    bot.send_message(message.chat.id, start_text)

print("🤖 Бот запущен")
bot.infinity_polling()