# Telegram Logging Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Auto-slopp system installed
- Python 3.11+ with uv
- Telegram account

### Step 1: Create Your Bot

1. Open Telegram and search for **@BotFather**
2. Send `/start` to BotFather
3. Send `/newbot` to create a new bot
4. Choose a name (e.g., "Auto-slopp Logger")
5. Choose a username (e.g., "auto_slopp_logger_bot")
6. Save your bot token: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

### Step 2: Get Your Chat ID

1. Start a chat with your new bot
2. Send any message to the bot
3. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Find your chat ID under `chat.id`

### Step 3: Configure Auto-slopp

Add to your `config.yaml`:

```yaml
telegram:
  enabled: true
  bot_token: "YOUR_BOT_TOKEN_HERE"
  default_chat_id: "YOUR_CHAT_ID_HERE"
```

### Step 4: Test It!

```python
from auto_slopp.telegram import telegram_log_info

telegram_log_info("Hello from Auto-slopp! 🚀", "quick_start")
```

You should receive a message in Telegram immediately!

## 🎯 Next Steps

- [Full Documentation](TELEGRAM_LOGGING_GUIDE.md) - Complete guide
- [Configuration Options](TELEGRAM_LOGGING_GUIDE.md#configuration) - Advanced config
- [Troubleshooting](TELEGRAM_LOGGING_GUIDE.md#troubleshooting) - Common issues
- [Examples](TELEGRAM_LOGGING_GUIDE.md#examples) - Usage examples

## 💡 Pro Tips

- Use environment variables for sensitive data
- Create a private group instead of using personal chat
- Monitor queue stats for performance
- Filter messages to avoid spam

## 🆘 Need Help?

- Check the [troubleshooting guide](TELEGRAM_LOGGING_GUIDE.md#troubleshooting)
- Create an issue in the Auto-slopp repository
- Join our community discussions

---

*Happy logging! 📝*