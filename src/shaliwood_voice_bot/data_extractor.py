import logging
from typing import Dict, Any, Optional
from openai import OpenAI
from .config import OPENAI_API_KEY
import json
from datetime import datetime

logger = logging.getLogger(__name__)

# Simple custom exception
class DataExtractionError(Exception):
    """Raised when data extraction fails."""
    pass

class WorkdayDataExtractor:
    """
    AI-powered workday data extractor.
    """
    
    def __init__(self):
        """
        Initialize the data extractor.
        
        Raises:
            DataExtractionError: If initialization fails
        """
        try:
            self.client = OpenAI(api_key=OPENAI_API_KEY)
            logger.info("Workday data extractor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize workday data extractor: {e}")
            raise DataExtractionError(f"Data extractor initialization failed: {e}")
    
    def extract_workday_data(self, transcribed_text: str, reference_date: str = None) -> Dict[str, Any]:
        """
        Extract structured workday data from transcribed Hebrew text.
        
        Args:
            transcribed_text: The transcribed Hebrew text describing the workday
            reference_date: Reference date in DD/MM/YYYY format for resolving relative expressions
            
        Returns:
            Dictionary containing structured workday data
            
        Raises:
            DataExtractionError: If extraction fails
        """
        try:
            if not transcribed_text or not transcribed_text.strip():
                raise DataExtractionError("Empty or invalid transcribed text provided")
            
            # Use current date as fallback if no reference date provided
            if not reference_date:
                reference_date = datetime.now().strftime('%d/%m/%Y')
                logger.info(f"No reference date provided, using current date: {reference_date}")
            else:
                logger.info(f"Using provided reference date for extraction: {reference_date}")
            
            # Create a prompt for OpenAI to extract structured data
            prompt = self._create_extraction_prompt(transcribed_text, reference_date)
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "אתה מומחה בחילוץ מידע מובנה מטקסטים בעברית עבור חברות בנייה. תמיד החזר תשובה בפורמט JSON תקף."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.0,
                max_tokens=1000
            )

            # Extract the JSON response
            content = response.choices[0].message.content.strip()
            
            # Parse and validate the response
            workday_data = self._parse_json_response(content)
            validated_data = self._validate_and_clean_data(workday_data)
            
            logger.info("Successfully extracted workday data from transcription")
            return validated_data
                
        except Exception as e:
            logger.error(f"Error extracting workday data: {e}")
            return self._create_fallback_data(transcribed_text)
    

    def _create_extraction_prompt(self, text: str, reference_date: str) -> str:
        """
        Create the extraction prompt for OpenAI.
        
        Args:
            text: Transcribed text
            reference_date: Reference date in DD/MM/YYYY format
            
        Returns:
            Formatted prompt string
        """
        return f"""
        You are an assistant helping a construction company named "Shalevud" that specializes in roofing.

        Your task is to extract structured information from a daily work report written in Hebrew.

        Input text:  
        {text}

        Reference date: {reference_date} (in DD/MM/YYYY format)

        Use the reference date to resolve relative expressions like "אתמול" or "היום".  
        
        The text may include **relative time expressions** such as:
        - "היום" (today)
        - "אתמול" (yesterday)
        - "מחר" (tomorrow)
        - "שלשום" or "לפני יומיים" (the day before yesterday)
        - "לפני שלושה ימים" (three days ago)

        You must resolve these expressions based on the provided reference date.  
        For example, if the reference date is `"21/06/2025"`, then:
        - "היום" → `21/06/2025`
        - "אתמול" → `20/06/2025`
        - "שלשום" / "לפני יומיים" → `19/06/2025`
        - "לפני שלושה ימים" → `18/06/2025`
        If the text includes expressions like "לפני X ימים", subtract X days from the reference date to get the actual date.
        
        Extract only information that is explicitly stated or can be clearly inferred.  
        Do not guess or fill in missing details. If a field is not present, leave it as an empty string ("")

        🟢 **Special rule regarding Itay (איתי):**  
        This text is the transcription of a voice message recorded by **Itay (איתי)**, the company's site manager, who is usually present and working on-site.
        Whenever the text uses the word **"אני" (I)**, it refers to **Itay** himself.

        If the text says anything that indicates **Itay was not present** — for example:  
        - "אני לא הייתי שם"  
        - "לא הגעתי היום"  
        - "שלחתי את העובדים לבד"  
        then you must **exclude Itay from the workers list**.

        Otherwise, include "איתי" by default.
        Since this message was recorded by Itay himself, you must assume that **he was present and working on-site**, unless he clearly says that he was not.  
        Therefore, include `"איתי"` in the `workers` field unless his absence is explicitly mentioned.

        Return your output as a JSON object with the following fields:
        {{
            "date": "",               // Date in format DD/MM/YYYY — must match the given date
            "start_time": "",         // Start time in HH:MM (24-hour format)
            "end_time": "",           // End time in HH:MM (24-hour format) 
            "project_name": "",       // Main project name
            "sub_project": "",        // Specific sub-area or zone (if any)
            "work_description": "",   // Clear and concise description of the work performed
            "workers": "",            // Names of workers who worked today, comma-separated (in Hebrew, without titles)
            "additional_notes": ""    // Any additional comments, issues, or problems encountered

        }}

        Important:
        - Return only the JSON object. No explanations, no formatting, no extra text.
        - All field values must be in Hebrew. Do not translate or transliterate anything to English.
        - Always include "איתי" in the workers field unless it is explicitly said he was not present.
        """
    
    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """
        Parse JSON response from OpenAI.
        
        Args:
            content: Raw response content
            
        Returns:
            Parsed JSON data
            
        Raises:
            DataExtractionError: If parsing fails
        """
        try:
            # Remove any markdown formatting if present
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            
            workday_data = json.loads(content.strip())
            return workday_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Raw response: {content}")
            raise DataExtractionError(f"JSON parsing failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error parsing JSON: {e}")
            raise DataExtractionError(f"JSON parsing failed: {e}")
    
    def _validate_and_clean_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean the extracted data.
        
        Args:
            data: Raw extracted data
            
        Returns:
            Cleaned and validated data
        """
        # Define expected fields
        expected_fields = [
            'day', 'date', 'start_time', 'end_time', 'project_name',
            'sub_project', 'work_description', 'workers', 'additional_notes'
        ]
        
        # Ensure all fields exist
        cleaned_data = {}
        for field in expected_fields:
            cleaned_data[field] = data.get(field, '')
        
        # Clean and format specific fields
        if cleaned_data['date']:
            cleaned_data['date'] = self._format_date(cleaned_data['date'])
        
        if cleaned_data['start_time']:
            cleaned_data['start_time'] = self._format_time(cleaned_data['start_time'])
        
        if cleaned_data['end_time']:
            cleaned_data['end_time'] = self._format_time(cleaned_data['end_time'])
        
        # Extract day from date
        date_obj = datetime.strptime(cleaned_data['date'], '%d/%m/%Y')
        hebrew_days = ['שני', 'שלישי', 'רביעי', 'חמישי', 'שישי', 'שבת', 'ראשון']
        cleaned_data['day'] = hebrew_days[date_obj.weekday()]

        return cleaned_data
    
    def _format_date(self, date_str: str) -> str:
        """
        Format date string to DD/MM/YYYY format.
        
        Args:
            date_str: Input date string
            
        Returns:
            Formatted date string
        """
        try:
            # Try different date formats and convert to DD/MM/YYYY
            date_formats = [
                '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%d.%m.%Y',
                '%d/%m/%y', '%d-%m-%y', '%y-%m-%d'
            ]
            
            for fmt in date_formats:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    return date_obj.strftime('%d/%m/%Y')
                except ValueError:
                    continue
            
            return date_str  # Return original if no format matches
        except Exception as e:
            logger.warning(f"Date formatting failed for '{date_str}': {e}")
            return date_str
    
    def _format_time(self, time_str: str) -> str:
        """
        Format time string to HH:MM format.
        
        Args:
            time_str: Input time string
            
        Returns:
            Formatted time string
        """
        try:
            # Try different time formats and convert to HH:MM
            time_formats = [
                '%H:%M', '%H:%M:%S', '%I:%M %p', '%I:%M:%S %p',
                '%H.%M', '%I.%M %p'
            ]
            
            for fmt in time_formats:
                try:
                    time_obj = datetime.strptime(time_str, fmt)
                    return time_obj.strftime('%H:%M')
                except ValueError:
                    continue
            
            return time_str  # Return original if no format matches
        except Exception as e:
            logger.warning(f"Time formatting failed for '{time_str}': {e}")
            return time_str
    
    def _create_fallback_data(self, transcribed_text: str) -> Dict[str, Any]:
        """
        Create fallback data when extraction fails.
        
        Args:
            transcribed_text: Original transcribed text
            
        Returns:
            Basic fallback data structure
        """
        logger.warning("Using fallback data structure due to extraction failure")
        
        return {
            'day': '',
            'date': datetime.now().strftime('%d/%m/%Y'),
            'start_time': '',
            'end_time': '',
            'project_name': '',
            'sub_project': '',
            'work_description': transcribed_text,  # Use original text as description
            'workers': '',
            'additional_notes': 'מידע חולץ אוטומטית - נדרש עיון ידני'
        } 