# Shaliwood Voice Bot

A Telegram bot that transcribes voice messages using OpenAI's Whisper API.

## Features

- Transcribes voice messages to text using OpenAI's Whisper API
- Supports Hebrew language transcription
- Easy to set up and use

## Prerequisites

- Python 3.8 or higher
- Poetry for dependency management
- Telegram Bot Token (get from [@BotFather](https://t.me/BotFather))
- OpenAI API Key (get from [OpenAI Dashboard](https://platform.openai.com/api-keys))

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/shaliwood-voice-bot.git
cd shaliwood-voice-bot
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Create a `.env` file in the project root with your credentials:
```env
TELEGRAM_TOKEN=your_telegram_token_here
OPENAI_API_KEY=your_openai_api_key_here
```

## Usage

1. Start the bot:
```bash
poetry run python main.py
```

2. Send a voice message to your bot on Telegram
3. The bot will transcribe the voice message and reply with the text

## Development

- The project uses Poetry for dependency management
- Environment variables are managed through python-dotenv
- Logging is configured to show detailed information about the bot's operation

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.