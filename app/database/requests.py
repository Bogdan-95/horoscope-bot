# /app/database/requests.py База данных (Асинхронная)

import aiosqlite
DB_PATH = 'data/database.db'

async def db_start():
    """ Инициализация базы данных: создание таблицы пользователей, если она не существует."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                tg_id BIGINT PRIMARY KEY,
                username TEXT,
                sign TEXT,
                is_subscribed BOOLEAN DEFAULT 0,
                last_forecast TEXT
            )
        """)
        await db.commit()

async def set_user(tg_id, username):
    """ Регистрация нового пользователя в системе при первом нажатии /start. """
    async with aiosqlite.connect(DB_PATH) as db:
        user = await db.execute("SELECT * FROM users WHERE tg_id = ?", (tg_id,))
        if not await user.fetchone():
            await db.execute("INSERT INTO users (tg_id, username) VALUES (?, ?)", (tg_id, username))
            await db.commit()

async def update_subscription(tg_id, status: bool, sign: str = None):
    """ Обновление статуса подписки и выбранного знака зодиака. """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET is_subscribed = ?, sign = ?, WHERE tg_id = ? ", (status, sign, tg_id))
        await db.commit()

async def get_user_sub(tg_id):
    """ Получение текущих настроек подписки конкретного пользователя. """
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT is_subscribed, sign FROM users WHERE tg_id = ?", (tg_id,)) as cur:
            return await cur.fetchone()

async def get_all_subscribers():
    """ Получение списка всех активных подписчиков для утренней рассылки. """
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT tg_id, sign, last_forecast FROM users WHERE is_subscribed = 1") as cur:
            return await cur.fetchall()

async def update_last_forecast(tg_id, text):
    """ Сохранение текста последнего отправленного гороскопа (защита от дублей). """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET last_forecast = ? WHERE tg_id = ?", (text, tg_id))
        await db.commit()