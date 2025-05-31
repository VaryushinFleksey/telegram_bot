import json
from datetime import datetime, timedelta
from collections import defaultdict

# Файл для хранения статистики
STATS_FILE = 'nickname_stats.json'

def load_stats():
    """Загружает статистику из файла"""
    try:
        with open(STATS_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Создаем начальную структуру статистики
        initial_stats = {
            'nickname_counts': {},  # Сколько раз выпадало каждое погоняло
            'user_nicknames': {},   # Какие погоняла были у каждого пользователя
            'history': [],          # История последних погонял
            'top_users': {},        # Топ пользователей по количеству погонял
            'last_update': datetime.now().isoformat()  # Время последнего обновления статистики
        }
        # Сразу сохраняем начальную структуру в файл
        with open(STATS_FILE, 'w', encoding='utf-8') as file:
            json.dump(initial_stats, file, ensure_ascii=False, indent=4)
        return initial_stats

def save_stats(stats):
    """Сохраняет статистику в файл"""
    with open(STATS_FILE, 'w', encoding='utf-8') as file:
        json.dump(stats, file, ensure_ascii=False, indent=4)

def update_stats(nickname, user_mention=None):
    """Обновляет статистику при назначении погоняла"""
    stats = load_stats()
    
    # Обновляем счетчик погоняла
    stats['nickname_counts'][nickname] = stats['nickname_counts'].get(nickname, 0) + 1
    
    # Если погоняло кому-то присвоено
    if user_mention:
        # Обновляем историю погонял пользователя
        if user_mention not in stats['user_nicknames']:
            stats['user_nicknames'][user_mention] = []
        stats['user_nicknames'][user_mention].append({
            'nickname': nickname,
            'date': datetime.now().isoformat()
        })
        
        # Обновляем топ пользователей
        stats['top_users'][user_mention] = stats['top_users'].get(user_mention, 0) + 1
    
    # Добавляем в историю
    stats['history'].append({
        'nickname': nickname,
        'assigned_to': user_mention,
        'date': datetime.now().isoformat()
    })
    
    # Оставляем только последние 30 записей в истории
    stats['history'] = stats['history'][-30:]
    
    # Обновляем время последнего обновления
    stats['last_update'] = datetime.now().isoformat()
    
    save_stats(stats)
    return stats

def get_top_nicknames(limit=5):
    """Возвращает топ самых частых погонял"""
    stats = load_stats()
    sorted_nicknames = sorted(
        stats['nickname_counts'].items(),
        key=lambda x: x[1],
        reverse=True
    )
    return sorted_nicknames[:limit]

def get_user_history(user_mention):
    """Возвращает историю погонял пользователя"""
    stats = load_stats()
    return stats['user_nicknames'].get(user_mention, [])

def get_recent_history(limit=5):
    """Возвращает последние назначенные погоняла"""
    stats = load_stats()
    return stats['history'][-limit:]

def get_top_users(limit=5):
    """Возвращает топ пользователей по количеству полученных погонял"""
    stats = load_stats()
    sorted_users = sorted(
        stats['top_users'].items(),
        key=lambda x: x[1],
        reverse=True
    )
    return sorted_users[:limit]

def get_weekly_stats():
    """Возвращает статистику за последнюю неделю"""
    stats = load_stats()
    week_ago = datetime.now() - timedelta(days=7)
    
    # Фильтруем историю за последнюю неделю
    weekly_history = [
        entry for entry in stats['history']
        if datetime.fromisoformat(entry['date']) > week_ago
    ]
    
    # Собираем статистику по погонялам за неделю
    weekly_nicknames = defaultdict(int)
    weekly_users = defaultdict(int)
    
    for entry in weekly_history:
        weekly_nicknames[entry['nickname']] += 1
        if entry['assigned_to']:
            weekly_users[entry['assigned_to']] += 1
    
    return {
        'top_nicknames': sorted(weekly_nicknames.items(), key=lambda x: x[1], reverse=True)[:5],
        'top_users': sorted(weekly_users.items(), key=lambda x: x[1], reverse=True)[:5],
        'total_assignments': len(weekly_history)
    } 