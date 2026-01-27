import aiosqlite
import os
from loguru import logger

# =========================
# НАСТРОЙКИ БАЗЫ ДАННЫХ
# =========================

DB_PATH = os.path.join('data', 'database.db')


# =========================
# ИНИЦИАЛИЗАЦИЯ БД
# =========================

async def db_start():
    """
    Создание папки data и таблицы users при первом запуске.
    """
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


# =========================
# ПОЛЬЗОВАТЕЛИ
# =========================

async def set_user(tg_id: int, username: str):
    """
    Добавляет пользователя в БД, если его ещё нет.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT tg_id FROM users WHERE tg_id = ?",
            (tg_id,)
        ) as cursor:
            if not await cursor.fetchone():
                await db.execute(
                    "INSERT INTO users (tg_id, username) VALUES (?, ?)",
                    (tg_id, username)
                )
                await db.commit()
                logger.info(f"БД: Новый пользователь {tg_id} (@{username}) добавлен.")


async def get_user_info(tg_id: int) -> dict | None:
    """
    Возвращает данные пользователя в виде dict или None.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE tg_id = ?",
            (tg_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def get_users_count() -> int:
    """
    Возвращает количество пользователей в БД.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        (count,) = await cursor.fetchone()
        return count


# =========================
# ПОДПИСКА (ВАЖНЫЙ БЛОК)
# =========================

async def subscribe_user(tg_id: int, sign: str, time: str):
    """
    Включает подписку пользователю.
    Обновляет знак и время.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE users
            SET is_subscribed = 1,
                sign = ?,
                mailing_time = ?
            WHERE tg_id = ?
        """, (sign, time, tg_id))
        await db.commit()

    logger.info(f"БД: Подписка ВКЛ для {tg_id} | {sign} | {time}")


async def unsubscribe_user(tg_id: int):
    """
    Отключает подписку.
    ВАЖНО: знак и время НЕ стираются.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE users
            SET is_subscribed = 0
            WHERE tg_id = ?
        """, (tg_id,))
        await db.commit()

    logger.info(f"БД: Подписка ВЫКЛ для {tg_id}")


async def get_users_by_time(current_time: str):
    """
    Возвращает список пользователей,
    которым нужно отправить рассылку в текущее время.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT tg_id, sign
            FROM users
            WHERE is_subscribed = 1
              AND mailing_time = ?
        """, (current_time,)) as cursor:
            return await cursor.fetchall()
