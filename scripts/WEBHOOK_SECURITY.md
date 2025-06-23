# Webhook Security Guide

This guide covers secure webhook configuration for both development and production environments.

## 🔐 Webhook Secret Security

### What is a Webhook Secret?

A webhook secret is a token that Telegram uses to verify that webhook requests are legitimate. It helps prevent unauthorized access to your bot.

### Secure Secret Requirements

- **Length**: At least 32 characters (64 hex characters)
- **Randomness**: Cryptographically secure random generation
- **Uniqueness**: Different for each environment
- **Secrecy**: Never commit to version control

## 🛠️ Generating Secure Secrets

### Method 1: OpenSSL (Recommended)
```bash
# Generate 32-byte hex secret (64 characters)
openssl rand -hex 32
```

### Method 2: Python
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Method 3: Our Script
```bash
./scripts/generate_secret.sh
```

### Method 4: Online Generator
Use a trusted online generator (for development only):
- https://generate-secret.vercel.app/32

## 📝 Environment Configuration

### Development (.env)
```env
# Webhook configuration for local testing
WEBHOOK_URL=https://your-ngrok-url.ngrok.io
WEBHOOK_PORT=8443
WEBHOOK_LISTEN=0.0.0.0
WEBHOOK_PATH=/webhook
WEBHOOK_SECRET=1d5ea35e3a98d8ff9be67544450387dc2cc5bbc0bbb4ec1f2ff1d1b6fad7665c
```

### Production (.env)
```env
# Production webhook configuration
WEBHOOK_URL=https://your-domain.com
WEBHOOK_PORT=8443
WEBHOOK_LISTEN=0.0.0.0
WEBHOOK_PATH=/webhook
WEBHOOK_SECRET=c7f327a560813508e9ba6f2dae6d769b6c1b6d245073f14912cb3bbca0242352
```

## 🚀 Production Setup

### 1. Domain and SSL
- **HTTPS Required**: Telegram only accepts HTTPS webhooks
- **Valid SSL Certificate**: Use Let's Encrypt or commercial certificate
- **Domain**: Use a dedicated domain or subdomain

### 2. Server Configuration
```bash
# Example nginx configuration
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location /webhook {
        proxy_pass http://localhost:8443;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. Firewall Configuration
```bash
# Allow only necessary ports
sudo ufw allow 443/tcp
sudo ufw allow 8443/tcp
sudo ufw enable
```

### 4. Environment Variables
```bash
# Set production environment variables
export WEBHOOK_URL=https://your-domain.com
export WEBHOOK_SECRET=your_secure_secret_here
export WEBHOOK_PORT=8443
export WEBHOOK_LISTEN=0.0.0.0
export WEBHOOK_PATH=/webhook
```

## 🔒 Security Best Practices

### 1. Secret Management
- ✅ **Use environment variables** for secrets
- ✅ **Generate unique secrets** for each environment
- ✅ **Rotate secrets** regularly
- ❌ **Never hardcode** secrets in code
- ❌ **Never commit** secrets to version control

### 2. Network Security
- ✅ **Use HTTPS** for all webhook URLs
- ✅ **Restrict access** to webhook endpoint
- ✅ **Use firewall** rules
- ✅ **Monitor access** logs
- ❌ **Don't expose** webhook port publicly

### 3. Application Security
- ✅ **Validate webhook signatures** (handled by python-telegram-bot)
- ✅ **Use secure headers**
- ✅ **Implement rate limiting**
- ✅ **Log security events**

### 4. Server Security
- ✅ **Keep systems updated**
- ✅ **Use strong passwords**
- ✅ **Enable 2FA** where possible
- ✅ **Regular security audits**

## 🧪 Testing Security

### 1. Verify Webhook Secret
```bash
# Test webhook endpoint with invalid secret
curl -X POST https://your-domain.com/webhook \
  -H "Content-Type: application/json" \
  -H "X-Telegram-Bot-Api-Secret-Token: invalid_secret" \
  -d '{"test": "data"}'
```

### 2. Check SSL Configuration
```bash
# Test SSL configuration
openssl s_client -connect your-domain.com:443 -servername your-domain.com
```