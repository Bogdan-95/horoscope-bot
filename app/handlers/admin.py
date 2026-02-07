# app/handlers/admin.py
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from app.utils.logger import logger

router = Router()

# Только для админов (укажи свой ID)
ADMIN_IDS = [930734096]  # Замени на свой ID


def check_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not check_admin(message.from_user.id):
        await message.answer("⛔ У вас нет прав администратора")
        return

    logger.info(f"[ADMIN_PANEL] {message.from_user.id}")

    await message.answer(
        "👨‍💼 *Панель администратора*\n\n"
        "Доступные команды:\n"
        "/stats - Статистика бота\n"
        "/users - Пользователи\n"
        "/broadcast - Рассылка\n"
        "/logs - Последние логи"
    )