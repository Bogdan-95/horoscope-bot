#Главный файл запуска

import asyncio
import os
import logging
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from app.handlers.user import router
from app.database.requests import db_start, get_all_subscribers, update_last_forecast
from app.services.horoscope_api import HoroscopeAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger


async def send_daily_horoscope(bot: Bot):
    """
    Фунция-задача для планировщика.
    Рассылает гороскопы всем активным подписчикам, если контент обновился.
    """
    api = HoroscopeAPI()
    subs = await get_all_subscribers()
    for user_id, sign, last_text in subs:
        new_forecast = await api.get_daily_horoscope(sign)
        # Отправляем только если прогноз новый и качественный
        if new_forecast and new_forecast != last_text:
            try:
                await bot.send_message(
                    user_id,
                    f"☕ *Доброе утро! Твой свежий гороскоп:*\n\n{new_forecast}",
                    parse_mode="Markdown"
                )
                await update_last_forecast(user_id, new_forecast)
                await asyncio.sleep(0.05)  # Плавная отправка, чтобы Telegram не забанил
            except Exception as e:
                logging.error(f"Не удалось отправить сообщение {user_id}: {e}")


async def main():
    """ Точка входа в приложение: запуск БД, планировщика и бота. """
    load_dotenv()
    await db_start()

    bot = Bot(token=os.getenv('BOT_TOKEN'))
    dp = Dispatcher()
    dp.include_router(router)

    # Инициализация планировщика задач
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    # Добавляем задачу на 07:00 по Москве ежедневно
    scheduler.add_job(send_daily_horoscope, CronTrigger(hour=7, minute=0), args=(bot,))
    scheduler.start()

    logging.basicConfig(level=logging.INFO)
    print("Бот версии 2.0 (aiogram 3) успешно запущен!")
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен пользователем")