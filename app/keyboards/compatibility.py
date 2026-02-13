# app/keyboards/compatibility.py
# Клавиатуры для совместимости

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Импортируем знаки и эмодзи из главного модуля клавиатур
from .main import SIGNS, SIGNS_EMOJI


# ===== ВЫБОР ЗНАКОВ ДЛЯ СОВМЕСТИМОСТИ =====
def compatibility_signs_kb(step: int = 1, first_sign: str = None) -> InlineKeyboardMarkup:
    """
        Создает динамическую клавиатуру выбора знаков зодиака для совместимости.
    """
    builder = InlineKeyboardBuilder()

    for sign in SIGNS:
        emoji = SIGNS_EMOJI[sign]

        if step == 1:
            callback_data = f"compat_first:{sign}"
        else:
            callback_data = f"compat_second:{first_sign}:{sign}"

        builder.button(
            text=f"{emoji} {sign.capitalize()}",
            callback_data=callback_data
        )

    builder.adjust(3, 3, 3, 3)

    # Кнопки управления
    buttons = []
    if step == 2:
        buttons.append(InlineKeyboardButton(
            text="↩️ Назад к выбору",
            callback_data="compatibility"
        ))

    buttons.append(InlineKeyboardButton(
        text="❌ Отмена",
        callback_data="menu"
    ))

    builder.row(*buttons)
    return builder.as_markup()