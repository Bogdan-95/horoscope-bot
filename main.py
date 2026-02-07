import asyncio
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand

from app.handlers import routers
from app.utils.logger import logger
from app.services.scheduler_service import SchedulerService

load_dotenv()


async def main():
    logger.info("🚀 Bot starting...")
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise RuntimeError("BOT_TOKEN is not set in environment variables")

    bot = Bot(
        token=bot_token,
        default=DefaultBotProperties(parse_mode="Markdown")
    )

    dp = Dispatcher()

    # Регистрируем все роутеры
    for router in routers:
        dp.include_router(router)

    # Создаём и запускаем планировщик
    scheduler = SchedulerService(bot)

    @dp.startup()
    async def on_startup():
        logger.success("🤖 Bot started successfully")

        # Устанавливаем команды бота с правильным типом
        await bot.set_my_commands([
            BotCommand(command="start", description="Запустить бота"),
            BotCommand(command="help", description="Помощь"),
            BotCommand(command="menu", description="Главное меню"),
            BotCommand(command="subscription", description="Управление рассылкой")
        ])

        # Запускаем планировщик
        await scheduler.start()

    @dp.shutdown()
    async def on_shutdown():
        logger.warning("🛑 Bot shutting down...")
        await scheduler.stop()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())