# Shaliwood Voice Bot

A simple Telegram voice bot for Shaliwood construction company that transcribes voice messages and automatically extracts workday information to Google Sheets.

## 🎯 Features

- 🎤 Voice message transcription using OpenAI Whisper
- 🧠 Intelligent data extraction using OpenAI GPT-4
- 📊 Automatic Google Sheets integration
- 🇮🇱 Hebrew language support
- 🏗️ Construction-specific data fields
- 🔧 Simple, direct implementation
- 🛡️ Basic error handling
- 📝 Clear logging
- 💾 Voice message saving for testing (optional)
- 🎵 Local audio file processing for testing
- 🔄 Unified processing pipeline (testing and production use identical code)

## 📊 Data Fields

The bot extracts the following information from voice messages:

| Field (English) | Field (Hebrew) | Description |
|----------------|----------------|-------------|
| day | יום | Day of the week |
| date | תאריך | Date (DD/MM/YYYY) |
| start_time | שעת התחלה | Work start time (HH:MM) |
| end_time | שעת סיום | Work end time (HH:MM) |
| project_name | שם הפרויקט | Main project name |
| sub_project | תת פרויקט | Sub-project or specific area |
| work_description | תיאור העבודה | Detailed work description |
| workers | עובדים | Workers who worked today |
| additional_notes | הערות נוספות | Additional notes or issues |
| raw_transcription | תמלול גולמי | Raw transcription of the voice message (added by business layer) |
| status | סטטוס | Approval status (default: "⏳ ממתין לאישור" - Pending approval, added by business layer) |

## 🎯 Project Structure

```
shaliwood-voice-bot/
├── src/shaliwood_voice_bot/
│   ├── __init__.py
│   ├── main.py                  # Main application orchestrator
│   ├── voice_processor.py       # Audio transcription and data extraction
│   ├── data_manager.py          # Google Sheets operations
│   ├── response_formatter.py    # Message formatting
│   ├── hebrew_console.py        # Hebrew text formatting for console
│   ├── telegram_bot.py          # Telegram-specific operations
│   ├── local_processor.py       # Local file processing for testing
│   ├── config.py                # Configuration management
│   ├── sheets.py                # Google Sheets integration
│   └── data_extractor.py        # AI data extraction
├── pyproject.toml               # Dependencies and project config
└── README.md                   # This file
```

## 🔧 Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- Poetry (for dependency management)
- Telegram Bot Token
- OpenAI API Key
- Google Cloud Project with Sheets API enabled

### 2. Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd shaliwood-voice-bot
```

2. Install dependencies:
```bash
poetry install
```

### 3. Environment Configuration

Create a `.env` file in the project root:

```env
# Required
TELEGRAM_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
SPREADSHEET_ID=your_google_spreadsheet_id

# Webhook configuration (required for webhook mode, which is the default)
WEBHOOK_URL=https://your-domain.com
WEBHOOK_PORT=8443
WEBHOOK_LISTEN=0.0.0.0
WEBHOOK_PATH=/webhook
WEBHOOK_SECRET=your_webhook_secret_here

# Optional
LOG_LEVEL=INFO
GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json

# Voice message saving (for testing)
SAVE_VOICE_MESSAGES=false
VOICE_SAVE_DIR=voice_messages
```

### 4. Google Sheets Setup

1. **Create a Google Cloud Project:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Google Sheets API

2. **Create Service Account Credentials:**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Download the JSON credentials file
   - Rename it to `credentials.json` and place it in the project root

3. **Create a Google Spreadsheet:**
   - Create a new Google Spreadsheet
   - Share it with the service account email (found in credentials.json)
   - Copy the spreadsheet ID from the URL
   - Add the spreadsheet ID to your `.env` file

### 5. Running the Bot

The bot supports two modes of operation:

#### Webhook Mode (Default)
Webhook mode is the default and recommended for production use. It requires a publicly accessible HTTPS URL.

```bash
# Activate the poetry environment
poetry shell

# Run the bot in webhook mode (default)
python -m src.shaliwood_voice_bot.main
```

**Webhook Requirements:**
- Public HTTPS URL (e.g., `https://your-domain.com`)
- Valid SSL certificate
- Port 8443 (or custom port configured in `.env`)
- Webhook secret for security

