import os
import random
import telebot
from dotenv import load_dotenv
from nicknames import NICKNAMES, add_nickname
from daily_data import DailyData
import stats
import html
from bot_log import logger
from keep_alive import start_keep_alive

# Загружаем токен из переменных окружения или .env файла
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN", '7842827025:AAHUEEI-v__l6X2HgHAawmNMeKtCcUxNxus')

# Инициализируем бота
bot = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML')
daily_data = DailyData()

def get_user_mention(user):
    """Создает кликабельное упоминание пользователя"""
    name = user.first_name
    if user.username:
        name = f"@{user.username}"
    return f'<a href="tg://user?id={user.id}">{name}</a>'

# Устанавливаем команды бота
bot.set_my_commands([
    telebot.types.BotCommand("start", "Запустить бота и получить список команд"),
    telebot.types.BotCommand("nickname", "Выбрать погоняло дня"),
    telebot.types.BotCommand("assign", "Присвоить погоняло случайному участнику"),
    telebot.types.BotCommand("add_nickname", "Добавить новое погоняло в список"),
    telebot.types.BotCommand("list", "Показать список всех погонял"),
    telebot.types.BotCommand("stats", "Показать общую статистику погонял"),
    telebot.types.BotCommand("mystats", "Показать статистику погонял конкретного пользователя")
])

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message,
        "👋 Привет! Я бот для выбора погоняла дня.\n"
        "🎭 Команды:\n"
        "/nickname - выбрать погоняло дня\n"
        "/assign - присвоить погоняло случайному участнику\n"
        "/add_nickname - добавить новое погоняло в список\n"
        "/list - показать все погоняла\n"
        "/stats - показать общую статистику погонял\n"
        "/mystats - показать статистику погонял конкретного пользователя"
    )

@bot.message_handler(commands=['list'])
def list_nicknames(message):
    try:
        # Формируем список с номерами
        numbered_list = [f"{i+1}. {nickname}" for i, nickname in enumerate(NICKNAMES)]
        
        # Разбиваем на части по 20 погонял
        chunks = [numbered_list[i:i+20] for i in range(0, len(numbered_list), 20)]
        
        # Отправляем первое сообщение с заголовком
        header = f"📋 Список всех погонял ({len(NICKNAMES)} шт.):\n\n"
        bot.send_message(message.chat.id, header + "\n".join(chunks[0]))
        
        # Отправляем остальные части списка
        for chunk in chunks[1:]:
            bot.send_message(message.chat.id, "\n".join(chunk))
            
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка при получении списка: {str(e)}")

@bot.message_handler(commands=['nickname'])
def choose_nickname(message):
    chat_id = str(message.chat.id)
    chat = message.chat
    chat_name = chat.title if chat.type != 'private' else f"Чат с {chat.first_name}"
    chat_type = chat.type
    
    if daily_data.need_new_nickname(chat_id):
        # Выбираем новое погоняло
        new_nickname = daily_data.get_random_nickname()
        # Сохраняем его вместе с информацией о чате
        data = daily_data.set_nickname(chat_id, new_nickname, chat_name, chat_type)
        
        bot.reply_to(message, 
            f"🎭 Погоняло дня в этом чатике сегодня: <b>{new_nickname}</b>\n"
            "Используйте /assign чтобы присвоить его случайному участнику!",
            parse_mode='HTML'
        )
    else:
        # Показываем текущее погоняло
        data = daily_data.get_current_nickname(chat_id)
        nickname = data['nickname']
        assigned_to = data['assigned_to']
        
        response = f"🎭 Погоняло дня в этом чатике сегодня: <b>{nickname}</b>\n"
        if assigned_to:
            response += f"Погоняло дня сегодня у {assigned_to}"
        else:
            response += "Еще никому не присвоено! Используйте /assign"
        
        bot.reply_to(message, response, parse_mode='HTML')

@bot.message_handler(commands=['assign'])
def assign_nickname_handler(message):
    chat_id = str(message.chat.id)
    data = daily_data.get_current_nickname(chat_id)
    
    if not data['nickname']:
        bot.reply_to(message, 
            "❌ Сначала нужно выбрать погоняло дня!\n"
            "Используйте команду /nickname"
        )
        return

    if data['assigned_to']:
        bot.reply_to(message,
            f"🎭 Погоняло <b>{data['nickname']}</b> сегодня у {data['assigned_to']}",
            parse_mode='HTML'
        )
        return

    # Получаем список участников чата
    try:
        chat_members = bot.get_chat_administrators(message.chat.id)
        # Исключаем ботов из списка
        real_members = [member.user for member in chat_members if not member.user.is_bot]
        
        if not real_members:
            bot.reply_to(message, "❌ Не могу найти участников чата!")
            return
        
        # Выбираем случайного участника
        lucky_member = random.choice(real_members)
        
        # Создаем кликабельное упоминание пользователя
        user_mention = get_user_mention(lucky_member)
        
        # Сохраняем информацию о том, кому присвоено погоняло
        data = daily_data.assign_nickname(chat_id, user_mention)
        
        # Обновляем статистику
        stats.update_stats(data['nickname'], user_mention)
        
        # Отправляем сообщение с упоминанием
        bot.reply_to(message,
            f"🎉 Поздравляем! Погоняло <b>{data['nickname']}</b> сегодня у {user_mention}",
            parse_mode='HTML'
        )
    except Exception as e:
        print(f"Error in assign_nickname_handler: {str(e)}")  # Добавляем логирование ошибки
        bot.reply_to(message, 
            "❌ Не могу получить список участников чата.\n"
            "Убедитесь, что я администратор группы!"
        )

