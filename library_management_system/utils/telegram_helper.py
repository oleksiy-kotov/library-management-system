from django.contrib.sites import requests
from django.conf import settings


def send_telegram_notification(message: str):
    """
    Sends a notification message to the configured Telegram chat.
    """
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        raise ValueError("Telegram bot token or chat ID not configured in .env")

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": settings.TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
    }

    response = requests.post(url, json=payload)
    if response.status_code != 200:
        raise Exception(f"Telegram API error: {response.text}")

    return response.json()
