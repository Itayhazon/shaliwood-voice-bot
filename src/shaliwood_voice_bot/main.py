import logging
import tempfile
from openai import OpenAI
import telegram
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from .config import TELEGRAM_TOKEN, OPENAI_API_KEY, ConfigError, LOG_LEVEL

print(">>> TELEGRAM VERSION:", telegram.__version__)

# Configure OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        voice = update.message.voice
        file = await context.bot.get_file(voice.file_id)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_audio:
            await file.download_to_drive(temp_audio.name)

            with open(temp_audio.name, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="he"  # Specify Hebrew language for better transcription
                )

            text = transcript.text
            await update.message.reply_text(f"הטקסט שזוהה:\n{text}")

    except Exception as e:
        logger.error(f"שגיאה בעיבוד ההקלטה: {e}")
        await update.message.reply_text(f"אירעה שגיאה בעיבוד ההקלטה:\n{e}")

def main():
    try:
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app.add_handler(MessageHandler(filters.VOICE, handle_voice))
        logger.info("Starting bot...")
        app.run_polling()
    except ConfigError as e:
        logger.error(f"Configuration error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise

if __name__ == "__main__":
    main()
