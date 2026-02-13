# app/keyboards/main.py
# Главные меню и базовые клавиатуры

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ===== ЭМОДЗИ ЗНАКОВ =====
SIGNS_EMOJI = {
    "овен": "♈", "телец": "♉", "близнецы": "♊", "рак": "♋",
    "лев": "♌", "дева": "♍", "весы": "♎", "скорпион": "♏",
    "стрелец": "♐", "козерог": "♑", "водолей": "♒", "рыбы": "♓",
}

SIGNS = list(SIGNS_EMOJI.keys())


# ===== REPLY КЛАВИАТУРА (ПОСТОЯННАЯ ВНИЗУ) =====
def reply_main_menu() -> ReplyKeyboardMarkup:
    """Создает reply-клавиатуру с кнопкой главного меню"""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="✨ Главное меню")]],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )


# ===== ГЛАВНОЕ МЕНЮ INLINE =====
def main_menu_kb() -> InlineKeyboardMarkup:
    """Создает главное меню с основными функциями бота"""
    builder = InlineKeyboardBuilder()

    builder.button(text="🔮 Гороскоп", callback_data="daily_horoscope")
    builder.button(text="❤️ Совместимость", callback_data="compatibility")
    builder.button(text="♻️ Выбрать знак", callback_data="choose_sign")
    builder.button(text="🔔 Рассылка", callback_data="subscription")
    builder.button(text="🆘 Помощь", callback_data="help")

    builder.adjust(2, 2, 1)
    return builder.as_markup()


# ===== ВЫБОР ЗНАКА ЗОДИАКА =====
def zodiac_kb(prefix: str = "sign:") -> InlineKeyboardMarkup:
    """Создает клавиатуру для выбора знака зодиака

    Args:
        prefix: Префикс для callback_data (по умолчанию "sign:")
    """
    builder = InlineKeyboardBuilder()

    for sign in SIGNS:
        emoji = SIGNS_EMOJI[sign]
        builder.button(
            text=f"{emoji} {sign.capitalize()}",
            callback_data=f"{prefix}{sign}"
        )

    builder.adjust(3, 3, 3, 3)
    builder.row(InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_menu"))
    return builder.as_markup()


# ===== КЛАВИАТУРА ПОМОЩИ =====
def help_kb() -> InlineKeyboardMarkup:
    """Создает клавиатуру для раздела помощи"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📞 Связаться с поддержкой",
                    url="https://t.me/bodya_95"
                )
            ],
            [
                InlineKeyboardButton(text="📚 Инструкция", callback_data="help_instructions"),
                InlineKeyboardButton(text="❓ FAQ", callback_data="help_faq")
            ],
            [
                InlineKeyboardButton(text="🔙 На главную", callback_data="menu")
            ]
        ]
    )


# ===== ПРОСТЫЕ КНОПКИ НАВИГАЦИИ =====
def back_to_menu_kb() -> InlineKeyboardMarkup:
    """Создает кнопку для возврата в главное меню"""
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⬅️ В меню", callback_data="menu")]]
    )


def back_kb(callback_data: str = "menu") -> InlineKeyboardMarkup:
    """Создает кнопку 'Назад' с указанным callback_data

    Args:
        callback_data: callback_data для кнопки назад (по умолчанию "menu")
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад", callback_data=callback_data)]]
    )