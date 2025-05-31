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
    """Запускает Telegram-бота с обработкой ошибок"""
    import bot  # Импорт внутри функции, чтобы избежать циклических импортов
    try:
        bot.bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        logger.error(f"❌ Ошибка при работе бота: {e}")

def keep_alive():
    """Периодически пингует URL для поддержания активности"""
    url = "https://telegram-bot-9kxx.onrender.com"
    while True:
        try:
            response = requests.get(url)
            logger.info(f"Keep-alive ping sent. Status: {response.status_code}")
        except Exception as e:
            logger.error(f"Keep-alive error: {e}")
        time.sleep(300)  # 5 минут

def start_keep_alive():
    """Запускает бота, функцию keep-alive и Flask-сервер"""
    # Запуск бота в отдельном демоническом потоке
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    logger.info("🚀 Бот запущен...")

    # Запуск keep-alive в отдельном демоническом потоке
    keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
    keep_alive_thread.start()
    logger.info("Keep-alive thread started")

    # Запуск Flask-сервера (блокирующий вызов)
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    start_keep_alive()
