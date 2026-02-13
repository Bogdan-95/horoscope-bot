# app/database/init_db.py
# Инициализация базы данных с правильной структурой таблиц для Telegram бота гороскопов

import sqlite3
import os
from pathlib import Path
from typing import List
from app.utils.logger import logger

# Путь к файлу базы данных в папке data
DB_PATH: Path = Path(__file__).resolve().parents[1] / "data" / "database.db"


def recreate_database() -> None:
    """
    Пересоздает базу данных с правильной структурой таблиц.

    Выполняет:
    1. Удаление существующей базы данных (если есть)
    2. Создание новых таблиц users и subscriptions
    3. Проверку созданной структуры

    Предназначена для инициализации или сброса БД при разработке.
    """
    try:
        # Удаляем старую базу данных, если она существует
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
            logger.info("[DB] Существующая база данных удалена")

        # Создаем новое подключение и курсор
        conn: sqlite3.Connection = sqlite3.connect(DB_PATH)
        cursor: sqlite3.Cursor = conn.cursor()

        # 1. Таблица пользователей
        # Хранит информацию о пользователях бота
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                sign TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 2. Таблица подписок
        # Хранит, настройки рассылки гороскопов для пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                user_id INTEGER PRIMARY KEY,
                is_subscribed INTEGER DEFAULT 0,
                notification_time TEXT DEFAULT '09:00',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # Фиксируем изменения и закрываем соединение
        conn.commit()
        conn.close()

        logger.success("[DB] База данных успешно пересоздана")

        # Проверяем структуру созданных таблиц
        check_database_structure()

    except Exception as e:
        logger.error(f"[DB_ERROR] Ошибка пересоздания базы данных: {e}")
        raise


def check_database_structure() -> None:
    """
    Проверяет структуру таблиц в базе данных.

    Выводит в лог список колонок для таблиц users и subscriptions
    для подтверждения корректного создания.
    """
    try:
        conn: sqlite3.Connection = sqlite3.connect(DB_PATH)
        cursor: sqlite3.Cursor = conn.cursor()

        # Проверяем структуру таблицы users
        cursor.execute("PRAGMA table_info(users)")
        users_columns: List[tuple] = cursor.fetchall()
        logger.info(f"[DB] Колонки таблицы users: {[col[1] for col in users_columns]}")

        # Проверяем структуру таблицы subscriptions
        cursor.execute("PRAGMA table_info(subscriptions)")
        subs_columns: List[tuple] = cursor.fetchall()
        logger.info(f"[DB] Колонки таблицы subscriptions: {[col[1] for col in subs_columns]}")

        conn.close()

    except Exception as e:
        logger.error(f"[DB_ERROR] Ошибка проверки структуры БД: {e}")


def migrate_old_data() -> None:
    """
    Миграция данных из старой структуры базы данных.

    Проверяет наличие старого файла database_old.db и логирует необходимость миграции.
    Логика миграции может быть дополнена при необходимости.
    """
    try:
        # Путь к старой базе данных
        old_db_path: Path = Path(__file__).resolve().parents[1] / "data" / "database_old.db"

        if os.path.exists(old_db_path):
            logger.info("[DB] Найдена старая база данных, может потребоваться миграция")
            # Здесь можно добавить логику миграции данных
        else:
            logger.debug("[DB] Старая база данных не найдена")

    except Exception as e:
        logger.error(f"[DB_ERROR] Ошибка миграции старых данных: {e}")


if __name__ == "__main__":
    """
    Точка входа для пересоздания базы данных.
    Выполняется при прямом запуске файла: python init_db.py
    """
    recreate_database()
