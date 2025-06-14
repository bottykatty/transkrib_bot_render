import telebot
from telebot import types
import os
import whisper
from translatepy import Translator

TOKEN = "8140428860:AAEBJX7uIG4UcjsheW9VMiP_wJkIGnOdHY0"
bot = telebot.TeleBot(TOKEN)
model = whisper.load_model("base")
translator = Translator()

start_text = """🇷🇺 Перешли сюда аудио-сообщение или запиши своё.
🇬🇧 Forward a voice message here or record your own."""

@bot.message_handler(commands=["start"])
def send_start(message):
    bot.send_message(message.chat.id, start_text)

@bot.message_handler(content_types=["voice"])
def handle_voice(message):
    bot.send_message(message.chat.id, "🕐 Обрабатываю...")

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
        original_text = result["text"]
        lang = result["language"]

        try:
            translated = translator.translate(
                original_text, "English" if lang == "ru" else "Russian"
            ).result
        except Exception:
            translated = "❌ Перевести не удалось. Попробуй позже."

        response = f"""🇷🇺 Вот оригинальный текст аудио / 🇬🇧 Here's the original audio text:
{original_text}

🇷🇺 А вот перевод / 🇬🇧 And here’s the translation:
{translated}"""

        bot.send_message(message.chat.id, response)

        os.remove(ogg_file)
        os.remove(mp3_file)

    except Exception as e:
        print("Ошибка:", e)
        bot.send_message(message.chat.id, "❌ Что-то пошло не так. Попробуй ещё раз.")

@bot.message_handler(func=lambda m: True)
def fallback(message):
    bot.send_message(
        message.chat.id,
        "🇷🇺 Я не понимаю текст. Запиши голосовое — я переведу его.\n"
        "🇬🇧 I don't understand text. Send me voice — I'll translate it."
    )

print("🤖 Бот запущен")
bot.infinity_polling()
