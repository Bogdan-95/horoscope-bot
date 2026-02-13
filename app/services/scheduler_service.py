# app/services/scheduler_service.py
# Сервис планировщика задач для автоматической рассылки гороскопов и бэкапов БД

import asyncio
from datetime import datetime, time
from aiogram import Bot
from app.database.crud import get_subscribed_users_for_time
from app.services.horoscope_api import HoroscopeAPI
from app.services.backup_service import BackupService
from app.utils.logger import logger
from app.utils.message_formatter import format_horoscope_message
from app.services.health import update_health

class SchedulerService:
    """
        Сервис планировщика фоновых задач для Telegram бота гороскопов.

        Отвечает за:
        - Ежедневную рассылку гороскопов подписчикам по расписанию
        - Автоматическое создание бэкапов базы данных
        - Управление жизненным циклом фоновых задач
        """
    def __init__(self, bot: Bot):
        """
            Инициализация планировщика.

            Args:
                bot (Bot): Экземпляр Telegram бота для отправки сообщений
        """

        self.bot = bot
        self.horoscope_api = HoroscopeAPI()
        self.is_running = False

        # Инициализируем сервис бэкапов
        self.backup_service = BackupService(
            db_path="app/data/database.db",
            backup_dir="app/data/backups",
            max_backups=10
        )

    async def start(self):
        """
                Запуск планировщика фоновых задач.

                Создает:
                - Бэкап БД при старте
                - Цикл рассылки гороскопов (каждую минуту проверяет)
                - Цикл ежедневных бэкапов (03:00)
                """
        self.is_running = True
        logger.info("⏰ Scheduler started")

        # Создаём бэкап при старте
        await self._create_backup()

        # Запускаем фоновые циклы в отдельных задачах
        asyncio.create_task(self._notification_loop())
        asyncio.create_task(self._daily_backup_loop())
        asyncio.create_task(self._health_update_loop())

    async def stop(self):
        """Остановка планировщика"""
        if self.is_running:
            self.is_running = False
            logger.info("⏰ Scheduler stopped")

    async def _create_backup(self):
        """Создание бэкапа базы данных"""
        try:
            backup_path = self.backup_service.create_backup()
            if backup_path:
                count = self.backup_service.get_backup_count()
                logger.info(f"📦 Бэкап создан. Всего бэкапов: {count}")
        except Exception as e:
            logger.error(f"Ошибка при создании бэкапа: {e}")

    async def _daily_backup_loop(self):
        """
                Цикл ежедневных бэкапов в 03:00 утра.

                Проверяет время каждую минуту и создает бэкап при совпадении.
                """
        while self.is_running:
            try:
                now = datetime.now()

                # Если 03:00 утра
                if now.hour == 3 and now.minute == 0:
                    await self._create_backup()
                    # Ждём час, чтобы не создавать много бэкапов
                    await asyncio.sleep(3600)
                else:
                    await asyncio.sleep(60)  # Проверяем каждую минуту

            except Exception as e:
                logger.error(f"Ошибка в daily_backup_loop: {e}")
                await asyncio.sleep(60)

    async def _notification_loop(self):
        """
                Основной цикл рассылки гороскопов.

                Каждую минуту проверяет подписчиков и отправляет гороскопы по времени уведомлений.
                """

        while self.is_running:
            try:
                now = datetime.now()
                current_time = now.strftime("%H:%M")

                # Получаем пользователей для текущего времени
                users = get_subscribed_users_for_time(current_time)

                if users:
                    logger.info(f"⏰ Отправка уведомлений для {len(users)} пользователей в {current_time}")
                    await self._send_horoscopes(users, current_time)

                # Ждём 1 минуту перед следующей проверкой
                await asyncio.sleep(60)

            except Exception as e:
                logger.error(f"⏰ Ошибка в notification_loop: {e}")
                await asyncio.sleep(60)

    async def _send_horoscopes(self, users: list, current_time: str):
        """Отправляет гороскопы пользователям"""
        for user in users:
            try:
                user_id = user["id"]
                sign = user.get("sign")
                first_name = user.get("first_name", "друг")

                if sign:
                    # Получаем гороскоп
                    horoscope_text = await self.horoscope_api.get_daily_horoscope(sign)

                    # Форматируем красивое сообщение
                    message = format_horoscope_message(first_name, sign, horoscope_text, current_time)

                    # Отправляем сообщение
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=message
                    )

                    logger.info(f"⏰ Гороскоп отправлен {user_id} ({sign})")

                    # Небольшая пауза между отправками
                    await asyncio.sleep(0.3)

            except Exception as e:
                logger.error(f"⏰ Ошибка отправки пользователю {user.get('id')}: {e}")

    async def _health_update_loop(self):
        """
        Цикл обновления health.txt каждые 30 секунд.
        """
        while self.is_running:
            try:
                update_health()
                await asyncio.sleep(30)
            except Exception as e:
                logger.error(f"Ошибка в health_update_loop: {e}")
                await asyncio.sleep(30)