# Основной код бота
import telebot
from telebot import types
import config
from horoscope import Horoscope
import time
from utils import UserStats
from datetime import datetime
import logging
import sys
import traceback

# ==================== ПРОСТАЯ НАСТРОЙКА ЛОГИРОВАНИЯ ====================
# Отключаем все handlers
logging.basicConfig(level=logging.WARNING)  # Только ошибки для корневого логгера

# Создаем свой логгер
logger = logging.getLogger('horoscope_bot')
logger.setLevel(logging.INFO)

# Удаляем все handlers чтобы не было дублирования
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# Только консольный handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Простой формат без цвета (чтобы не было дублирования)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)

# Файловый логгер
file_handler = logging.FileHandler('bot.log', encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# ==================== КОНЕЦ НАСТРОЙКИ ЛОГИРОВАНИЯ ====================

# Инициализация бота
bot = telebot.TeleBot(config.BOT_TOKEN)
horoscope = Horoscope()
user_stats = UserStats()

# Логируем запуск
logger.info("=" * 60)
logger.info("🚀 БОТ ЗАПУЩЕН")
logger.info(f"📅 Дата: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
logger.info(f"🤖 Имя бота: @{bot.get_me().username}")
logger.info("=" * 60)


# Словарь для хранения состояния пользователей
user_states = {}


# ==================== КОМАНДЫ БОТА ====================

# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Обработчик команды /start"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    username = message.from_user.username

    logger.info(f"👤 /start от {user_id} ({user_name} @{username})")

    welcome_text = f"""
👋 *Привет, {user_name}!*

Я - *бот-гороскоп!* 🌟
Я могу рассказать твой гороскоп на сегодня.

📌 *Доступные команды:*
/horoscope - Получить гороскоп
/signs - Список знаков зодиака
/help - Помощь

*Выбери свой знак зодиака ниже или используй команды!* ✨
"""

    # Создаем клавиатуру
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)

    # Добавляем кнопки со знаками зодиака
    signs = horoscope.get_keyboard_signs()
    for row in signs:
        markup.add(*[types.KeyboardButton(sign) for sign in row])

    markup.add(types.KeyboardButton("Помощь 🆘"))

    try:
        bot.send_message(message.chat.id, welcome_text,
                         parse_mode='Markdown', reply_markup=markup)
        logger.debug(f"✅ Приветствие отправлено {user_id}")
    except Exception as e:
        logger.error(f"❌ Ошибка отправки приветствия {user_id}: {e}")


# Команда /help
@bot.message_handler(commands=['help'])
def send_help(message):
    """Обработчик команды /help"""
    user_id = message.from_user.id
    logger.info(f"❓ /help от {user_id}")

    help_text = """
📖 *ПОМОЩЬ ПО БОТУ*

*Как получить гороскоп?*
1. Нажми на кнопку со своим знаком зодиака
2. Или отправь название своего знака
3. Или используй команду /horoscope

*Доступные знаки:*
♈ Овен
♉ Телец
♊ Близнецы
♋ Рак
♌ Лев
♍ Дева
♎ Весы
♏ Скорпион
♐ Стрелец
♑ Козерог
♒ Водолей
♓ Рыбы

*Команды:*
/start - Начать общение
/horoscope - Выбрать знак зодиака
/signs - Список всех знаков
/help - Эта справка

✨ Бот обновляет гороскопы ежедневно!
"""

    try:
        bot.send_message(message.chat.id, help_text, parse_mode='Markdown')
        logger.debug(f"✅ Справка отправлена {user_id}")
    except Exception as e:
        logger.error(f"❌ Ошибка отправки справки {user_id}: {e}")


# Команда /horoscope
@bot.message_handler(commands=['horoscope'])
def ask_horoscope(message):
    """Показать inline клавиатуру для выбора знака"""
    user_id = message.from_user.id
    logger.info(f"✨ /horoscope от {user_id}")

    markup = types.InlineKeyboardMarkup(row_width=3)

    # Создаем inline кнопки
    buttons = []
    for sign_ru in horoscope.zodiac_signs.keys():
        emoji = horoscope.zodiac_emojis.get(sign_ru, '✨')
        buttons.append(
            types.InlineKeyboardButton(
                f"{emoji} {sign_ru.capitalize()}",
                callback_data=f"sign_{sign_ru}"
            )
        )

    # Распределяем кнопки по 3 в строку
    for i in range(0, len(buttons), 3):
        markup.add(*buttons[i:i + 3])

    try:
        bot.send_message(
            message.chat.id,
            "✨ *Выбери свой знак зодиака:*",
            parse_mode='Markdown',
            reply_markup=markup
        )
        logger.debug(f"✅ Клавиатура знаков отправлена {user_id}")
    except Exception as e:
        logger.error(f"❌ Ошибка отправки клавиатуры {user_id}: {e}")


# Команда /signs
@bot.message_handler(commands=['signs'])
def send_signs_list(message):
    """Показать список всех знаков зодиака"""
    user_id = message.from_user.id
    logger.info(f"📋 /signs от {user_id}")

    signs_list = horoscope.get_all_signs()
    response = "📜 *Знаки зодиака:*\n\n" + "\n".join(signs_list)

    try:
        bot.send_message(message.chat.id, response, parse_mode='Markdown')
        logger.debug(f"✅ Список знаков отправлен {user_id}")
    except Exception as e:
        logger.error(f"❌ Ошибка отправки списка знаков {user_id}: {e}")


# Команда /stats (только для администратора)
@bot.message_handler(commands=['stats'])
def show_stats(message):
    """Показать статистику бота (только для админа)"""
    user_id = message.from_user.id
    logger.info(f"📊 Запрос /stats от {user_id}")

    # Укажите ваш Telegram ID здесь
    ADMIN_IDS = [930734096]  # Замените на ваш ID или добавьте несколько

    if user_id not in ADMIN_IDS:
        logger.warning(f"⚠️ Попытка доступа к stats не-админом {user_id}")
        bot.reply_to(message, "⛔ Эта команда только для администратора")
        return

    try:
        stats = user_stats.get_total_stats()
        stats_text = f"""
📊 *СТАТИСТИКА БОТА*

👥 Всего пользователей: *{stats['total_users']}*
📨 Всего запросов: *{stats['total_requests']}*
⭐ Самый популярный знак: *{stats['most_popular_sign']}*
🔢 Запросов для этого знака: *{stats['most_popular_count']}*

📅 *Дата:* {datetime.now().strftime('%d.%m.%Y %H:%M')}
"""
        bot.send_message(message.chat.id, stats_text, parse_mode='Markdown')
        logger.info(f"📈 Статистика отправлена админу {user_id}")
    except Exception as e:
        logger.error(f"❌ Ошибка получения статистики: {e}")
        bot.reply_to(message, "❌ Ошибка при получении статистики")


# ==================== ОБРАБОТКА ТЕКСТОВЫХ СООБЩЕНИЙ ====================

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    """Обработчик текстовых сообщений"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    text = message.text.lower().strip()

    logger.info(f"💬 Текст от {user_id} ({user_name}): '{text}'")

    # Проверяем команды
    if text == '/start' or text == 'start':
        send_welcome(message)
        return

    # Если нажали "Помощь"
    if "помощь" in text or "🆘" in text:
        send_help(message)
        return

    # Проверяем, является ли текст знаком зодиака
    if text in horoscope.zodiac_signs:
        logger.info(f"🔮 Запрос гороскопа для знака: {text}")
        send_horoscope_to_user(message.chat.id, text, user_id)
    else:
        # Если не знак - предлагаем выбрать
        logger.warning(f"⚠️ Неизвестный запрос от {user_id}: '{text}'")
        try:
            bot.send_message(
                message.chat.id,
                "🤔 Я не понял ваш запрос.\n\n"
                "Выберите знак зодиака на клавиатуре ниже или используйте команду /horoscope",
                reply_markup=types.ReplyKeyboardRemove()
            )
            ask_horoscope(message)
        except Exception as e:
            logger.error(f"❌ Ошибка обработки неизвестного запроса {user_id}: {e}")


# ==================== ОБРАБОТКА CALLBACK КНОПОК ====================

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    """Обработчик inline кнопок"""
    user_id = call.from_user.id
    user_name = call.from_user.first_name
    callback_data = call.data

    logger.info(f"🔄 Callback от {user_id} ({user_name}): {callback_data}")

    if callback_data.startswith("sign_"):
        sign = callback_data[5:]  # Убираем "sign_"
        logger.info(f"✅ Выбран знак: {sign} для пользователя {user_id}")

        try:
            bot.answer_callback_query(call.id, f"🔮 Готовлю гороскоп для {sign}...")
            send_horoscope_to_user(call.message.chat.id, sign, user_id)
        except Exception as e:
            logger.error(f"❌ Ошибка обработки callback знака: {e}")
            bot.answer_callback_query(call.id, "❌ Ошибка, попробуйте еще раз")

    elif callback_data == "get_another":
        logger.info(f"🔄 Запрос другого гороскопа от {user_id}")

        try:
            bot.answer_callback_query(call.id, "✨ Выберите другой знак")
            ask_horoscope(call.message)
        except Exception as e:
            logger.error(f"❌ Ошибка обработки get_another: {e}")


# ==================== ФУНКЦИЯ ОТПРАВКИ ГОРОСКОПА ====================

def send_horoscope_to_user(chat_id, sign_ru, user_id):
    """Основная функция отправки гороскопа"""
    try:
        # Логируем запрос в статистику
        user_stats.add_request(user_id, sign_ru)
        logger.info(f"📊 Статистика обновлена для {user_id} - знак: {sign_ru}")

        # Отправляем "типинг" действие
        bot.send_chat_action(chat_id, 'typing')
        time.sleep(0.5)  # Небольшая задержка для реалистичности

        # Получаем гороскоп
        logger.debug(f"🔍 Получение гороскопа для знака: {sign_ru}")
        horoscope_text = horoscope.get_online_horoscope(sign_ru)

        if horoscope_text:
            logger.info(f"✅ Гороскоп получен успешно для {sign_ru}")

            try:
                # Отправляем гороскоп
                bot.send_message(chat_id, horoscope_text, parse_mode='Markdown')

                # Добавляем кнопку для другого гороскопа
                markup = types.InlineKeyboardMarkup()
                markup.add(
                    types.InlineKeyboardButton(
                        "🔮 Получить другой гороскоп",
                        callback_data="get_another"
                    )
                )

                bot.send_message(
                    chat_id,
                    "✨ Хочешь узнать гороскоп для другого знака?",
                    reply_markup=markup
                )

                logger.debug(f"✅ Гороскоп отправлен {user_id} для знака {sign_ru}")

            except Exception as e:
                logger.error(f"❌ Ошибка отправки сообщения {user_id}: {e}")

        else:
            logger.error(f"❌ Не удалось получить гороскоп для {sign_ru}")
            bot.send_message(
                chat_id,
                f"😕 Извините, не удалось получить гороскоп для *{sign_ru}*.\n"
                "Попробуйте позже или выберите другой знак.",
                parse_mode='Markdown'
            )

    except Exception as e:
        logger.error(f"❌ Критическая ошибка при отправке гороскопа: {e}")

        try:
            bot.send_message(
                chat_id,
                "❌ Произошла ошибка при получении гороскопа.\n"
                "Пожалуйста, попробуйте еще раз через пару минут.",
                parse_mode='Markdown'
            )
        except:
            pass  # Если не можем отправить сообщение об ошибке


# ==================== ОБРАБОТКА МЕДИА ====================

@bot.message_handler(content_types=['audio', 'video', 'document', 'photo', 'sticker', 'voice'])
def handle_media(message):
    """Обработчик медиа-сообщений"""
    user_id = message.from_user.id
    content_type = message.content_type

    logger.warning(f"⚠️ Получен {content_type} от {user_id}")

    try:
        bot.reply_to(
            message,
            "😊 Я понимаю только текстовые сообщения и команды.\n"
            "Используйте кнопки или команды для получения гороскопа! ✨"
        )
    except Exception as e:
        logger.error(f"❌ Ошибка обработки медиа {user_id}: {e}")


# ==================== ЗАПУСК БОТА ====================

def start_bot():
    """Функция запуска бота"""
    logger.info("🟢 НАЧИНАЮ ЗАПУСК БОТА...")

    try:
        bot_info = bot.get_me()
        logger.info(f"🤖 Бот: @{bot_info.username} (ID: {bot_info.id})")
        logger.info(f"👋 Приветственное сообщение: {bot_info.first_name}")
        logger.info("🟢 БОТ ЗАПУЩЕН И ГОТОВ К РАБОТЕ!")
        logger.info("=" * 60)

        # Запускаем polling БЕЗ restart_on_change
        bot.infinity_polling(timeout=60, long_polling_timeout=60)

    except Exception as e:
        logger.critical(f"🔴 КРИТИЧЕСКАЯ ОШИБКА: {e}")
        logger.info("🔄 Перезапуск через 10 секунд...")
        time.sleep(10)
        start_bot()


if __name__ == "__main__":
    while True:
        try:
            start_bot()
        except KeyboardInterrupt:
            logger.info("🛑 Бот остановлен пользователем")
            sys.exit(0)
        except Exception as e:
            logger.critical(f"💀 Критическая ошибка: {e}")
            logger.error(traceback.format_exc())
            logger.info("🔄 Перезапуск через 30 секунд...")
            time.sleep(30)