#### Polling Mode
Polling mode is useful for development and debugging. It doesn't require a public URL.

```bash
# Activate the poetry environment
poetry shell

# Run the bot in polling mode
python -m src.shaliwood_voice_bot.main --polling
```

**When to use polling mode:**
- Local development
- Testing and debugging
- When you don't have a public HTTPS URL
- Quick setup for development

### Local Webhook Testing

For testing webhook mode locally, we provide convenient scripts:

```bash
# Start local webhook testing (recommended)
./scripts/start_webhook_local.sh

# Stop and clean up
./scripts/stop_webhook_local.sh

# First-time setup (if needed)
./scripts/setup_webhook_local.sh
```

**Requirements for local webhook testing:**
- ngrok (installed automatically by scripts)
- Free ngrok account (signup at https://dashboard.ngrok.com/signup)

See `scripts/README.md` for detailed instructions and `scripts/WEBHOOK_SECURITY.md` for security best practices.

## 🚀 Usage

### Running the Bot

1. Send a voice message to your Telegram bot
2. The bot will:
   - Transcribe the voice message to Hebrew text
   - Extract structured workday information using AI
   - Add the information to your Google Sheet
   - Send a confirmation message with the extracted data

### Testing with Local Files

You can test the bot with local audio files without sending Telegram messages:

```bash
# Basic transcription and data extraction
python -m src.shaliwood_voice_bot.main --file path/to/audio.ogg

# Transcribe only (skip data extraction)
python -m src.shaliwood_voice_bot.main --file path/to/audio.ogg --transcribe-only

# Save transcription to file
python -m src.shaliwood_voice_bot.main --file path/to/audio.ogg --output transcription.txt

# Skip Google Sheets integration for testing (data extraction still works)
python -m src.shaliwood_voice_bot.main --file path/to/audio.ogg --no-sheets

# Combine options
python -m src.shaliwood_voice_bot.main --file path/to/audio.ogg --transcribe-only --output transcription.txt
```

**Supported audio formats**: OGG, MP3, WAV, M4A, and other formats supported by OpenAI Whisper.

**Note**: When using `--no-sheets`, data extraction still works and displays the extracted information, but it won't be saved to Google Sheets.

### Running Modes

The bot supports two running modes for Telegram operation:

```bash
# Webhook mode (default) - requires public HTTPS URL
python -m src.shaliwood_voice_bot.main

# Polling mode - useful for development and debugging
python -m src.shaliwood_voice_bot.main --polling
```

## 💾 Voice Message Saving

For testing and debugging purposes, you can enable voice message saving **for Telegram messages only**:

1. **Enable the feature** by setting `SAVE_VOICE_MESSAGES=true` in your `.env` file
2. **Configure save directory** by setting `VOICE_SAVE_DIR=your_directory` (default: `voice_messages`)
3. **Voice files will be saved** with timestamps and user IDs for easy identification

**Note:** Voice message saving does **not** apply to local file processing. When processing local audio files (using the LocalProcessor or CLI), no additional copies are created, regardless of the `SAVE_VOICE_MESSAGES` setting. This prevents redundant or unnecessary file duplication during local testing.

**File naming format**: `voice_{user_id}_{timestamp}.ogg`

**Example**: `voice_123456789_20241201_143022.ogg`

This feature is useful for:
- Testing transcription accuracy
- Debugging voice processing issues
- Building training datasets
- Quality assurance

**Note**: Voice files are saved in OGG format as received from Telegram.

## 📝 Example Voice Message

"היום עבדנו על פרויקט הגג ברחוב הרצל 15. התחלנו בשמונה בבוקר וסיימנו בשש בערב. דני ויוסי עבדו על התקנת האיטום, ואני עבדתי על התקנת הרעפים. הכל הלך חלק, רק היה קצת בעיה עם החומרים שהגיעו באיחור."

## 🛡️ Error Handling

The application includes basic error handling:

- **Graceful Degradation**: Continues operation even if optional services fail
- **Clear Error Messages**: Hebrew error messages for end users
- **Basic Logging**: Essential logging for debugging
- **Fallback Mechanisms**: Automatic fallback when AI extraction fails

## 🔒 Security Considerations

- API keys stored in environment variables
- Google Sheets credentials stored locally
- No sensitive data logged
- Secure HTTPS connections
- Basic input validation

## 🧪 Testing

The simple architecture makes testing straightforward:

```python
# Example test
from src.shaliwood_voice_bot.main import ShaliwoodBot

# Test bot initialization
bot = ShaliwoodBot()
```

## 🔧 Troubleshooting

### Common Issues

1. **Google Sheets Authentication Error:**
   - Ensure `credentials.json` is in the project root
   - Verify the service account has access to the spreadsheet
   - Check that the Google Sheets API is enabled

2. **OpenAI API Error:**
   - Verify your OpenAI API key is correct
   - Check your OpenAI account has sufficient credits
   - Ensure the API key has access to GPT-4

3. **Telegram Bot Not Responding:**
   - Verify the bot token is correct
   - Check that the bot is not blocked
   - Ensure the bot has permission to receive voice messages

4. **Webhook Issues:**
   - Ensure `WEBHOOK_URL` is set to a valid HTTPS URL
   - Verify the URL is publicly accessible
   - Check that port 8443 (or your custom port) is open
   - Ensure your SSL certificate is valid
   - Try using polling mode (`--polling`) for testing

5. **Polling Mode Issues:**
   - Use polling mode for local development: `python -m src.shaliwood_voice_bot.main --polling`
   - Polling mode doesn't require a public URL or SSL certificate
   - Useful for debugging and development

6. **Local Webhook Testing Issues:**
   - Use the provided scripts: `./scripts/start_webhook_local.sh`
   - Free ngrok account required: https://dashboard.ngrok.com/signup
   - Check `scripts/README.md` for detailed troubleshooting

### Logs

The application logs essential operations:
- `INFO`: General operational information
- `WARNING`: Warning messages for non-critical issues
- `ERROR`: Error messages for failed operations

## 🏗️ Development

### Architecture

The bot uses a **clean modular architecture** with clear separation of concerns:

#### 🎯 **Core Components**

- **`VoiceProcessor`**: Handles audio transcription and data extraction only
- **`DataManager`**: Manages Google Sheets operations independently
- **`ResponseFormatter`**: Handles message formatting for different contexts
- **`TelegramBot`**: Manages Telegram-specific operations
- **`LocalProcessor`**: Processes local files for testing
- **`ShaliwoodBot`**: Main orchestrator that coordinates all components

#### 🔄 **Unified Processing Pipeline**

- **Single Source of Truth**: All audio processing goes through `VoiceProcessor.process_audio()`
- **Independent Services**: Each component has a single responsibility
- **Shared Logic**: Transcription and data extraction use identical code paths
- **Consistent Results**: Testing with local files produces identical results to Telegram messages

#### 📦 **Module Responsibilities**

| Module | Responsibility | Dependencies |
|--------|---------------|--------------|
| `main.py` | Application orchestration | All other modules |
| `voice_processor.py` | Audio transcription & data extraction | OpenAI, Data Extractor |
| `data_manager.py` | Google Sheets operations | Sheets |
| `response_formatter.py` | Message formatting | None |
| `hebrew_console.py` | Hebrew text formatting for console | None |
| `telegram_bot.py` | Telegram operations | Voice Processor, Data Manager, Response Formatter |
| `local_processor.py` | Local file testing | Voice Processor, Data Manager, Response Formatter, Hebrew Console |
| `config.py` | Configuration management | None |
| `sheets.py` | Google Sheets integration | None |
| `data_extractor.py` | AI data extraction | OpenAI |

### Adding New Features

1. **Follow Module Responsibilities**: Add features to the appropriate module
2. **Use VoiceProcessor**: Add new processing steps to `VoiceProcessor` for consistency
3. **Keep It Simple**: Maintain clear separation of concerns
4. **Minimal Dependencies**: Avoid adding unnecessary complexity
5. **Clear Logic**: Write straightforward, readable code
6. **Basic Testing**: Test new functionality using local file processing

### Code Quality

- **Type Hints**: Basic type annotations
- **Docstrings**: Simple documentation
- **Error Handling**: Basic exception handling
- **Logging**: Essential logging for debugging
- **Validation**: Basic input validation

## 📄 License

This project is proprietary software for Shaliwood construction company.

## 🆘 Support

For technical support or questions, please contact the development team.