#!/bin/bash

# Generate secure webhook secret for production use

echo "🔐 Generating secure webhook secret..."
echo ""

# Generate hex secret (64 characters)
HEX_SECRET=$(openssl rand -hex 32)
echo "WEBHOOK_SECRET=$HEX_SECRET"
echo ""

echo "✅ Secret generated successfully!"
echo ""
echo "📝 Usage:"
echo "1. Copy the secret above"
echo "2. Add it to your .env file"
echo "3. Never commit secrets to version control"
echo ""
echo "🔒 Security notes:"
echo "- Use different secrets for each environment"
echo "- Rotate secrets regularly"
echo "- Keep secrets secure and private" 