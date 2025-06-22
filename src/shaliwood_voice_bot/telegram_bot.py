"""
Telegram bot module for Shaliwood Voice Bot.
Handles Telegram-specific operations and message handling.
"""
import logging
import tempfile
import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from .config import TELEGRAM_TOKEN
from .voice_processor import VoiceProcessor
from .data_manager import DataManager
from .response_formatter import ResponseFormatter

logger = logging.getLogger(__name__)


class TelegramBot:
    """Handles Telegram bot operations."""
    
    def __init__(self, voice_processor: VoiceProcessor, data_manager: DataManager, response_formatter: ResponseFormatter):
        """Initialize the Telegram bot."""
        self.voice_processor = voice_processor
        self.data_manager = data_manager
        self.response_formatter = response_formatter
        self.application = None
    
    async def handle_voice_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming voice message from Telegram."""
        temp_file_path = None
        
        try:
            # Validate input
            if not update.message or not update.message.voice:
                logger.error("Invalid voice message received")
                return
            
            # Extract message date for reference
            message_date = update.message.date
            reference_date = message_date.strftime('%d/%m/%Y') if message_date else None
            logger.info(f"Voice message date: {reference_date}")
            
            # Download voice file
            voice = update.message.voice
            file = await context.bot.get_file(voice.file_id)
            
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".ogg")
            temp_file_path = temp_file.name
            temp_file.close()
            
            await file.download_to_drive(temp_file_path)
            logger.info(f"Voice file downloaded: {temp_file_path}")
            
            # Process audio using voice processor
            user_info = {'user_id': update.message.from_user.id if update.message.from_user else 'unknown'}
            success, text, workday_data = self.voice_processor.process_audio(
                temp_file_path, user_info, save_for_testing=True, reference_date=reference_date
            )
            
            if not success:
                await update.message.reply_text("שגיאה בעיבוד ההקלטה")
                return
            
            # Send transcription
            await update.message.reply_text(f"הטקסט שזוהה:\n{text}")
            
            # Handle workday data
            await self._handle_workday_data(update, workday_data)
                
        except Exception as e:
            logger.error(f"Error processing voice message: {e}")
            await update.message.reply_text(f"שגיאה בעיבוד ההקלטה: {str(e)}")
        finally:
            # Clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                    logger.debug(f"Temporary file cleaned up: {temp_file_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean up temporary file: {e}")
    
    async def _handle_workday_data(self, update: Update, workday_data: dict):
        """Handle workday data processing and response."""
        if workday_data:
            try:
                # Try to save to sheets
                sheets_available = self.data_manager.is_sheets_available()
                sheets_saved = self.data_manager.save_workday_data(workday_data)
                
                # Format and send the response message
                message = self.response_formatter.format_workday_summary(
                    workday_data, sheets_available, sheets_saved
                )
                await update.message.reply_text(message)
                
            except Exception as e:
                logger.warning(f"Data processing failed: {e}")
                await update.message.reply_text(f"שגיאה בעיבוד המידע: {str(e)}")
        else:
            await update.message.reply_text("⚠️ מערכת חילוץ המידע לא זמינה")
    
    def setup_handlers(self):
        """Setup message handlers."""
        self.application.add_handler(
            MessageHandler(filters.VOICE, self.handle_voice_message)
        )
    
    def run(self):
        """Run the Telegram bot."""
        try:
            # Create application
            self.application = Application.builder().token(TELEGRAM_TOKEN).build()
            
            # Setup handlers
            self.setup_handlers()
            
            logger.info("Starting Shaliwood Voice Bot...")
            self.application.run_polling()
            
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Bot runtime error: {e}")
            raise 