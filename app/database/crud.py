# app/database/crud.py
# CRUD операции для базы данных

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
from app.utils.logger import logger


DB_PATH = Path(__file__).resolve().parents[1] / "data" / "database.db"


def get_connection():
    """Создает соединение с базой данных"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Инициализация базы данных """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Таблица пользователей
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

        # Таблица подписок
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                user_id INTEGER PRIMARY KEY,
                is_subscribed INTEGER DEFAULT 0,
                notification_time TEXT DEFAULT '09:00',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()
        logger.success("[DB] Database initialized successfully")

    except Exception as e:
        logger.error(f"[DB_ERROR] init_database: {e}")


# ===================== USERS =====================

def get_user(user_id: int) -> Optional[Dict]:
    """Получает пользователя по ID """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user_row = cursor.fetchone()

        if user_row:
            user = dict(user_row)

            # Получаем подписку отдельно
            cursor.execute('SELECT * FROM subscriptions WHERE user_id = ?', (user_id,))
            sub_row = cursor.fetchone()
            if sub_row:
                user.update({
                    'is_subscribed': sub_row['is_subscribed'],
                    'notification_time': sub_row['notification_time']
                })

            conn.close()
            return user

        conn.close()
        return None

    except Exception as e:
        logger.error(f"[DB_ERROR] get_user: {e}")
        return None


def create_user(user_id: int, username: Optional[str], first_name: Optional[str]) -> None:
    """Создает нового пользователя """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # вставляем без проверки
        cursor.execute(
            'INSERT OR REPLACE INTO users (id, username, first_name) VALUES (?, ?, ?)',
            (user_id, username, first_name)
        )

        # Проверяем, есть ли уже подписка
        cursor.execute('SELECT user_id FROM subscriptions WHERE user_id = ?', (user_id,))
        if not cursor.fetchone():
            cursor.execute(
                'INSERT INTO subscriptions (user_id) VALUES (?)',
                (user_id,)
            )

        conn.commit()
        conn.close()

        logger.info(f"[DB] User created/updated: {user_id}")

    except Exception as e:
        logger.error(f"[DB_ERROR] create_user: {e}")


def update_user_sign(user_id: int, sign: str) -> None:
    """Обновляет знак зодиака пользователя"""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            'UPDATE users SET sign = ? WHERE id = ?',
            (sign.lower(), user_id)
        )
        conn.commit()
        conn.close()

        logger.info(f"[DB] Sign updated: {user_id} -> {sign}")

    except Exception as e:
        logger.error(f"[DB_ERROR] update_user_sign: {e}")


# ===================== SUBSCRIPTIONS =====================

def get_subscription(user_id: int) -> Optional[Dict]:
    """Получает подписку пользователя """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT s.*, u.sign 
            FROM subscriptions s
            JOIN users u ON s.user_id = u.id
            WHERE s.user_id = ?
        ''', (user_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    except Exception as e:
        logger.error(f"[DB_ERROR] get_subscription: {e}")
        return None


def update_subscription(user_id: int, is_subscribed: bool = None,
                        notification_time: str = None) -> None:
    """Обновляет подписку пользователя"""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        updates = []
        params = []

        if is_subscribed is not None:
            updates.append("is_subscribed = ?")
            params.append(1 if is_subscribed else 0)

        if notification_time:
            updates.append("notification_time = ?")
            params.append(notification_time)

        if updates:
            updates.append("updated_at = ?")
            params.append(datetime.now().isoformat())

            params.append(user_id)

            query = f'''
                UPDATE subscriptions 
                SET {', '.join(updates)}
                WHERE user_id = ?
            '''
            cursor.execute(query, params)
            conn.commit()
            logger.info(f"[DB] Subscription updated: {user_id}")

        conn.close()

    except Exception as e:
        logger.error(f"[DB_ERROR] update_subscription: {e}")


def get_subscribed_users_for_time(target_time: str) -> List[Dict]:
    """Получает пользователей с активной подпиской на указанное время """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT u.id as user_id, u.username, u.first_name, u.sign, s.notification_time
            FROM users u
            JOIN subscriptions s ON u.id = s.user_id
            WHERE s.is_subscribed = 1 
            AND u.sign IS NOT NULL
            AND u.sign != ''
            AND s.notification_time = ?
        ''', (target_time,))

        rows = cursor.fetchall()
        conn.close()

        result = []
        for row in rows:
            result.append({
                "id": row['user_id'],  # Используем правильное имя столбца
                "username": row['username'],
                "first_name": row['first_name'],
                "sign": row['sign'],
                "notification_time": row['notification_time']
            })

        return result

    except Exception as e:
        logger.error(f"[DB_ERROR] get_subscribed_users_for_time: {e}")
        return []


# Инициализируем базу данных при импорте
init_database()