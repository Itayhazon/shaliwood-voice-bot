"""
Data management module for Shaliwood Voice Bot.
Handles Google Sheets operations and data persistence.
"""
import logging
from .sheets import GoogleSheetsManager

logger = logging.getLogger(__name__)


class DataManager:
    """Handles data persistence operations."""
    
    def __init__(self, disable_sheets: bool = False):
        """Initialize the data manager."""
        self.sheets_manager = None
        
        if not disable_sheets:
            try:
                self.sheets_manager = GoogleSheetsManager()
                self.sheets_manager.setup_spreadsheet_headers()
                logger.info("Google Sheets initialized")
            except Exception as e:
                logger.warning(f"Google Sheets not available: {e}")
        else:
            logger.info("Google Sheets disabled for testing")
    
    def save_workday_data(self, workday_data: dict, raw_transcription: str = None, recording_date: str = None) -> bool:
        """
        Save workday data to Google Sheets.
        
        Args:
            workday_data: Dictionary containing extracted workday information
            raw_transcription: Raw transcription text (optional)
            recording_date: Date when the voice message was recorded (optional)
        """
        if not self.sheets_manager or not workday_data:
            return False
        
        try:
            # Enrich workday data with business-specific fields
            enriched_data = workday_data.copy()
            
            # Add raw transcription if provided
            if raw_transcription:
                enriched_data['raw_transcription'] = raw_transcription
            
            # Add recording date if provided
            if recording_date:
                enriched_data['recording_date'] = recording_date
            
            # Add default status
            enriched_data['status'] = '⏳ ממתין לאישור'
            
            success = self.sheets_manager.add_workday_summary(enriched_data)
            return success
        except Exception as e:
            logger.warning(f"Failed to save to sheets: {e}")
            return False
    
    def is_sheets_available(self) -> bool:
        """Check if Google Sheets is available."""
        return self.sheets_manager is not None 