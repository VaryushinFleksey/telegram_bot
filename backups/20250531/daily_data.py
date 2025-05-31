import json
from datetime import datetime, timedelta
import os
from nicknames import NICKNAMES
import random

# Файл для хранения данных
DATA_FILE = 'daily_nickname.json'

class DailyData:
    def __init__(self):
        self.data_file = DATA_FILE

    def load_data(self, chat_id):
        """Загружает данные из файла"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
                # Преобразуем строку даты обратно в datetime
                if data.get('last_update'):
                    data['last_update'] = datetime.fromisoformat(data['last_update'])
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                'nickname': None,
                'last_update': None,
                'assigned_to': None,
                'chat_name': None,
                'chat_type': None
            }

    def save_data(self, chat_id, data):
        """Сохраняет данные в файл"""
        # Преобразуем datetime в строку для JSON
        if data.get('last_update'):
            data = data.copy()
            data['last_update'] = data['last_update'].isoformat()
        
        with open(self.data_file, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def need_new_nickname(self, chat_id):
        """Проверяет, нужно ли обновить погоняло дня"""
        data = self.load_data(chat_id)
        if not data['last_update']:
            return True
        
        last_update = data['last_update']
        now = datetime.now()
        
        # Проверяем, прошли ли сутки
        return (now - last_update) > timedelta(days=1)

    def get_current_nickname(self, chat_id):
        """Получает текущее погоняло дня и информацию о нём"""
        return self.load_data(chat_id)

    def set_nickname(self, chat_id, nickname, chat_name, chat_type):
        """Устанавливает новое погоняло дня"""
        data = {
            'nickname': nickname,
            'last_update': datetime.now(),
            'assigned_to': None,
            'chat_name': chat_name,
            'chat_type': chat_type
        }
        self.save_data(chat_id, data)
        return data

    def assign_nickname(self, chat_id, username):
        """Присваивает текущее погоняло пользователю"""
        data = self.load_data(chat_id)
        data['assigned_to'] = username
        self.save_data(chat_id, data)
        return data

    def get_random_nickname(self):
        """Возвращает случайное погоняло из списка"""
        return random.choice(NICKNAMES) 