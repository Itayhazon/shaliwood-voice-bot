import logging
from typing import Dict, Any, List
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import json
from .config import GOOGLE_SHEETS_CREDENTIALS_FILE, SPREADSHEET_ID

logger = logging.getLogger(__name__)

# Simple custom exception
class StorageError(Exception):
    """Raised when storage operations fail."""
    pass

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Hebrew column mapping for the spreadsheet
HEBREW_COLUMNS = {
    'day': 'יום',
    'date': 'תאריך',
    'recording_date': 'תאריך הקלטה',
    'start_time': 'שעת התחלה',
    'end_time': 'שעת סיום',
    'project_name': 'שם הפרויקט',
    'sub_project': 'תת פרויקט',
    'work_description': 'תיאור העבודה',
    'workers': 'עובדים',
    'additional_notes': 'הערות נוספות',
    'raw_transcription': 'תמלול גולמי',
    'status': 'סטטוס'
}

class GoogleSheetsManager:
    """
    Google Sheets manager for storing workday data.
    """
    
    def __init__(self):
        """Initialize the Google Sheets manager."""
        self.creds = None
        self.service = None
        self._authenticate()
    
    def _authenticate(self) -> None:
        """
        Authenticate with Google Sheets API using service account.
        
        Raises:
            StorageError: If authentication fails
        """
        try:
            if not os.path.exists(GOOGLE_SHEETS_CREDENTIALS_FILE):
                raise StorageError(
                    f"Credentials file '{GOOGLE_SHEETS_CREDENTIALS_FILE}' not found. "
                    "Please download it from Google Cloud Console."
                )
            
            # Use service account credentials
            self.creds = Credentials.from_service_account_file(
                GOOGLE_SHEETS_CREDENTIALS_FILE, 
                scopes=SCOPES
            )
            
            self.service = build('sheets', 'v4', credentials=self.creds)
            logger.info("Google Sheets authentication successful")
            
        except Exception as e:
            logger.error(f"Google Sheets authentication failed: {e}")
            raise StorageError(f"Authentication failed: {e}")
    
    def setup_spreadsheet_headers(self) -> None:
        """
        Set up the spreadsheet with Hebrew headers if they don't exist.
        
        Raises:
            StorageError: If setup fails
        """
        try:
            # Check if headers already exist
            result = self.service.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID,
                range='A1:L1'
            ).execute()
            
            values = result.get('values', [])
            
            if not values or len(values[0]) < 12:
                # Headers don't exist or are incomplete, add them
                headers = list(HEBREW_COLUMNS.values())
                body = {
                    'values': [headers]
                }
                
                self.service.spreadsheets().values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range='A1:L1',
                    valueInputOption='RAW',
                    body=body
                ).execute()
                
                logger.info("Spreadsheet headers set up successfully")
            else:
                logger.info("Spreadsheet headers already exist")
                
        except HttpError as error:
            logger.error(f"Error setting up spreadsheet headers: {error}")
            raise StorageError(f"Headers setup failed: {error}")
        except Exception as e:
            logger.error(f"Unexpected error setting up headers: {e}")
            raise StorageError(f"Headers setup failed: {e}")
    
    def add_workday_summary(self, workday_data: Dict[str, Any]) -> bool:
        """
        Add a new workday summary row to the spreadsheet.
        
        Args:
            workday_data: Dictionary containing the workday information
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            StorageError: If storage operation fails
        """
        try:
            if not workday_data:
                raise StorageError("No workday data provided")
            
            # Prepare the row data in the correct order
            row_data = [
                workday_data.get('day', ''),
                workday_data.get('date', ''),
                workday_data.get('recording_date', ''),
                workday_data.get('start_time', ''),
                workday_data.get('end_time', ''),
                workday_data.get('project_name', ''),
                workday_data.get('sub_project', ''),
                workday_data.get('work_description', ''),
                workday_data.get('workers', ''),
                workday_data.get('additional_notes', ''),
                workday_data.get('raw_transcription', ''),  # Set by business layer
                workday_data.get('status', '⏳ ממתין לאישור')  # Set by business layer
            ]
            
            # Find the next empty row
            result = self.service.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID,
                range='A:A'
            ).execute()
            
            values = result.get('values', [])
            next_row = len(values) + 1
            
            # Add the new row
            body = {
                'values': [row_data]
            }
            
            self.service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=f'A{next_row}:L{next_row}',
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"Successfully added workday summary to row {next_row}")
            return True
            
        except HttpError as error:
            logger.error(f"Error adding workday summary: {error}")
            raise StorageError(f"Data storage failed: {error}")
        except Exception as e:
            logger.error(f"Unexpected error adding workday summary: {e}")
            raise StorageError(f"Data storage failed: {e}")
    
    def get_spreadsheet_info(self) -> Dict[str, Any]:
        """
        Get basic information about the spreadsheet.
        
        Returns:
            Dictionary with spreadsheet information
            
        Raises:
            StorageError: If operation fails
        """
        try:
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=SPREADSHEET_ID
            ).execute()
            
            return {
                'title': spreadsheet['properties']['title'],
                'sheets': [sheet['properties']['title'] for sheet in spreadsheet['sheets']]
            }
        except HttpError as error:
            logger.error(f"Error getting spreadsheet info: {error}")
            raise StorageError(f"Failed to get spreadsheet info: {error}")
        except Exception as e:
            logger.error(f"Unexpected error getting spreadsheet info: {e}")
            raise StorageError(f"Failed to get spreadsheet info: {e}") 