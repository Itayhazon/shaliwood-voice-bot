"""
Response formatter module for Shaliwood Voice Bot.
Handles message formatting for different contexts.
"""
import logging

logger = logging.getLogger(__name__)


class ResponseFormatter:
    """Handles response formatting for different contexts."""
    
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
    
    @staticmethod
    def format_complete_workday_data(workday_data: dict, sheets_available: bool = False, sheets_saved: bool = False) -> str:
        """Format complete workday data from the current recording for display."""
        if not workday_data:
            return "⚠️ מערכת חילוץ המידע לא זמינה"
        
        # Status message based on sheets availability
        if sheets_available and sheets_saved:
            status_msg = "✅ המידע נוסף בהצלחה לגיליון האלקטרוני!"
        elif sheets_available and not sheets_saved:
            status_msg = "❌ שגיאה בהוספת המידע לגיליון האלקטרוני"
        else:
            status_msg = "📊 המידע שחולץ (Google Sheets לא זמין)"
        
        # Format all extracted information
        result = f"{status_msg}\n\n"
        result += "📋 המידע שחולץ מההקלטה:\n\n"
        
        # Add all extracted fields
        result += f"📅 תאריך: {workday_data.get('date', 'לא צוין')}\n"
        result += f"🏗️ פרויקט: {workday_data.get('project_name', 'לא צוין')}\n"
        result += f"🔧 תת פרויקט: {workday_data.get('sub_project', 'לא צוין')}\n"
        result += f"👷 עובדים: {workday_data.get('workers', 'לא צוין')}\n"
        result += f"⏰ שעות: {workday_data.get('start_time', '')} - {workday_data.get('end_time', '')}\n"
        result += f"📝 תיאור העבודה: {workday_data.get('work_description', 'לא צוין')}\n"
        result += f"📌 הערות נוספות: {workday_data.get('additional_notes', 'לא צוין')}\n"
        
        return result 