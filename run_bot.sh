#!/bin/bash

# Переходим в директорию бота
cd "$(dirname "$0")"

# Активируем виртуальное окружение
source venv/bin/activate

while true; do
    echo "Запуск бота..."
    python bot.py
    echo "Бот остановлен, перезапуск через 5 секунд..."
    sleep 5
done 