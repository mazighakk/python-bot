
# Djezzy Gift Bot

A Telegram bot that helps Djezzy users claim their daily internet gifts automatically.

## Features

- Automatic OTP verification system
- Daily gift claiming functionality
- Phone number validation
- Secure token management
- User data persistence

## Requirements

- Python 3.11+
- Required packages:
  - telebot
  - requests
  - urllib3

## Setup

1. Clone the repository
2. Update the `TOKEN` variable in `main.py` with your Telegram bot token
3. Run the bot using: `python main.py`

## Usage

1. Start the bot by sending `/start`
2. Click "▶️ إرسال الرقم" button
3. Enter your Djezzy phone number (starting with 07)
4. Enter the OTP code received via SMS
5. Click "🎁 خذ الهدية" to claim your daily gift

## Security

- Phone numbers are partially hidden in messages
- User data is stored locally in `djezzy_data.json`
- One gift claim per user per 24 hours

## Notes

- The bot requires a valid Djezzy number
- Gift claims are limited to once per 24 hours
- Internet connection is required for API calls
