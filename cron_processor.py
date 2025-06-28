#!/usr/bin/env python3
"""
Standalone cron processor for Shaliwood Voice Bot.
This script can be called directly from system cron to process recent Telegram messages.

Usage:
    python3 cron_processor.py

Cron example (run daily at 2 AM):
    0 2 * * * cd /path/to/shaliwood-voice-bot && python3 cron_processor.py >> /var/log/shaliwood-cron.log 2>&1
"""

import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    try:
        logger.info("Starting Shaliwood Voice Bot cron processing")
        from shaliwood_voice_bot.cron_processor import run_cron_processing
        import asyncio
        stats = asyncio.run(run_cron_processing())
        logger.info("Cron processing completed successfully")
        logger.info(f"Statistics: {stats}")
        return 0
    except Exception as e:
        logger.error(f"Cron processing failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 