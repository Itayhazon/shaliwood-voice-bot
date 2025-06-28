# Cron Processing for Shaliwood Voice Bot

This document explains the cron processing feature that allows batch processing of recent Telegram messages.

## ⚠️ Important Limitations

### Telegram API Constraints

**CRITICAL**: Due to Telegram Bot API limitations, this feature has significant constraints:

1. **24-Hour Message Storage**: Telegram only stores incoming messages for **24 hours**
2. **No Historical Access**: Messages older than 24 hours are permanently deleted from Telegram's servers
3. **Limited Scope**: Cron processing can only access messages from the last 24 hours

### What This Means

- ✅ **Compliant**: Using `getUpdates` to fetch recent messages is allowed by Telegram's API
- ❌ **Limited**: Only messages from the last 24 hours are accessible
- ❌ **Incomplete**: Cannot retrieve older messages for daily processing
- ⚠️ **Not a Replacement**: This should not replace real-time webhook/polling processing

## 🎯 Use Cases

The cron processing feature is useful for:

1. **Backup Processing**: Catch any messages that might have been missed by real-time processing
2. **Batch Processing**: Process multiple messages at once for efficiency
3. **Recovery**: Recover from temporary outages or processing failures
4. **Monitoring**: Track message processing statistics and health
5. **Development**: Test processing logic without real-time bot operation

## 🚀 Installation and Setup

### 1. Prerequisites

Ensure your bot is properly configured with:
- Valid `TELEGRAM_TOKEN` in `.env`
- All other required environment variables
- Google Sheets credentials (if using sheets integration)

### 2. Running Manually

#### Option A: Using the Shell Script
```bash
./scripts/run_cron_processing.sh
```

#### Option B: Using Poetry
```bash
poetry run python -m src.shaliwood_voice_bot.cron_processor
```

#### Option C: Using the Standalone Script
```bash
poetry run python cron_processor.py
```

### 3. Setting Up System Cron

#### Daily Processing (Recommended)
```bash
# Edit crontab
crontab -e

# Add this line to run daily at 2 AM
0 2 * * * cd /path/to/shaliwood-voice-bot && poetry run python cron_processor.py >> /var/log/shaliwood-cron.log 2>&1
```

#### Hourly Processing (More Frequent)
```bash
# Run every hour
0 * * * * cd /path/to/shaliwood-voice-bot && poetry run python cron_processor.py >> /var/log/shaliwood-cron.log 2>&1
```

#### Custom Schedule
```bash
# Run every 6 hours
0 */6 * * * cd /path/to/shaliwood-voice-bot && poetry run python cron_processor.py >> /var/log/shaliwood-cron.log 2>&1
```

## 📊 Understanding the Output

### Processing Statistics

The cron processor provides detailed statistics:

```json
{
  "total_messages": 15,
  "voice_messages": 8,
  "processed_voice": 7,
  "errors": 1,
  "start_time": "2024-01-15T02:00:00",
  "end_time": "2024-01-15T02:05:30",
  "duration": 330.5,
  "messages_processed": [
    {
      "user_id": "123456789",
      "message_date": "15/01/2024",
      "transcription": "היום עבדנו על פרויקט הגג...",
      "has_workday_data": true
    }
  ]
}
```

### Log Output

```
2024-01-15 02:00:00 - shaliwood_voice_bot.cron_processor - INFO - Starting cron message processing for last 24 hours
2024-01-15 02:00:01 - shaliwood_voice_bot.cron_processor - INFO - Found 15 recent updates
2024-01-15 02:00:02 - shaliwood_voice_bot.cron_processor - INFO - Processing voice message from user 123456789
2024-01-15 02:00:05 - shaliwood_voice_bot.cron_processor - INFO - Successfully processed voice message from user 123456789
2024-01-15 02:05:30 - shaliwood_voice_bot.cron_processor - INFO - Cron processing completed: 7 voice messages processed, 1 errors
```

## 🔧 Configuration

### Environment Variables

The cron processor uses the same configuration as the main bot:

```env
# Required
TELEGRAM_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
SPREADSHEET_ID=your_google_spreadsheet_id

# Optional
SAVE_VOICE_MESSAGES=false
VOICE_SAVE_DIR=voice_messages
LOG_LEVEL=INFO
```

### Processing Options

You can customize the processing behavior by modifying the `CronMessageProcessor` class:

