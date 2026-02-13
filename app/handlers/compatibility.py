# app/handlers/compatibility.py
# Обработчики для совместимости знаков зодиака в Telegram боте

from aiogram import Router, F
from aiogram.types import CallbackQuery
from app.utils.logger import logger
from app.services.compatibility_service import CompatibilityService
from app.keyboards.compatibility import compatibility_signs_kb
from app.keyboards.main import back_to_menu_kb

router = Router()

# Глобальный экземпляр сервиса совместимости (создается один раз)
compat_service = CompatibilityService()


def u(user) -> str:
    """Форматирует информацию о пользователе для логов"""
    if not user:
        return "Unknown"
    name = user.first_name or user.username or "NoName"
    return f"{name} ({user.id})"


# ===================== COMPATIBILITY =====================

@router.callback_query(F.data == "compatibility")
async def compatibility_start(callback: CallbackQuery):
    """
    Стартовая обработка совместимости знаков зодиака.
    """
    logger.info(f"[COMPAT_START] {u(callback.from_user)}")

    await callback.message.edit_text(
        "💞 *Совместимость знаков зодиака*\n\n"
        "✨ *Выберите первый знак:*",
        reply_markup=compatibility_signs_kb(step=1) # Клавиатура всех знаков
    )
    await callback.answer()


@router.callback_query(F.data.startswith("compat_first:"))
async def compatibility_first_sign(callback: CallbackQuery):
    """
        Обработка выбора ПЕРВОГО знака зодиака.
    """
    sign1 = callback.data.split(":")[1]
    logger.info(f"[COMPAT_FIRST] {u(callback.from_user)} → {sign1}")

    await callback.message.edit_text(
        f"✅ *Первый знак:* {sign1.capitalize()}\n\n"
        "✨ *Теперь выберите второй знак:*",
        reply_markup=compatibility_signs_kb(step=2, first_sign=sign1)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("compat_second:"))
async def compatibility_calculate(callback: CallbackQuery):
    """
        Финальный расчет и отображение совместимости двух знаков.
    """
    _, sign1, sign2 = callback.data.split(":")
    logger.info(f"[COMPAT_CALC] {u(callback.from_user)} → {sign1} + {sign2}")

    try:
        result = compat_service.calculate(sign1, sign2)
        await callback.message.edit_text(
            result,
            reply_markup=back_to_menu_kb()
        )
        logger.success(f"[COMPAT_DONE] {u(callback.from_user)}")
    except Exception as e:
        logger.exception(f"[COMPAT_ERROR] {u(callback.from_user)} | {e}")
        await callback.message.edit_text(
            "⚠️ *Ошибка при расчёте совместимости*\n\n"
            "Попробуйте позже или выберите другие знаки.",
            reply_markup=back_to_menu_kb()
        )

    await callback.answer() # Закрываем индикатор загрузки