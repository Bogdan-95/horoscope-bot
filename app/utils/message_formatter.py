# app/utils/message_formatter.py
# Форматирование красивых сообщений

def format_subscription_message(user_data: dict, subscription: dict) -> str:
    """Форматирует сообщение о подписке"""

    sign_display = user_data['sign'].capitalize() if user_data and user_data.get('sign') else "не выбран"

    # Получаем и форматируем время
    if subscription and 'notification_time' in subscription:
        time_display = subscription['notification_time']
        # Убеждаемся, что время в формате HH:MM
        if ":" not in time_display and time_display.isdigit():
            time_display = f"{time_display}:00"
    else:
        time_display = "09:00"

    # Эмодзи для статуса
    if subscription and subscription.get('is_subscribed'):
        status_emoji = "🟢"
        status_text = "АКТИВНА"
        time_emoji = get_time_emoji(time_display)
    else:
        status_emoji = "🔴"
        status_text = "НЕАКТИВНА"
        time_emoji = "⏰"

    message = (
        f"🔔 *ВАША ПОДПИСКА* {status_emoji}\n\n"
        f"📊 *Статус:* **{status_text}**\n"
        f"✨ *Знак:* **{sign_display}**\n"
        f"{time_emoji} *Время:* **{time_display}** (МСК)\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )

    if subscription and subscription.get('is_subscribed'):
        message += (
            f"📬 *Что вы получаете:*\n"
            f"• Персональный гороскоп для **{sign_display}**\n"
            f"• Автоматически каждый день в **{time_display}**\n"
            f"• Детальный прогноз на день\n\n"
            f"💡 *Управление:*\n"
            f"Меняйте время или отписывайтесь когда удобно."
        )
    else:
        message += (
            f"📭 *Подписка не активна*\n\n"
            f"Включите её, чтобы получать:\n"
            f"• Персональные гороскопы\n"
            f"• Автоматически в удобное время\n"
            f"• Ежедневные прогнозы"
        )

    return message


def get_time_emoji(time_str: str) -> str:
    """Возвращает эмодзи для времени"""
    try:
        # Разбираем время (формат "HH:MM" или "HH")
        if ":" in time_str:
            hour = int(time_str.split(":")[0])
        else:
            hour = int(time_str)

        if 5 <= hour < 7:
            return "🌅"  # Рассвет
        elif 7 <= hour < 9:
            return "☀️"  # Утро
        elif 9 <= hour < 11:
            return "🌞"  # День
        elif 11 <= hour < 14:
            return "🌟"  # Обед
        elif 14 <= hour < 18:
            return "🌇"  # Вечер
        else:
            return "🌙"  # Ночь
    except:
        return "⏰"


def format_horoscope_message(user_name: str, sign: str, horoscope: str, time_str: str = None) -> str:
    """Форматирует сообщение с гороскопом"""

    sign_display = sign.capitalize()

    # Форматируем время, если оно есть
    if time_str:
        # Убеждаемся, что время в формате HH:MM
        if ":" not in time_str and time_str.isdigit():
            time_str = f"{time_str}:00"
        time_part = f"🕐 *Время отправки:* {time_str}\n\n"
    else:
        time_part = ""

    # Определяем приветствие по времени
    from datetime import datetime
    now = datetime.now()
    if now.hour < 12:
        greeting = f"🌅 *Доброе утро, {user_name}!*"
    elif now.hour < 18:
        greeting = f"☀️ *Добрый день, {user_name}!*"
    else:
        greeting = f"🌙 *Добрый вечер, {user_name}!*"

    return (
        f"{greeting}\n\n"
        f"✨ *Ваш ежедневный гороскоп для {sign_display}*\n"
        f"{time_part}"
        f"{horoscope}\n\n"
        f"_Хорошего дня!_ 🌟\n\n"
        f"💡 *Управление подпиской:* /subscription"
    )