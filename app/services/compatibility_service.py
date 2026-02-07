import random
from app.data.compatibility_data import COMPATIBILITY_DATA, PAIR_DESCRIPTIONS
from app.utils.logger import logger
from app.utils.sign_converter import rus_to_eng


class CompatibilityService:
    def calculate(self, sign1: str, sign2: str) -> str:
        logger.info(f"[COMPAT] {sign1} + {sign2}")

        # Конвертируем русские названия в английские
        sign1_eng = rus_to_eng(sign1)
        sign2_eng = rus_to_eng(sign2)

        logger.debug(f"[COMPAT_CONVERT] {sign1}->{sign1_eng}, {sign2}->{sign2_eng}")

        # Ищем данные в двух вариантах (прямой и обратный порядок)
        key1 = (sign1_eng, sign2_eng)
        key2 = (sign2_eng, sign1_eng)

        # Ищем данные совместимости
        compat_data = None

        for key in [key1, key2]:
            if key in COMPATIBILITY_DATA:
                compat_data = COMPATIBILITY_DATA[key]
                logger.debug(f"[COMPAT_FOUND] {key}")
                break

        if not compat_data:
            logger.warning(f"[COMPAT] No data for {sign1_eng} + {sign2_eng}")
            # Если данных нет, создаём фиктивные
            return self._create_fallback_compatibility(sign1, sign2)

        # Ищем описания
        desc_list = None
        for key in [key1, key2]:
            if key in PAIR_DESCRIPTIONS:
                desc_list = PAIR_DESCRIPTIONS[key]
                logger.debug(f"[COMPAT_DESC_FOUND] {key}")
                break

        # Если описаний нет, используем стандартное
        if not desc_list:
            desc_list = [
                f"Интересное сочетание знаков {sign1.capitalize()} и {sign2.capitalize()}.",
                f"Совместимость показывает потенциал для развития отношений.",
                f"Каждый союз уникален - главное взаимопонимание и уважение."
            ]

        desc = random.choice(desc_list)

        # Создаём красивое форматирование
        result = self._format_compatibility(sign1, sign2, compat_data, desc)

        logger.success(f"[COMPAT_OK] {sign1} + {sign2} → {compat_data.get('total', 0)}%")
        return result

    def _create_fallback_compatibility(self, sign1: str, sign2: str) -> str:
        """Создаёт совместимость, если данных нет в БД"""
        # Простая логика на основе первых букв
        base_compat = 50 + (hash(sign1 + sign2) % 30)  # 50-80%

        compat_data = {
            "total": base_compat,
            "love": base_compat + random.randint(-10, 10),
            "understanding": base_compat + random.randint(-15, 15),
            "passion": base_compat + random.randint(-5, 15),
            "communication": base_compat + random.randint(-10, 10)
        }

        # Ограничиваем значения 0-100
        for key in compat_data:
            compat_data[key] = max(0, min(100, compat_data[key]))

        descriptions = [
            f"Интересное сочетание знаков {sign1.capitalize()} и {sign2.capitalize()}.",
            f"Астрологи отмечают потенциал для взаимопонимания.",
            f"Союз может развиваться при взаимных усилиях.",
            f"Разные подходы к жизни могут как притягивать, так и отталкивать.",
            f"Важно научиться понимать и принимать различия."
        ]

        desc = random.choice(descriptions)

        return self._format_compatibility(sign1, sign2, compat_data, desc)

    def _format_compatibility(self, sign1: str, sign2: str,
                              compat_data: dict, description: str) -> str:
        """Форматирует результат совместимости"""

        total = compat_data.get('total', 0)

        # Создаём красивую графику с эмодзи
        progress_bar = self._create_progress_bar(total)

        result = (
            f"❤️ *СОВМЕСТИМОСТЬ ЗНАКОВ*\n\n"
            f"✨ *{sign1.upper()} + {sign2.upper()}*\n\n"
            f"📊 *Общая совместимость:* {total}%\n"
            f"{progress_bar}\n"
        )

        # Добавляем детали
        if 'love' in compat_data:
            love_bar = self._create_small_bar(compat_data['love'])
            result += f"💖 Любовь: {compat_data['love']}% {love_bar}\n"

        if 'understanding' in compat_data:
            under_bar = self._create_small_bar(compat_data['understanding'])
            result += f"🧠 Понимание: {compat_data['understanding']}% {under_bar}\n"

        if 'passion' in compat_data:
            passion_bar = self._create_small_bar(compat_data['passion'])
            result += f"🔥 Страсть: {compat_data['passion']}% {passion_bar}\n"

        if 'communication' in compat_data:
            comm_bar = self._create_small_bar(compat_data['communication'])
            result += f"🗣 Общение: {compat_data['communication']}% {comm_bar}\n"

        # Добавляем разделитель
        result += "\n" + "─" * 30 + "\n\n"

        # Описание
        result += f"💭 *Астрологический анализ:*\n{description}\n\n"

        # Добавляем рекомендации
        result += self._get_recommendation(total)

        return result

    @staticmethod
    def _create_progress_bar(percentage: int, length: int = 10) -> str:
        """Создаёт прогресс-бар"""
        filled = round(percentage / 100 * length)
        empty = length - filled

        # Выбираем эмодзи в зависимости от процента
        if percentage >= 80:
            filled_char = "🟢"
        elif percentage >= 60:
            filled_char = "🟡"
        elif percentage >= 40:
            filled_char = "🟠"
        else:
            filled_char = "🔴"

        empty_char = "⚫"

        return filled_char * filled + empty_char * empty

    @staticmethod
    def _create_small_bar(percentage: int, length: int = 5) -> str:
        """Создаёт маленький прогресс-бар"""
        filled = round(percentage / 100 * length)
        empty = length - filled
        return "█" * filled + "░" * empty

    @staticmethod
    def _get_recommendation(total: int) -> str:
        """Возвращает рекомендацию на основе процента совместимости"""
        if total >= 85:
            return "🎉 *ИДЕАЛЬНАЯ СОВМЕСТИМОСТЬ!* Отличный потенциал для гармоничных отношений!"
        elif total >= 70:
            return "✅ *ХОРОШАЯ СОВМЕСТИМОСТЬ.* При взаимных усилиях отношения будут успешными."
        elif total >= 55:
            return "⚠️ *СРЕДНЯЯ СОВМЕСТИМОСТЬ.* Потребуется работа над взаимопониманием."
        elif total >= 40:
            return "💡 *СЛОЖНАЯ СОВМЕСТИМОСТЬ.* Возможны конфликты, но всё зависит от вас."
        else:
            return "🔴 *НИЗКАЯ СОВМЕСТИМОСТЬ.* Потребуется много терпения и компромиссов."