"""
Сервис API гороскопов
======================
Предоставляет доступ к API гороскопов с механизмами резервирования.
Обрабатывает перевод, восстановление ошибок и несколько источников API.

Иерархия источников (по убыванию приоритета):
1. Новый API (astrology-api.io) — требует Bearer-токен (переменная ASTROLOGY_API_KEY).
2. Локальный резерв с детерминированными текстами (28 вариантов на знак, меняются по дате).
3. Крайний резерв — случайные общие фразы (на случай отсутствия локальных данных).
"""

import aiohttp
import os
import random
import asyncio
from typing import Optional, Dict
from datetime import datetime
from dotenv import load_dotenv

from app.services.translator_service import SimpleTranslator
from app.utils.logger import logger
from app.data.local_horoscopes import get_local_horoscope

load_dotenv()


class HoroscopeAPI:
    """
    Сервис для получения ежедневных гороскопов.
    Источники:
    - astrology-api.io (Bearer-токен)
    - Локальный файл с 28 текстами на знак
    - Крайний резерв (общие фразы)
    """

    def __init__(self):
        """
        Инициализация сервиса.
        Загружает API-ключ из переменной окружения ASTROLOGY_API_KEY.
        Создаёт переводчик и подготавливает маппинги знаков.
        """
        self.api_key = os.getenv("ASTROLOGY_API_KEY")
        logger.debug(f"[HoroscopeAPI] __init__: ASTROLOGY_API_KEY = {self.api_key}")
        self.translator = SimpleTranslator()

        # Маппинг русских названий знаков на английские (нижний регистр)
        self.signs: Dict[str, str] = {
            "овен": "aries",
            "телец": "taurus",
            "близнецы": "gemini",
            "рак": "cancer",
            "лев": "leo",
            "дева": "virgo",
            "весы": "libra",
            "скорпион": "scorpio",
            "стрелец": "sagittarius",
            "козерог": "capricorn",
            "водолей": "aquarius",
            "рыбы": "pisces",
        }

        # Английские знаки с заглавной буквы (для astrology-api.io)
        self.signs_capitalized: Dict[str, str] = {
            "овен": "Aries",
            "телец": "Taurus",
            "близнецы": "Gemini",
            "рак": "Cancer",
            "лев": "Leo",
            "дева": "Virgo",
            "весы": "Libra",
            "скорпион": "Scorpio",
            "стрелец": "Sagittarius",
            "козерог": "Capricorn",
            "водолей": "Aquarius",
            "рыбы": "Pisces",
        }

        # Крайние резервные фразы (на случай, если локальный резерв недоступен)
        self.fallback_phrases: list = [
            "Сегодня звезды благоволят к новым начинаниям.",
            "День идеален для планирования будущего.",
            "Слушайте свою интуицию - она не подведет.",
            "Не бойтесь делать первый шаг в важных вопросах.",
            "Сегодняшний день принесет приятные сюрпризы.",
            "Хорошее время для завершения старых дел.",
            "Звезды советуют проявить терпение в общении.",
            "Сегодня вы особенно привлекательны для окружающих.",
            "Уделите время саморазвитию и обучению.",
            "Финансовые вопросы требуют особого внимания.",
        ]

    async def get_daily_horoscope(self, sign_ru: str) -> str:
        """
        Получить ежедневный гороскоп для указанного знака.

        Стратегия:
        1. Пытаемся получить через astrology-api.io.
        2. Если не вышло — берём из локального хранилища (28 текстов на знак).
        3. Если и локального нет — возвращаем случайную общую фразу.

        Args:
            sign_ru: Знак зодиака на русском (например, "козерог")

        Returns:
            Отформатированный текст гороскопа с заголовком.
        """
        logger.info(f"[API] Запрос гороскопа | знак={sign_ru}")

        # Проверка корректности знака
        if sign_ru.lower() not in self.signs:
            logger.warning(f"[API] Неизвестный знак: {sign_ru}")
            return "❌ Неизвестный знак зодиака. Пожалуйста, выберите знак из списка."

        # Уровень 1: Новый API (astrology-api.io)
        horoscope = await self._try_astrology_api(sign_ru)

        # Уровень 2: Локальный резерв (28 текстов на знак)
        if not horoscope:
            horoscope = self._get_local_horoscope(sign_ru)
            if horoscope:
                logger.info("[API] Используется локальный резерв (28 текстов)")
            else:
                # Уровень 3: Крайний резерв (общие фразы)
                horoscope = self._get_fallback_horoscope(sign_ru)
                logger.info("[API] Используется крайний резерв (общие фразы)")

        return horoscope

    async def _try_astrology_api(self, sign_ru: str) -> Optional[str]:
        """
        Пытается получить гороскоп из astrology-api.io (Bearer-токен).

        Документация: https://astrology-api.io
        Требует ключ в переменной окружения ASTROLOGY_API_KEY.

        Args:
            sign_ru: Знак на русском.

        Returns:
            Текст гороскопа или None при ошибке.
        """
        logger.debug(f"[AstrologyAPI] self.api_key = {self.api_key}")
        if not self.api_key:
            logger.warning("[AstrologyAPI] Ключ API не найден, пропускаем")
            return None

        try:
            sign_en = self.signs_capitalized.get(sign_ru.lower())
            if not sign_en:
                return None

            today = datetime.now().strftime("%Y-%m-%d")
            url = "https://api.astrology-api.io/api/v3/horoscope/sign/daily"
            headers = {
                "Content-Type": "application/json",
                "Accept": "*/*",
                "Authorization": f"Bearer {self.api_key}"
            }
            payload = {
                "sign": sign_en,
                "date": today,
                "language": "en",
                "tradition": "universal"
            }

            logger.info(f"[AstrologyAPI] Запрос для {sign_en} на {today}")

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers, timeout=15) as response:
                    if response.status != 200:
                        logger.error(f"[AstrologyAPI] Ошибка {response.status}: {await response.text()}")
                        return None

                    data = await response.json()
                    if not data.get("success"):
                        logger.error("[AstrologyAPI] Ответ с ошибкой")
                        return None

                    result = data.get("data", {})
                    overall_theme = result.get("overall_theme", "")
                    life_areas = result.get("life_areas", [])
                    tips = result.get("tips", [])

                    # Формируем читаемый текст (на английском)
                    lines = []
                    if overall_theme:
                        lines.append(f"✨ *Общая тема:* {overall_theme}\n")

                    # Эмодзи для разных сфер жизни
                    area_emojis = {
                        "love": "❤️ Любовь",
                        "career": "💼 Карьера",
                        "health": "💪 Здоровье",
                        "finance": "💰 Финансы",
                        "relationships": "🤝 Отношения",
                        "creativity": "🎨 Творчество",
                        "spirituality": "🙏 Духовность",
                        "communication": "💬 Общение"
                    }

                    for area in life_areas:
                        area_key = area.get("area")
                        if area_key in area_emojis:
                            prediction = area.get("prediction", "")
                            if prediction:
                                lines.append(f"{area_emojis[area_key]}: {prediction}")

                    # Добавляем совет дня (случайный из списка)
                    if tips:
                        random_tip = random.choice(tips)
                        lines.append(f"\n🌟 *Совет дня:* {random_tip}")

                    if not lines:
                        logger.warning("[AstrologyAPI] Нет данных для формирования текста")
                        return None

                    final_text_en = "\n\n".join(lines)

                    # Переводим на русский
                    translated_text = await self.translator.translate_text(final_text_en)
                    logger.info(f"[AstrologyAPI] Гороскоп успешно получен для {sign_ru}")
                    return self._format_horoscope(sign_ru, translated_text)

        except aiohttp.ClientError as e:
            logger.error(f"[AstrologyAPI] Сетевая ошибка: {e}")
        except asyncio.TimeoutError:
            logger.error("[AstrologyAPI] Таймаут запроса")
        except Exception as e:
            logger.exception(f"[AstrologyAPI] Неожиданная ошибка: {e}")

        return None

    def _get_local_horoscope(self, sign_ru: str) -> Optional[str]:
        """
        Получает гороскоп из локального файла local_horoscopes.py.
        Там для каждого знака подготовлено 28 текстов, выбор идёт по дню года.

        Args:
            sign_ru: Знак на русском.

        Returns:
            Текст гороскопа или None, если данных нет.
        """
        try:
            today = datetime.now()
            text = get_local_horoscope(sign_ru.lower(), for_date=today)
            if text:
                return self._format_horoscope(sign_ru, text)
        except Exception as e:
            logger.error(f"[LocalHoroscope] Ошибка: {e}")
        return None

    def _get_fallback_horoscope(self, sign_ru: str) -> str:
        """
        Крайний резерв — случайная фраза из небольшого списка.
        Используется только если всё остальное не сработало.

        Args:
            sign_ru: Знак на русском.

        Returns:
            Отформатированный гороскоп с одной фразой.
        """
        phrase = random.choice(self.fallback_phrases)
        return self._format_horoscope(sign_ru, phrase)

    @staticmethod
    def _format_horoscope(sign_ru: str, text: str) -> str:
        """
        Форматирует итоговое сообщение с заголовком знака и Markdown-разметкой.

        Args:
            sign_ru: Знак на русском.
            text: Текст гороскопа.

        Returns:
            Строка, готовая для отправки в Telegram.
        """
        sign_formatted = sign_ru.capitalize()
        return f"🔮 *{sign_formatted}*\n\n{text}"