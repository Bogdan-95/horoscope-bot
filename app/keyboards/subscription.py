# app/keyboards/subscription.py
# Клавиатуры для управления подпиской

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


# ===== ГЛАВНОЕ МЕНЮ ПОДПИСКИ =====
def subscription_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="✅ Включить", callback_data="subscribe_on")
    builder.button(text="❌ Выключить", callback_data="subscribe_off")
    builder.button(text="⏰ Изменить время", callback_data="change_time")
    builder.button(text="📋 Моя подписка", callback_data="my_subscription")
    builder.button(text="⬅️ В меню", callback_data="menu")

    builder.adjust(2, 2, 1)
    return builder.as_markup()


# ===== ВЫБОР ВРЕМЕНИ (06:00 - 10:30 с шагом 30 мин) =====
def time_selection_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    # Генерируем время с 06:00 до 10:30 с шагом 30 минут
    times = []
    for hour in [6, 7, 8, 9, 10]:
        for minute in ["00", "30"]:
            if hour == 10 and minute == "30":
                times.append("10:30")
                break
            time_str = f"{hour:02d}:{minute}"
            times.append(time_str)

    # Добавляем кнопки с эмодзи
    emoji_times = {
        "06:00": "🌅", "06:30": "🌅",
        "07:00": "☀️", "07:30": "☀️",
        "08:00": "🌞", "08:30": "🌞",
        "09:00": "🌟", "09:30": "🌟",
        "10:00": "✨", "10:30": "✨"
    }

    for time_str in times:
        emoji = emoji_times.get(time_str, "🕐")
        builder.button(
            text=f"{emoji} {time_str}",
            callback_data=f"set_time:{time_str}"  # Передаём полное время
        )

    builder.adjust(3, 3, 3, 1)

    builder.row(
        InlineKeyboardButton(text="↩️ Назад", callback_data="subscription"),
        InlineKeyboardButton(text="⬅️ В меню", callback_data="menu")
    )

    return builder.as_markup()


# ===== ИНФОРМАЦИЯ О ПОДПИСКЕ =====
def subscription_info_kb(has_subscription: bool = True) -> InlineKeyboardMarkup:
    """
        Клавиатура информации о подписке в зависимости от статуса.

        Args:
            has_subscription (bool): True если пользователь подписан

        Returns:
            InlineKeyboardMarkup: Клавиатура управления подпиской
        """
    if has_subscription:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="❌ Отписаться", callback_data="unsubscribe"),
                    InlineKeyboardButton(text="⏰ Изменить время", callback_data="change_time")
                ],
                [
                    InlineKeyboardButton(text="⬅️ В меню", callback_data="menu")
                ]
            ]
        )
    else:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Включить", callback_data="subscribe_on")
                ],
                [
                    InlineKeyboardButton(text="⬅️ В меню", callback_data="menu")
                ]
            ]
        )


# ===== ПОДТВЕРЖДЕНИЕ ОТПИСКИ =====
def unsubscribe_confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да, отписаться", callback_data="confirm_unsubscribe"),
                InlineKeyboardButton(text="❌ Нет, остаться", callback_data="my_subscription")
            ],
            [
                InlineKeyboardButton(text="⬅️ В меню", callback_data="menu")
            ]
        ]
    )


# ===== ПОДТВЕРЖДЕНИЕ ВКЛЮЧЕНИЯ =====
def subscribe_confirm_kb(time_str: str = None) -> InlineKeyboardMarkup:
    """
        Клавиатура подтверждения включения подписки.

        Args:
            time_str (Optional[str]): Предустановленное время (например, "09:00")

        Returns:
            InlineKeyboardMarkup: Клавиатура подтверждения подписки
        """

    buttons = []

    if time_str:
        buttons.append([
            InlineKeyboardButton(
                text=f"✅ Включить на {time_str}",
                callback_data="confirm_subscribe"
            )
        ])
    else:
        buttons.append([
            InlineKeyboardButton(text="✅ Включить", callback_data="confirm_subscribe")
        ])

    buttons.append([
        InlineKeyboardButton(text="⏰ Другое время", callback_data="change_time"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="subscription")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)