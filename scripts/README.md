# Local Webhook Testing Scripts

This directory contains scripts to make local webhook testing as simple as possible.

## 🚀 Quick Start (Recommended)

For the easiest experience, use the start script:

```bash
./scripts/start_webhook_local.sh
```

This single command will:
- ✅ Check all prerequisites
- ✅ Install ngrok if needed
- ✅ Guide you through free ngrok account setup
- ✅ Start ngrok tunnel
- ✅ Update your .env with the correct webhook URL
- ✅ Start the bot in webhook mode

## 🛑 Stop Testing

To stop webhook testing and clean up:

```bash
./scripts/stop_webhook_local.sh
```

## 🔑 Free ngrok Setup (Required)

ngrok requires a free account for authentication:

1. **Sign up for free account**: https://dashboard.ngrok.com/signup
2. **Get your auth token**: https://dashboard.ngrok.com/get-started/your-authtoken
3. **Add token to ngrok**: `ngrok config add-authtoken YOUR_TOKEN`

The scripts will guide you through this process automatically.

## 📋 Manual Setup (Step by Step)

If you prefer to control each step manually:

### 1. Initial Setup
```bash
./scripts/setup_webhook_local.sh
```

This will:
- Install ngrok if not present
- Guide you through free account setup
- Create a `.env.local` template

### 2. Start Webhook Testing
```bash
./scripts/start_webhook_local.sh
```

### 3. Stop and Clean Up
```bash
./scripts/stop_webhook_local.sh
```

## 🛠️ Script Details

### `start_webhook_local.sh` (Main Script)
- **Purpose**: Start local webhook testing
- **What it does**: Automates the entire process
- **Usage**: `./scripts/start_webhook_local.sh`
- **Stop**: Run `./scripts/stop_webhook_local.sh` or press `Ctrl+C`

### `stop_webhook_local.sh`
- **Purpose**: Stop webhook testing and cleanup
- **What it does**: Stops processes and restores configuration
- **Usage**: `./scripts/stop_webhook_local.sh`

### `setup_webhook_local.sh`
- **Purpose**: Initial setup and ngrok installation
- **What it does**: Installs ngrok and guides through free account setup
- **Usage**: `./scripts/setup_webhook_local.sh`

## 🔧 Prerequisites

- **Poetry**: For dependency management
- **ngrok**: Will be installed automatically by setup script
- **Free ngrok account**: Required for authentication (signup at https://dashboard.ngrok.com/signup)

## 📝 Configuration

Your `.env` file should contain:
```env
TELEGRAM_TOKEN=your_bot_token
OPENAI_API_KEY=your_openai_key
SPREADSHEET_ID=your_spreadsheet_id
WEBHOOK_URL=https://your-ngrok-url.ngrok.io
WEBHOOK_PORT=8443
WEBHOOK_LISTEN=0.0.0.0
WEBHOOK_PATH=/webhook
WEBHOOK_SECRET=your_secret
```

## 🐛 Troubleshooting

### ngrok Issues
- **Not authenticated**: Follow the free account setup guide above
- **Port in use**: Change port in script or kill existing processes
- **URL not working**: Check ngrok logs with `tail -f ngrok.log`
- **Free tier limits**: ngrok free tier has some limitations but works fine for testing

### Bot Issues
- **Configuration errors**: Check `.env` file values
- **Port conflicts**: Ensure port 8443 is free
- **Dependencies**: Run `poetry install`

### General Issues
- **Scripts not executable**: Run `chmod +x scripts/*.sh`
- **Permission denied**: Check file permissions
- **Process cleanup**: Use `./scripts/stop_webhook_local.sh`

## 🎯 Testing Workflow

1. **Start testing**: `./scripts/start_webhook_local.sh`
2. **Follow ngrok setup** (if first time)
3. **Send message**: Use your Telegram bot
4. **Check logs**: Monitor bot output
5. **Stop testing**: `./scripts/stop_webhook_local.sh`

## 📊 Logs

- **ngrok logs**: `tail -f ngrok.log`
- **Bot logs**: Displayed in terminal
- **Application logs**: Check bot output for errors

## 🔄 Alternative: Polling Mode

For simpler local testing without webhooks:
```bash
python -m src.shaliwood_voice_bot.main --polling
```

This doesn't require ngrok or public URL setup.

## 💰 Free ngrok Account Benefits

- **No cost**: Completely free
- **HTTPS tunnels**: Secure connections
- **Custom domains**: Free subdomains
- **Web interface**: Real-time tunnel inspection
- **Perfect for testing**: Ideal for development and testing

## 🔐 Security

For comprehensive security guidance, see `WEBHOOK_SECURITY.md`:
- Secure webhook secret generation
- Production deployment security
- Best practices and checklists 