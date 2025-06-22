"""
Local file processor module for Shaliwood Voice Bot.
Handles local audio file processing for testing purposes.
"""
import logging
import os
from datetime import datetime
from .voice_processor import VoiceProcessor
from .data_manager import DataManager
from .response_formatter import ResponseFormatter
from .hebrew_console import format_hebrew_for_console, format_hebrew_data_for_console

logger = logging.getLogger(__name__)


class LocalProcessor:
    """Handles local audio file processing for testing."""
    
    def __init__(self, voice_processor: VoiceProcessor, data_manager: DataManager, response_formatter: ResponseFormatter):
        """Initialize the local processor."""
        self.voice_processor = voice_processor
        self.data_manager = data_manager
        self.response_formatter = response_formatter
    
    def process_audio_file(self, audio_file_path: str, transcribe_only: bool = False, output_file: str = None):
        """Process a local audio file for testing purposes."""
        if not os.path.exists(audio_file_path):
            logger.error(f"Audio file not found: {audio_file_path}")
            return False
        
        try:
            logger.info(f"Processing local audio file: {audio_file_path}")
            
            # Get file creation date for reference
            file_stat = os.stat(audio_file_path)
            file_creation_time = file_stat.st_ctime
            reference_date = datetime.fromtimestamp(file_creation_time).strftime('%d/%m/%Y')
            logger.info(f"File creation date: {reference_date}")
            
            # Process audio using voice processor
            # Note: save_for_testing=False ensures that voice messages are never saved,
            # regardless of the SAVE_VOICE_MESSAGES environment variable setting
            success, text, workday_data = self.voice_processor.process_audio(
                audio_file_path, save_for_testing=False, reference_date=reference_date
            )
            
            if not success:
                print("❌ Error processing audio file")
                return False
            
            # Format Hebrew text for console display
            formatted_text = format_hebrew_for_console(text)
            print(f"\n📝 Transcription:")
            print(f"{formatted_text}\n")
            
            # Save transcription to file if requested (save original text, not formatted)
            if output_file:
                self._save_transcription_to_file(text, output_file)
            
            # Skip data extraction if transcribe_only is True
            if transcribe_only:
                print("⏭️ Skipping data extraction (transcribe-only mode)")
                return True
            
            # Handle workday data
            self._handle_workday_data(workday_data, text, reference_date)
            
            return True
                
        except Exception as e:
            logger.error(f"Error processing local audio file: {e}")
            print(f"❌ Error processing audio file: {str(e)}")
            return False
    
    def _save_transcription_to_file(self, text: str, output_file: str):
        """Save transcription to file."""
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"💾 Transcription saved to: {output_file}")
        except Exception as e:
            logger.error(f"Failed to save transcription to file: {e}")
            print(f"❌ Failed to save transcription to file: {e}")
    
    def _handle_workday_data(self, workday_data: dict, raw_transcription: str = None, recording_date: str = None):
        """Handle workday data processing and display."""
        if workday_data:
            try:
                # Try to save to sheets
                sheets_available = self.data_manager.is_sheets_available()
                sheets_saved = self.data_manager.save_workday_data(workday_data, raw_transcription, recording_date=recording_date)
                
                # Format Hebrew data for console display
                formatted_data = format_hebrew_data_for_console(workday_data)
                
                # Format and display the result
                result = self.response_formatter.format_console_workday_data(
                    formatted_data, sheets_available, sheets_saved
                )
                print(result)
                    
            except Exception as e:
                logger.error(f"Data processing failed: {e}")
                print(f"❌ Error processing data: {str(e)}")
        else:
            print("⚠️ Data extractor not available") 