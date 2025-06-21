import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

class ConfigError(Exception):
    """Raised when there's an error in the configuration."""
    pass

def load_config() -> None:
    """Load environment variables from .env file if it exists."""
    env_path = Path('.env')
    if env_path.exists():
        load_dotenv(env_path)

def get_required_env(key: str) -> str:
    """
    Get a required environment variable.
    
    Args:
        key: The environment variable name
        
    Returns:
        The environment variable value
        
    Raises:
        ConfigError: If the environment variable is not set
    """
    value = os.getenv(key)
    if not value:
        raise ConfigError(f"Required environment variable '{key}' is not set")
    return value

def get_optional_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get an optional environment variable.
    
    Args:
        key: The environment variable name
        default: Default value if the environment variable is not set
        
    Returns:
        The environment variable value or the default value
    """
    return os.getenv(key, default)

# Load configuration when module is imported
load_config()

# Required environment variables
TELEGRAM_TOKEN = get_required_env('TELEGRAM_TOKEN')
OPENAI_API_KEY = get_required_env('OPENAI_API_KEY')

# Google Sheets configuration
GOOGLE_SHEETS_CREDENTIALS_FILE = get_optional_env('GOOGLE_SHEETS_CREDENTIALS_FILE', 'credentials.json')
SPREADSHEET_ID = get_required_env('SPREADSHEET_ID')

# Optional environment variables
LOG_LEVEL = get_optional_env('LOG_LEVEL', 'INFO')

# Voice message saving configuration
SAVE_VOICE_MESSAGES = get_optional_env('SAVE_VOICE_MESSAGES', 'false').lower() == 'true'
VOICE_SAVE_DIR = get_optional_env('VOICE_SAVE_DIR', 'voice_messages') 