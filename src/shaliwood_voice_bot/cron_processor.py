"""
Cron-based message processor for Shaliwood Voice Bot.
Fetches recent messages from Telegram and processes them in batch.
Note: Only messages from the last 24 hours are accessible due to Telegram API limitations.
"""
import logging
import asyncio
import tempfile
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from telegram import Bot, Update
from telegram.error import TelegramError
from .config import TELEGRAM_TOKEN, SAVE_VOICE_MESSAGES
from .voice_processor import VoiceProcessor
from .data_manager import DataManager
from .response_formatter import ResponseFormatter

logger = logging.getLogger(__name__)


class CronMessageProcessor:
    """Handles batch processing of recent Telegram messages via cron job."""
    
    def __init__(self, voice_processor: VoiceProcessor, data_manager: DataManager, response_formatter: ResponseFormatter):
        """Initialize the cron message processor."""
        self.voice_processor = voice_processor
        self.data_manager = data_manager
        self.response_formatter = response_formatter
        self.bot = Bot(token=TELEGRAM_TOKEN)
        self.last_processed_update_id = 0
        
    async def fetch_and_process_recent_messages(self, hours_back: int = 24) -> Dict[str, Any]:
        """
        Fetch and process recent messages from Telegram.
        
        Args:
            hours_back: How many hours back to look for messages (max 24 due to Telegram limitations)
            
        Returns:
            Dict with processing statistics
        """
        stats = {
            'total_messages': 0,
            'voice_messages': 0,
            'processed_voice': 0,
            'errors': 0,
            'start_time': datetime.now(),
            'messages_processed': []
        }
        
        try:
            logger.info(f"Starting cron message processing for last {hours_back} hours")
            
            # Fetch recent updates
            updates = await self._fetch_recent_updates()
            if not updates:
                logger.info("No recent updates found")
                return stats
            
            stats['total_messages'] = len(updates)
            logger.info(f"Found {len(updates)} recent updates")
            
            # Process each update
            for update in updates:
                try:
                    await self._process_single_update(update, stats)
                except Exception as e:
                    logger.warning(f"Error processing update {update.update_id}: {e}")
                    stats['errors'] += 1
            
            # Update last processed update ID
            if updates:
                self.last_processed_update_id = max(update.update_id for update in updates)
            
            stats['end_time'] = datetime.now()
            stats['duration'] = (stats['end_time'] - stats['start_time']).total_seconds()
            
            logger.info(f"Cron processing completed: {stats['processed_voice']} voice messages processed, {stats['errors']} errors")
            
        except Exception as e:
            logger.error(f"Error in cron message processing: {e}")
            stats['errors'] += 1
            
        return stats
    
    async def _fetch_recent_updates(self) -> List[Update]:
        """Fetch recent updates from Telegram."""
        try:
            # Use offset to avoid processing the same messages multiple times
            offset = self.last_processed_update_id + 1 if self.last_processed_update_id > 0 else None
            
            updates = await self.bot.get_updates(
                offset=offset,
                limit=100,  # Maximum allowed by Telegram
                timeout=1,  # Short timeout for cron job
                allowed_updates=['message']  # Only fetch messages
            )
            
            # Filter for messages from the last 24 hours
            cutoff_time = datetime.now() - timedelta(hours=24)
            recent_updates = []
            
            for update in updates:
                if update.message and update.message.date:
                    if update.message.date > cutoff_time:
                        recent_updates.append(update)
            
            return recent_updates
            
        except TelegramError as e:
            logger.error(f"Telegram API error fetching updates: {e}")
            return []
    
    async def _process_single_update(self, update: Update, stats: Dict[str, Any]):
        """Process a single update (message)."""
        if not update.message:
            return
        
        message = update.message
        
        # Process voice messages
        if message.voice:
            stats['voice_messages'] += 1
            await self._process_voice_message(message, stats)
        else:
            # Log other message types for debugging
            logger.debug(f"Non-voice message from user {message.from_user.id if message.from_user else 'unknown'}")
    
    async def _process_voice_message(self, message, stats: Dict[str, Any]):
        """Process a voice message."""
        temp_file_path = None
        
        try:
            logger.info(f"Processing voice message from user {message.from_user.id if message.from_user else 'unknown'}")
            
            # Download voice file
            file = await self.bot.get_file(message.voice.file_id)
            
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".ogg")
            temp_file_path = temp_file.name
            temp_file.close()
            
            await file.download_to_drive(temp_file_path)
            logger.info(f"Voice file downloaded: {temp_file_path}")
            
            # Extract message date for reference
            message_date = message.date
            reference_date = message_date.strftime('%d/%m/%Y') if message_date else None
            
            # Process audio using voice processor
            user_info = {'user_id': message.from_user.id if message.from_user else 'unknown'}
            success, text, workday_data = self.voice_processor.process_audio(
                temp_file_path, user_info, save_for_testing=SAVE_VOICE_MESSAGES, reference_date=reference_date
            )
            
            if success:
                # Handle workday data
                await self._handle_workday_data_cron(message, workday_data, text)
                stats['processed_voice'] += 1
                
                # Add to processed messages list
                stats['messages_processed'].append({
                    'user_id': user_info['user_id'],
                    'message_date': reference_date,
                    'transcription': text[:100] + "..." if text and len(text) > 100 else text,
                    'has_workday_data': bool(workday_data)
                })
                
                logger.info(f"Successfully processed voice message from user {user_info['user_id']}")
            else:
                logger.warning(f"Failed to process voice message from user {user_info['user_id']}")
                
        except Exception as e:
            logger.error(f"Error processing voice message: {e}")
            stats['errors'] += 1
        finally:
            # Clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    logger.warning(f"Failed to clean up temporary file: {e}")
    
    async def _handle_workday_data_cron(self, message, workday_data: dict, raw_transcription: str = None):
        """Handle workday data processing for cron job (without sending responses)."""
        if workday_data:
            try:
                # Get reference date from the message
                reference_date = None
                if message.date:
                    reference_date = message.date.strftime('%d/%m/%Y')
                
                # Try to save to sheets
                sheets_available = self.data_manager.is_sheets_available()
                sheets_saved = self.data_manager.save_workday_data(workday_data, raw_transcription, recording_date=reference_date)
                
                if sheets_saved:
                    logger.info(f"Workday data saved to sheets for user {message.from_user.id if message.from_user else 'unknown'}")
                else:
                    logger.warning(f"Failed to save workday data to sheets for user {message.from_user.id if message.from_user else 'unknown'}")
                
            except Exception as e:
                logger.error(f"Error saving workday data: {e}")
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get current processing statistics."""
        return {
            'last_processed_update_id': self.last_processed_update_id,
            'bot_token_configured': bool(TELEGRAM_TOKEN),
            'voice_processor_available': self.voice_processor is not None,
            'data_manager_available': self.data_manager is not None
        }


async def run_cron_processing():
    """Main function to run cron processing."""
    from .voice_processor import VoiceProcessor
    from .data_manager import DataManager
    from .response_formatter import ResponseFormatter
    
    # Initialize components
    voice_processor = VoiceProcessor()
    data_manager = DataManager()
    response_formatter = ResponseFormatter()
    
    # Create processor
    processor = CronMessageProcessor(voice_processor, data_manager, response_formatter)
    
    # Run processing
    stats = await processor.fetch_and_process_recent_messages()
    
    # Log results
    logger.info("Cron processing completed:")
    logger.info(f"  - Total messages: {stats['total_messages']}")
    logger.info(f"  - Voice messages: {stats['voice_messages']}")
    logger.info(f"  - Processed voice: {stats['processed_voice']}")
    logger.info(f"  - Errors: {stats['errors']}")
    logger.info(f"  - Duration: {stats.get('duration', 0):.2f} seconds")
    
    return stats


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the cron processing
    asyncio.run(run_cron_processing()) 