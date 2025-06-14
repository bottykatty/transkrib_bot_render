import os
import telebot
from telebot import types
import ffmpeg
import openai
import whisper

# Инициализация
TOKEN = os.getenv("TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
bot = telebot.TeleBot(TOKEN)
openai.api_key = OPENAI_API_KEY

# Загружаем tiny-модель
model = whisper.load_model("tiny")

start_text = """🇷🇺 Перешли сюда аудио-сообщение или запиши своё.
🇬🇧 Forward a voice message here or record your own."""

@bot.message_handler(commands=["start"])
def send_start(message):
    bot.send_message(message.chat.id, start_text)

@bot.message_handler(content_types=["voice"])
def handle_voice(message):
    bot.send_message(message.chat.id, "🕐 Обрабатываю...")

    try:
        # Скачиваем и сохраняем файл
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        ogg_file = f"voice_{message.message_id}.ogg"
        mp3_file = f"voice_{message.message_id}.mp3"

        with open(ogg_file, 'wb') as f:
            f.write(downloaded_file)

        ffmpeg.input(ogg_file).output(mp3_file).run(overwrite_output=True)

        # Распознаём речь
        result = model.transcribe(mp3_file)
        original_text = result["text"]
        lang = result["language"]

        # GPT-перевод
        prompt = f"""Переведи следующий текст с сохранением стиля и интонации.
Если он на русском — переведи на английский. Если на английском — переведи на русский.

Текст:
{original_text}
"""
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        translated = response["choices"][0]["message"]["content"]

        reply = f"""🇷🇺 Оригинал / 🇬🇧 Original:
{original_text}

🌐 Перевод / Translation:
{translated}"""

        bot.send_message(message.chat.id, reply)

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
