# файл с обработчиками команд для администраторов бота
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.services.uptime import get_uptime
from app.database.requests import get_users_count


router = Router()

# ID администраторов бота
ADMIN_IDS = {930734096}

# команда /health - проверка состояния бота
@router.message(Command("health"))
async def health_command(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    users = await get_users_count()

    await message.answer(
        f"🟢 Бот работает\n"
        f"⏱ Аптайм: {get_uptime()}"
        f"📊 Статистика\n"
        f"👥 Пользователей: {users}"
    )