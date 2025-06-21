"""
Hebrew console display utilities for Shaliwood Voice Bot.
Handles proper Hebrew text formatting for terminal output.
"""
import unicodedata
import re


def format_hebrew_for_console(text: str) -> str:
    """
    Format Hebrew text for proper console display.
    
    This function handles Hebrew text that might be displayed incorrectly
    in terminal output by intelligently handling RTL text flow.
    
    Args:
        text: Hebrew text to format
        
    Returns:
        Formatted text suitable for console display
    """
    if not text:
        return text
    
    # Check if text contains Hebrew characters
    if not _contains_hebrew(text):
        return text
    
    # Split into words and process each word
    words = text.split()
    formatted_words = []
    
    for word in words:
        if _contains_hebrew(word):
            # For Hebrew words, reverse the character order
            formatted_words.append(word[::-1])
        else:
            # Keep non-Hebrew words as is
            formatted_words.append(word)
    
    return ' '.join(formatted_words)


def _contains_hebrew(text: str) -> bool:
    """Check if text contains Hebrew characters."""
    hebrew_range = range(0x0590, 0x05FF + 1)  # Hebrew Unicode range
    
    for char in text:
        if ord(char) in hebrew_range:
            return True
    return False


def _split_hebrew_segments(text: str) -> list:
    """
    Split text into Hebrew and non-Hebrew segments.
    
    Args:
        text: Input text to split
        
    Returns:
        List of segments (Hebrew and non-Hebrew alternating)
    """
    segments = []
    current_segment = ""
    current_is_hebrew = None
    
    for char in text:
        char_is_hebrew = ord(char) in range(0x0590, 0x05FF + 1)
        
        # Initialize on first character
        if current_is_hebrew is None:
            current_is_hebrew = char_is_hebrew
            current_segment = char
        # Continue current segment if same type
        elif char_is_hebrew == current_is_hebrew:
            current_segment += char
        # Switch to new segment if different type
        else:
            segments.append(current_segment)
            current_segment = char
            current_is_hebrew = char_is_hebrew
    
    # Add the last segment
    if current_segment:
        segments.append(current_segment)
    
    return segments


def format_hebrew_data_for_console(data: dict) -> dict:
    """
    Format Hebrew data in a dictionary for console display.
    
    Args:
        data: Dictionary containing Hebrew text values
        
    Returns:
        Dictionary with formatted Hebrew text values
    """
    if not data:
        return data
    
    formatted_data = {}
    for key, value in data.items():
        if isinstance(value, str):
            formatted_data[key] = format_hebrew_for_console(value)
        else:
            formatted_data[key] = value
    
    return formatted_data 