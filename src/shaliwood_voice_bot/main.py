"""
Main application module for Shaliwood Voice Bot.
Orchestrates the bot components and provides the main application loop.
"""
import logging
import sys
import argparse
from .config import LOG_LEVEL, ConfigError
from .voice_processor import VoiceProcessor
from .data_manager import DataManager
from .response_formatter import ResponseFormatter
from .telegram_bot import TelegramBot
from .local_processor import LocalProcessor

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ShaliwoodBot:
    """Main bot application that orchestrates all components."""
    
    def __init__(self, disable_sheets: bool = False):
        """Initialize the bot application."""
        self.voice_processor = VoiceProcessor()
        self.data_manager = DataManager(disable_sheets=disable_sheets)
        self.response_formatter = ResponseFormatter()
        self.telegram_bot = TelegramBot(self.voice_processor, self.data_manager, self.response_formatter)
        self.local_processor = LocalProcessor(self.voice_processor, self.data_manager, self.response_formatter)
    
    def run_telegram_bot(self, use_polling: bool = False):
        """Run the Telegram bot."""
        logger.info("Starting Telegram bot...")
        self.telegram_bot.run(use_polling=use_polling)
    
    def process_local_file(self, audio_file_path: str, transcribe_only: bool = False, output_file: str = None):
        """Process a local audio file."""
        logger.info(f"Processing local file: {audio_file_path}")
        success = self.local_processor.process_audio_file(
            audio_file_path, transcribe_only=transcribe_only, output_file=output_file
        )
        return success


def main():
    """Main entry point with support for local file processing."""
    parser = argparse.ArgumentParser(description='Shaliwood Voice Bot')
    parser.add_argument('--file', '-f', type=str, help='Process a local audio file instead of running the bot')
    parser.add_argument('--no-sheets', action='store_true', help='Skip Google Sheets integration for testing')
    parser.add_argument('--transcribe-only', action='store_true', help='Only transcribe audio, skip data extraction')
    parser.add_argument('--output', '-o', type=str, help='Save transcription to file')
    parser.add_argument('--polling', action='store_true', help='Use polling mode instead of webhook mode (default)')
    
    args = parser.parse_args()
    
    try:
        bot = ShaliwoodBot(disable_sheets=args.no_sheets)
        
        if args.file:
            # Process local audio file
            print(f"🎵 Processing local audio file: {args.file}")
            success = bot.process_local_file(
                args.file, transcribe_only=args.transcribe_only, output_file=args.output
            )
            if success:
                print("✅ Processing completed successfully!")
            else:
                print("❌ Processing failed!")
                sys.exit(1)
        else:
            # Run the Telegram bot
            bot.run_telegram_bot(use_polling=args.polling)
            
    except ConfigError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
