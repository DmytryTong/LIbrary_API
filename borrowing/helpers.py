import os
import telebot


def send_telegram_notification(message):
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    bot = telebot.TeleBot(token=bot_token)
    bot.send_message(chat_id=chat_id, text=message)
