"""
Response formatter module for Shaliwood Voice Bot.
Handles message formatting for different contexts.
"""
import logging

logger = logging.getLogger(__name__)


class ResponseFormatter:
    """Handles response formatting for different contexts."""
    
    @staticmethod
    def format_workday_summary(workday_data: dict, sheets_available: bool = False, sheets_saved: bool = False) -> str:
        """Format workday data for display."""
        if not workday_data:
            return "⚠️ מערכת חילוץ המידע לא זמינה"
        
        # Base data display
        data_display = (
            f"📅 תאריך: {workday_data.get('date', 'לא צוין')}\n"
            f"🏗️ פרויקט: {workday_data.get('project_name', 'לא צוין')}\n"
            f"👷 עובדים: {workday_data.get('workers', 'לא צוין')}\n"
            f"⏰ שעות: {workday_data.get('start_time', '')} - {workday_data.get('end_time', '')}"
        )
        
        # Add appropriate header based on context
        if sheets_available and sheets_saved:
            return f"✅ המידע נוסף בהצלחה לגיליון האלקטרוני!\n\n{data_display}"
        elif sheets_available and not sheets_saved:
            return f"❌ שגיאה בהוספת המידע לגיליון האלקטרוני\n\n{data_display}"
        else:
            return f"📊 המידע שחולץ (Google Sheets לא זמין):\n\n{data_display}"
    
    @staticmethod
    def format_console_workday_data(workday_data: dict, sheets_available: bool = False, sheets_saved: bool = False) -> str:
        """Format workday data for console display."""
        if not workday_data:
            return "⚠️ Data extractor not available"
        
        # Display extracted data
        result = "📊 Extracted Data:\n"
        for key, value in workday_data.items():
            result += f"  {key}: {value}\n"
        result += "\n"
        
        # Add status message
        if sheets_available and sheets_saved:
            result += "✅ Data successfully added to Google Sheets!"
        elif sheets_available and not sheets_saved:
            result += "❌ Error adding data to Google Sheets"
        else:
            result += "📊 Data extracted successfully (Google Sheets disabled)"
        
        return result 