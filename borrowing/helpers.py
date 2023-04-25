import os
from telegram import Bot


def send_telegram_notification(message):
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    bot = Bot(token=bot_token)
    bot.sendMessage(chat_id=chat_id, text=message)
