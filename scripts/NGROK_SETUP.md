# Free ngrok Setup Guide

This guide will help you set up a free ngrok account for local webhook testing.

## 🚀 Quick Setup (2 minutes)

### Step 1: Sign Up for Free Account
1. Go to: https://dashboard.ngrok.com/signup
2. Click "Sign up for free"
3. Fill in your details (email, password)
4. Verify your email

### Step 2: Get Your Auth Token
1. Go to: https://dashboard.ngrok.com/get-started/your-authtoken
2. Copy your auth token (looks like: `2abc123def456ghi789jkl`)

### Step 3: Add Token to ngrok
Run this command in your terminal:
```bash
ngrok config add-authtoken YOUR_TOKEN_HERE
```

Replace `YOUR_TOKEN_HERE` with the token you copied.

### Step 4: Test Your Setup
Run our webhook testing script:
```bash
./scripts/start_webhook_local.sh
```

## ✅ That's It!

You now have:
- ✅ Free ngrok account
- ✅ Authenticated ngrok installation
- ✅ Ready for local webhook testing

## 🎯 What You Get with Free Account

- **HTTPS tunnels**: Secure connections to your local server
- **Custom subdomains**: Free ngrok.io subdomains
- **Web interface**: Real-time tunnel inspection
- **No cost**: Completely free forever
- **Perfect for testing**: Ideal for development

## 🔧 Troubleshooting

### "ngrok not authenticated" error
- Make sure you copied the token correctly
- Check that you ran the `ngrok config add-authtoken` command
- Verify your account is active

### "Sign up" issues
- Use a valid email address
- Check your spam folder for verification email
- Try a different browser if needed

### Token not working
- Make sure you're logged into the correct ngrok account
- Try copying the token again
- Check for extra spaces in the token

## 📞 Need Help?

- **ngrok Support**: https://ngrok.com/support
- **Our Scripts**: Check `scripts/README.md` for detailed troubleshooting
- **Alternative**: Use polling mode instead: `python -m src.shaliwood_voice_bot.main --polling` 