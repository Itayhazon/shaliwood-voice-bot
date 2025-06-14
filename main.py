import logging
import os
import tempfile
import openai
import telegram
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

print(">>> TELEGRAM MODULE LOCATION:", telegram.__file__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        voice = update.message.voice
        file = await context.bot.get_file(voice.file_id)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_audio:
            await file.download_to_drive(temp_audio.name)

            with open(temp_audio.name, "rb") as audio_file:
                transcript = openai.Audio.transcribe("whisper-1", audio_file)

            text = transcript["text"]
            await update.message.reply_text(f"הטקסט שזוהה:\n{text}")

    except Exception as e:
        logging.error(f"שגיאה בעיבוד ההקלטה: {e}")
        await update.message.reply_text(f"אירעה שגיאה בעיבוד ההקלטה:\n{e}")

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(MessageHandler(filters.VOICE, handle_voice))
app.run_polling()