@bot.message_handler(commands=['add_nickname'])
def add_new_nickname(message):
    try:
        # Получаем текст после команды
        nickname = message.text.split('/add_nickname ', 1)[1].strip()
        if not nickname:
            raise IndexError
        
        # Добавляем новое погоняло
        if add_nickname(nickname):
            bot.reply_to(message, f"✅ Погоняло <b>{nickname}</b> успешно добавлено в список!", parse_mode='HTML')
        else:
            bot.reply_to(message, "❌ Не удалось добавить погоняло. Попробуйте позже.")
    except IndexError:
        bot.reply_to(message, 
            "❌ Укажите погоняло после команды!\n"
            "Пример: `/add_nickname Властелин Пиццы`",
            parse_mode='HTML'
        )
    except Exception as e:
        bot.reply_to(message, f"❌ Произошла ошибка: {str(e)}")

@bot.message_handler(commands=['stats'])
def show_stats(message):
    """Показывает общую статистику погонял"""
    top_nicknames = stats.get_top_nicknames()
    top_users = stats.get_top_users()
    recent = stats.get_recent_history()
    
    response = "📊 <b>Статистика погонял:</b>\n\n"
    
    # Топ погонял
    response += "🏆 <b>Топ-5 погонял:</b>\n"
    for i, (nickname, count) in enumerate(top_nicknames, 1):
        response += f"{i}. {html.escape(nickname)} - {count} раз(а)\n"
    
    response += "\n👥 <b>Топ-5 пользователей:</b>\n"
    for i, (user, count) in enumerate(top_users, 1):
        response += f"{i}. {user} - {count} погонял(о)\n"
    
    response += "\n📜 <b>Последние назначения:</b>\n"
    for entry in reversed(recent[:5]):
        date = entry['date'].split('T')[0]
        if entry['assigned_to']:
            response += f"• {html.escape(entry['nickname'])} → {entry['assigned_to']} ({date})\n"
        else:
            response += f"• {html.escape(entry['nickname'])} ({date})\n"
    
    bot.reply_to(message, response)

@bot.message_handler(commands=['mystats'])
def show_user_stats(message):
    """Показывает статистику погонял конкретного пользователя"""
    user_mention = f'<a href="tg://user?id={message.from_user.id}">{html.escape(message.from_user.first_name)}</a>'
    history = stats.get_user_history(user_mention)
    
    if not history:
        bot.reply_to(message, f"У {user_mention} пока нет истории погонял 😢")
        return
    
    response = f"📊 <b>Статистика {user_mention}:</b>\n\n"
    response += "Последние 5 погонял:\n"
    
    for entry in reversed(history[-5:]):
        date = entry['date'].split('T')[0]
        response += f"• {html.escape(entry['nickname'])} ({date})\n"
    
    total = len(history)
    response += f"\nВсего получено погонял: {total}"
    
    bot.reply_to(message, response)

# Обновляем существующие функции для сбора статистики
def update_daily_nickname():
    nickname = daily_data.get_random_nickname()
    daily_data.update_daily_nickname(nickname)
    stats.update_stats(nickname)  # Добавляем в статистику
    return nickname

def assign_nickname_to_user(message):
    chat_id = message.chat.id
    nickname = daily_data.get_random_nickname()
    
    if message.reply_to_message:
        user = message.reply_to_message.from_user
        user_mention = f'<a href="tg://user?id={user.id}">{html.escape(user.first_name)}</a>'
    else:
        members = [member for member in bot.get_chat_administrators(chat_id) 
                  if not member.user.is_bot]
        if not members:
            bot.reply_to(message, "Не удалось найти участников чата 😢")
            return
        member = random.choice(members)
        user_mention = f'<a href="tg://user?id={member.user.id}">{html.escape(member.user.first_name)}</a>'
    
    stats.update_stats(nickname, user_mention)  # Добавляем в статистику
    bot.reply_to(message, f"🎯 {user_mention} получает погоняло: <b>{html.escape(nickname)}</b>")

if __name__ == "__main__":
    # Запускаем поддержание активности
    start_keep_alive()
    
    # Запускаем бота
    logger.info("🚀 Бот запущен...")
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        logger.error(f"❌ Ошибка при работе бота: {e}")
    finally:
        logger.info("Бот остановлен") 