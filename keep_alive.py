from flask import Flask
import threading
import time
import requests
import os
from bot_log import logger

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/health')
def health():
    return {"status": "healthy"}, 200

def run_bot():
    """Запускает телеграм бота"""
    import bot
    try:
        bot.bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        logger.error(f"❌ Ошибка при работе бота: {e}")

def keep_alive():
    """Функция для поддержания активности на Render"""
    while True:
        try:
            url = "https://telegram-bot-9kxx.onrender.com"
            response = requests.get(url)
            logger.info(f"Keep-alive ping sent. Status: {response.status_code}")
        except Exception as e:
            logger.error(f"Keep-alive error: {e}")
        time.sleep(300)

def start_keep_alive():
    """Запускает бота, keep-alive и Flask сервер в отдельных потоках"""
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    logger.info("🚀 Бот запущен...")

    # Запускаем keep-alive в отдельном потоке
    keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
    keep_alive_thread.start()
    logger.info("Keep-alive thread started")

    # Запускаем Flask сервер в основном потоке
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    start_keep_alive()
