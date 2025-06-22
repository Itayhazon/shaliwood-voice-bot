"""
Voice processing module for Shaliwood Voice Bot.
Handles audio transcription and data extraction only.
"""
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from openai import OpenAI
from .config import OPENAI_API_KEY, VOICE_SAVE_DIR
from .data_extractor import WorkdayDataExtractor

logger = logging.getLogger(__name__)


class VoiceProcessor:
    """Handles audio transcription and data extraction."""
    
    def __init__(self):
        """Initialize the voice processor."""
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        self.data_extractor = None
        
        try:
            self.data_extractor = WorkdayDataExtractor()
            logger.info("Data extractor initialized")
        except Exception as e:
            logger.warning(f"Data extractor not available: {e}")
    
    def process_audio(self, audio_file_path: str, user_info: dict = None, save_for_testing: bool = False, reference_date: str = None):
        """
        Core audio processing pipeline.
        
        Args:
            audio_file_path: Path to the audio file to process
            user_info: Dictionary with user information (for Telegram messages)
            save_for_testing: Whether to save the voice message for testing (decided by caller)
            reference_date: Reference date in DD/MM/YYYY format for data extraction
            
        Returns:
            tuple: (success: bool, text: str, workday_data: dict)
        """
        try:
            logger.info(f"Processing audio file: {audio_file_path}")
            
            # Save voice message for testing if enabled (decided by caller)
            if save_for_testing:
                self._save_voice_for_testing(audio_file_path, user_info)
            
            # Transcribe audio
            text = self._transcribe_audio(audio_file_path)
            if not text:
                return False, None, None
            
            # Extract workday data
            workday_data = self._extract_workday_data(text, reference_date)
            
            return True, text, workday_data
                
        except Exception as e:
            logger.error(f"Error in audio processing: {e}")
            return False, None, None
    
    def _save_voice_for_testing(self, audio_file_path: str, user_info: dict = None):
        """Save voice message for testing purposes."""
        try:
            # Create save directory if it doesn't exist
            save_dir = Path(VOICE_SAVE_DIR)
            save_dir.mkdir(exist_ok=True)
            
            # Generate filename with timestamp and user info
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            user_id = user_info.get('user_id', 'unknown') if user_info else 'unknown'
            filename = f"voice_{user_id}_{timestamp}.ogg"
            save_path = save_dir / filename
            
            # Copy the file to the save directory
            shutil.copy2(audio_file_path, save_path)
            logger.info(f"Voice message saved for testing: {save_path}")
            
        except Exception as e:
            logger.warning(f"Failed to save voice message for testing: {e}")
    
    def _transcribe_audio(self, audio_file_path: str) -> str:
        """Transcribe audio file using OpenAI Whisper."""
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="he"
                )
            
            text = transcript.text
            logger.info(f"Audio transcribed: {len(text)} characters")
            return text
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return None
    
    def _extract_workday_data(self, text: str, reference_date: str = None) -> dict:
        """Extract workday data from transcribed text."""
        if not self.data_extractor:
            return None
        
        try:
            # Extract structured data from OpenAI
            workday_data = self.data_extractor.extract_workday_data(text, reference_date)
            
            logger.info(f"Workday data extracted: {len(workday_data)} fields")
            return workday_data
        except Exception as e:
            logger.error(f"Data extraction failed: {e}")
            return None 