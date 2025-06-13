import telebot
from telebot import types
import os
import whisper
import ffmpeg
from googletrans import Translator

# 🔑 Твой Telegram API Token
TOKEN = '8140428860:AAEBJX7uIG4UcjsheW9VMiP_wJkIGnOdHY0'

bot = telebot.TeleBot(TOKEN)
model = whisper.load_model("base")
translator = Translator()

# 🟢 Сообщение после команды /start
start_text = """🇷🇺 Перешли сюда аудио-сообщение или запиши своё.
🇬🇧 Forward a voice message here or record your own."""

# ❌ Сообщение если прислали не аудио
wrong_format_text = """🇷🇺 Я не понимаю текст, запиши аудио и я переведу его.
🇬🇧 I don’t understand text, please send me a voice message and I’ll translate it."""

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, start_text)

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    bot.send_message(message.chat.id, "🇷🇺 Процесс запущен. Жди готовый файл.\n🇬🇧 Process started. Please wait for the final file.")
    
    try:
        # Скачиваем голосовое сообщение
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        ogg_file = f"voice_{message.message_id}.ogg"
        mp3_file = f"voice_{message.message_id}.mp3"
        
        with open(ogg_file, 'wb') as f:
            f.write(downloaded_file)

        # Конвертация в mp3
        ffmpeg.input(ogg_file).output(mp3_file).run(overwrite_output=True)

        # Распознавание речи
        result = model.transcribe(mp3_file)
        original_text = result["text"]

        # Перевод
        translated = translator.translate(original_text, src='auto', dest='ru' if result['language'] == 'en' else 'en').text

        # Ответ пользователю в нужном формате
        response = f"🇷🇺 Вот оригинальный текст аудио / 🇬🇧 Here's the original audio text:\n{original_text}\n\n" \
                   f"🇷🇺 А вот перевод / 🇬🇧 And here’s the translation:\n{translated}"
        
        bot.send_message(message.chat.id, response)

        # Удаление временных файлов
        os.remove(ogg_file)
        os.remove(mp3_file)

    except Exception as e:
        print("Error:", e)
        bot.send_message(message.chat.id, "❌ Что-то пошло не так. Попробуй ещё раз.")

# Любой другой тип сообщения → ошибка
@bot.message_handler(func=lambda m: True, content_types=['text', 'audio', 'video', 'photo', 'document', 'sticker', 'location', 'contact'])
def wrong_format(message):
    bot.send_message(message.chat.id, wrong_format_text)

# ▶️ Запуск
print("🤖 Бот запущен")
bot.infinity_polling()
