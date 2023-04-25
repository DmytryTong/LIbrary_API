import os
import telebot


def send_telegram_notification(message):
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    bot = telebot.TeleBot(token=BOT_TOKEN)
    bot.send_message(chat_id=chat_id, text=message)