```python
# In src/shaliwood_voice_bot/cron_processor.py

# Change the time window (max 24 hours)
stats = await processor.fetch_and_process_recent_messages(hours_back=12)

# Modify allowed update types
updates = await self.bot.get_updates(
    allowed_updates=['message', 'edited_message']  # Add more types if needed
)
```

## 🛡️ Security Considerations

### API Rate Limits

- Telegram has rate limits on API calls
- The cron processor uses conservative timeouts and limits
- Avoid running too frequently to prevent rate limiting

### Error Handling

- Failed message processing is logged but doesn't stop the batch
- Temporary files are cleaned up even if processing fails
- Network errors are handled gracefully

### Logging

- Processing statistics are logged for monitoring
- Sensitive data (user IDs, transcriptions) are logged at INFO level
- Full transcriptions are truncated in logs for privacy

## 🔍 Troubleshooting

### Common Issues

#### 1. No Messages Found
```
INFO - No recent updates found
```
**Cause**: No messages in the last 24 hours, or all messages already processed
**Solution**: This is normal if no new messages were sent

#### 2. Telegram API Errors
```
ERROR - Telegram API error fetching updates: ...
```
**Cause**: Invalid token, network issues, or rate limiting
**Solution**: Check your `TELEGRAM_TOKEN` and network connectivity

#### 3. Processing Errors
```
ERROR - Error processing voice message: ...
```
**Cause**: Audio processing failures, file download issues
**Solution**: Check OpenAI API key and audio file accessibility

#### 4. Permission Errors
```
ERROR - Cron processing failed: ...
```
**Cause**: File permissions, missing dependencies
**Solution**: Ensure proper file permissions and Poetry environment

### Debug Mode

Enable debug logging for more detailed information:

```bash
# Set debug level
export LOG_LEVEL=DEBUG

# Run with debug output
poetry run python cron_processor.py
```

## 📈 Monitoring and Maintenance

### Log Monitoring

Monitor the cron logs for:
- Processing success rates
- Error patterns
- Performance metrics
- API rate limiting

### Health Checks

The processor provides health check information:

```python
stats = processor.get_processing_stats()
print(f"Bot token configured: {stats['bot_token_configured']}")
print(f"Last processed update ID: {stats['last_processed_update_id']}")
```

### Performance Optimization

- The processor uses efficient batch processing
- Temporary files are cleaned up automatically
- Network timeouts are optimized for cron execution
- Memory usage is minimal

## 🚨 Important Notes

### Not a Replacement for Real-time Processing

**DO NOT** rely solely on cron processing. Always use:
- Webhook mode (recommended for production)
- Polling mode (for development/testing)

### Message Deduplication

The processor tracks the last processed update ID to avoid:
- Processing the same message multiple times
- Duplicate entries in your data storage

### Time Zone Considerations

- Message dates are processed in UTC
- Ensure your cron schedule accounts for your timezone
- Consider running slightly after midnight UTC for best coverage

## 🔄 Integration with Existing Bot

The cron processor works alongside your existing bot:

1. **Real-time Processing**: Bot handles messages as they arrive
2. **Cron Processing**: Catches any missed messages from the last 24 hours
3. **No Conflicts**: Uses the same data storage and processing logic
4. **Shared Configuration**: Uses the same environment variables

## 📝 Example Cron Jobs

### Development Environment
```bash
# Run every 6 hours during development
0 */6 * * * cd /home/user/shaliwood-voice-bot && poetry run python cron_processor.py >> /tmp/shaliwood-dev.log 2>&1
```

### Production Environment
```bash
# Run daily at 2 AM in production
0 2 * * * cd /opt/shaliwood-voice-bot && poetry run python cron_processor.py >> /var/log/shaliwood-cron.log 2>&1
```

### High-Frequency Processing
```bash
# Run every 2 hours for high-traffic bots
0 */2 * * * cd /opt/shaliwood-voice-bot && poetry run python cron_processor.py >> /var/log/shaliwood-cron.log 2>&1
```

## 🤝 Contributing

When modifying the cron processor:

1. Maintain backward compatibility
2. Add comprehensive logging
3. Handle errors gracefully
4. Update this documentation
5. Test with various message types

## 📚 Additional Resources

- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
- [python-telegram-bot Documentation](https://python-telegram-bot.readthedocs.io/)
- [Cron Expression Generator](https://crontab.guru/)
- [System Cron Documentation](https://man7.org/linux/man-pages/man5/crontab.5.html) 