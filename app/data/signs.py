"""
Единый справочник знаков зодиака.

Используется:
- для UI (эмодзи, русский язык)
- для API (английские идентификаторы)
- для совместимости (стихии)

❗ Это единственный источник данных о знаках
"""

from typing import Dict


SIGNS: Dict[str, dict] = {
    "aries": {
        "ru": "овен",
        "emoji": "♈",
        "element": "fire",
    },
    "taurus": {
        "ru": "телец",
        "emoji": "♉",
        "element": "earth",
    },
    "gemini": {
        "ru": "близнецы",
        "emoji": "♊",
        "element": "air",
    },
    "cancer": {
        "ru": "рак",
        "emoji": "♋",
        "element": "water",
    },
    "leo": {
        "ru": "лев",
        "emoji": "♌",
        "element": "fire",
    },
    "virgo": {
        "ru": "дева",
        "emoji": "♍",
        "element": "earth",
    },
    "libra": {
        "ru": "весы",
        "emoji": "♎",
        "element": "air",
    },
    "scorpio": {
        "ru": "скорпион",
        "emoji": "♏",
        "element": "water",
    },
    "sagittarius": {
        "ru": "стрелец",
        "emoji": "♐",
        "element": "fire",
    },
    "capricorn": {
        "ru": "козерог",
        "emoji": "♑",
        "element": "earth",
    },
    "aquarius": {
        "ru": "водолей",
        "emoji": "♒",
        "element": "air",
    },
    "pisces": {
        "ru": "рыбы",
        "emoji": "♓",
        "element": "water",
    },
}


def get_sign_by_ru(name_ru: str) -> str | None:
    """
    Возвращает английский ключ знака по русскому названию
    """
    name_ru = name_ru.lower()
    for key, data in SIGNS.items():
        if data["ru"] == name_ru:
            return key
    return None


def get_sign_data(sign_en: str) -> dict:
    """
    Безопасное получение данных знака
    """
    return SIGNS.get(sign_en)

