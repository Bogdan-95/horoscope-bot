# app/database/init_db.py
# Инициализация базы данных с правильной структурой

import sqlite3
import os
from pathlib import Path
from app.utils.logger import logger

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "database.db"


def recreate_database():
    """Пересоздает базу данных с правильной структурой"""
    try:
        # Удаляем старую базу если существует
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
            logger.info("[DB] Old database removed")

        # Создаем новую базу
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 1. Таблица users с правильными столбцами
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

        # 2. Таблица subscriptions
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

        conn.commit()
        conn.close()

        logger.success("[DB] Database recreated successfully")

        # Проверяем структуру
        check_database_structure()

    except Exception as e:
        logger.error(f"[DB_ERROR] recreate_database: {e}")


def check_database_structure():
    """Проверяет структуру базы данных"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Проверяем таблицу users
        cursor.execute("PRAGMA table_info(users)")
        users_columns = cursor.fetchall()
        logger.info(f"[DB] Users table columns: {[col[1] for col in users_columns]}")

        # Проверяем таблицу subscriptions
        cursor.execute("PRAGMA table_info(subscriptions)")
        subs_columns = cursor.fetchall()
        logger.info(f"[DB] Subscriptions table columns: {[col[1] for col in subs_columns]}")

        conn.close()

    except Exception as e:
        logger.error(f"[DB_ERROR] check_database_structure: {e}")


def migrate_old_data():
    """Миграция данных из старой структуры"""
    try:
        old_db_path = Path(__file__).resolve().parents[1] / "data" / "database_old.db"

        if os.path.exists(old_db_path):
            # Здесь можно добавить логику миграции
            logger.info("[DB] Old database found, migration might be needed")

    except Exception as e:
        logger.error(f"[DB_ERROR] migrate_old_data: {e}")


if __name__ == "__main__":
    recreate_database()