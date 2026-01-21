""" Главный файл запуска бота """
import asyncio
import os
import sys
from datetime import datetime
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from loguru import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Импорты проекта
import app.database.requests as rq
from app.handlers.user import router as user_router
from app.services.horoscope_api import HoroscopeAPI  # Импортируем наш API

# Настройка логов
logger.remove()
logger.add(sys.stdout,
           format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")

# Инициализируем API глобально
api = HoroscopeAPI()


async def daily_broadcast_task(bot: Bot):
    """ Проверка каждую минуту: рассылка реальных гороскопов """
    now = datetime.now().strftime("%H:%M")
    subscribers = await rq.get_users_by_time(now)

    if subscribers:
        logger.info(f"Рассылка: Найдено {len(subscribers)} подписчиков на {now}")
        for user_id, sign in subscribers:
            try:
                # Получаем реальный гороскоп для рассылки
                horo_text = await api.get_daily_horoscope(sign)

                await bot.send_message(
                    user_id,
                    f"☀️ *Доброе утро!*\n\n{horo_text}\n\nЖелаем вам продуктивного дня!",
                    parse_mode="Markdown"
                )
                logger.success(f"Рассылка отправлена: {user_id} ({sign})")
                await asyncio.sleep(0.05)  # Небольшая пауза, чтобы Telegram не забанил за спам
            except Exception as e:
                logger.error(f"Ошибка рассылки пользователю {user_id}: {e}")


async def main():
    load_dotenv()
    logger.info("Старт бота...")

    await rq.db_start()

    bot = Bot(token=os.getenv('BOT_TOKEN'))
    dp = Dispatcher()

    # Подключаем роутеры
    dp.include_router(user_router)

    # Настройка планировщика
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(
        daily_broadcast_task,
        trigger='cron',
        minute='*',
        args=[bot]
    )
    scheduler.start()
    logger.info("Планировщик запущен (МСК).")

    logger.success("🚀 Бот 2.0 запущен и готов принимать сообщения!")

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f"Ошибка при работе бота: {e}")
    finally:
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("Бот остановлен пользователем")