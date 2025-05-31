from flask import Flask
import threading
import time
import requests
from bot_log import logger

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/health')
def health():
    return {"status": "healthy"}, 200

def run_flask():
    """Запускает Flask сервер"""
    app.run(host='0.0.0.0', port=10000, debug=False, use_reloader=False)

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
    """Запускает поддержание активности и Flask сервер в отдельных потоках"""
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("Flask server started")
    
    keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
    keep_alive_thread.start()
    logger.info("Keep-alive thread started")

if __name__ == "__main__":
    start_keep_alive()
    # Чтобы основной поток не завершился и не остановил демоны, можно сделать так:
    while True:
        time.sleep(60)
