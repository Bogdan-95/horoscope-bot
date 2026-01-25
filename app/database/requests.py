import aiosqlite
import os
from loguru import logger

DB_PATH = os.path.join('data', 'database.db')

async def db_start():
    if not os.path.exists('data'):
        os.makedirs('data')
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                tg_id BIGINT PRIMARY KEY,
                username TEXT,
                sign TEXT,
                is_subscribed BOOLEAN DEFAULT 0,
                mailing_time TEXT DEFAULT '07:00',
                last_forecast TEXT
            )
        """)
        await db.commit()
    logger.success("Бот 2.0: База данных готова к работе!")

async def set_user(tg_id, username):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT tg_id FROM users WHERE tg_id = ?", (tg_id,)) as cursor:
            if not await cursor.fetchone():
                await db.execute("INSERT INTO users (tg_id, username) VALUES (?, ?)", (tg_id, username))
                await db.commit()
                logger.info(f"БД: Новый пользователь {tg_id} (@{username}) добавлен.")

async def get_users_count() -> int:
    async with aiosqlite.connect("data/database.db") as db:
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        (count,) = await cursor.fetchone()
        return count


async def update_subscription(tg_id, status: bool, sign: str = None, time: str = '07:00'):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE users 
            SET is_subscribed = ?, sign = ?, mailing_time = ? 
            WHERE tg_id = ?
        """, (1 if status else 0, sign, time, tg_id))
        await db.commit()
        logger.info(f"БД: Подписка обновлена для {tg_id}. Статус: {status}, Знак: {sign}, Время: {time}")

async def get_user_info(tg_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE tg_id = ?", (tg_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def get_users_by_time(current_time: str):
    """ Поиск пользователей для рассылки на конкретное время. """
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT tg_id, sign FROM users WHERE is_subscribed = 1 AND mailing_time = ?",
            (current_time,)
        ) as cursor:
            # Возвращаем список кортежей [(id, sign), (id, sign)...]
            return await cursor.fetchall()