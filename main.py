"""
Точка входа в Telegram-бота для гороскопов
============================================
Инициализирует и запускает Telegram бота со всеми обработчиками и сервисами.
Возможности: ежедневные гороскопы, совместимость знаков зодиака, система подписки.
"""

import asyncio
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand

from app.handlers import routers  # Список всех роутеров (обработчиков сообщений)
from app.services.health import update_health
from app.utils.logger import logger  # Кастомный логгер с цветным выводом
from app.services.scheduler_service import SchedulerService  # Сервис планировщика задач

# Загружаем переменные окружения из файла .env
load_dotenv()

print(f"DEBUG: BOT_TOKEN exists: {'✅' if os.getenv('BOT_TOKEN') else '❌'}")
print(f"DEBUG: ASTROLOGY_API_KEY exists: {'✅' if os.getenv('ASTROLOGY_API_KEY') else '❌'}")

async def main() -> None:
    """
    Главная асинхронная функция для запуска Telegram бота.

    Инициализирует:
    - Бота с токеном Telegram
    - Диспетчер для обработки сообщений
    - Все роутеры (обработчики)
    - Планировщик для уведомлений по расписанию
    """
    logger.info("🚀 Бот запускается...")

    # Получаем токен бота из переменных окружения
    bot_token: str = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise RuntimeError("Переменная BOT_TOKEN не установлена в окружении")

    # Проверяем наличие API ключа (опционально, для резервного API)
    api_key: str | None = os.getenv("ASTROLOGY_API_KEY")
    if api_key:
        logger.info(f"📡 API ключ загружен: {api_key[:10]}...")
    else:
        logger.warning("⚠️  API ключ не найден - используется только бесплатное API")

    # Инициализируем бота с Markdown как режимом разметки по умолчанию
    bot: Bot = Bot(
        token=bot_token,
        default=DefaultBotProperties(parse_mode="Markdown")
    )

    # Инициализируем диспетчер для обработки событий
    dp: Dispatcher = Dispatcher()

    # Подключаем все роутеры (группы обработчиков сообщений)
    for router in routers:
        dp.include_router(router)

    # Инициализируем планировщик для уведомлений по расписанию
    scheduler: SchedulerService = SchedulerService(bot)

    @dp.startup()
    async def on_startup() -> None:
        """
        Обработчик запуска - выполняется при старте бота.

        Выполняет:
        - Устанавливает команды бота для меню Telegram
        - Запускает планировщик ежедневных уведомлений
        - Логирует успешный запуск
        """
        logger.success("🤖 Бот успешно запущен")

        # Устанавливаем команды бота для меню Telegram (/help, /start и т.д.)
        await bot.set_my_commands([
            BotCommand(command="start", description="Запустить бота"),
            BotCommand(command="help", description="Помощь"),
            BotCommand(command="menu", description="Главное меню"),
            BotCommand(command="subscription", description="Управление рассылкой")
        ])

        # Запускаем планировщик ежедневных гороскопов
        await scheduler.start()

        # Создаем health.txt при старте.
        update_health()
        logger.info("✅ Health file created")

    @dp.shutdown()
    async def on_shutdown() -> None:
        """
        Обработчик остановки - выполняется при выключении бота.

        Выполняет:
        - Корректно останавливает планировщик
        - Логирует событие остановки
        """
        logger.warning("🛑 Бот останавливается...")
        await scheduler.stop()

    # Запускаем polling для получения обновлений от Telegram
    await dp.start_polling(bot)


if __name__ == "__main__":
    # Запускаем главную асинхронную функцию
    asyncio.run(main())
