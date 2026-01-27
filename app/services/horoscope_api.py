# Сервис для получения гороскопов и совместимости знаков зодиака
import aiohttp
import random
from datetime import datetime
from .translator_service import SimpleTranslator

#==================================================
# ГОРСКОПЫ И СОВМЕСТИМОСТЬ
#==================================================

class HoroscopeAPI:
    def __init__(self):
        self.base_url = "https://ohmanda.com/api/horoscope"
        self.translator = SimpleTranslator()
        self.signs = {
            'овен': 'aries', 'телец': 'taurus', 'близнецы': 'gemini',
            'рак': 'cancer', 'лев': 'leo', 'дева': 'virgo',
            'весы': 'libra', 'скорпион': 'scorpio', 'стрелец': 'sagittarius',
            'козерог': 'capricorn', 'водолей': 'aquarius', 'рыбы': 'pisces'
        }
        # Стихии для расчета совместимости
        self.elements = {
            'овен': 'fire', 'лев': 'fire', 'стрелец': 'fire',
            'телец': 'earth', 'дева': 'earth', 'козерог': 'earth',
            'близнецы': 'air', 'весы': 'air', 'водолей': 'air',
            'рак': 'water', 'скорпион': 'water', 'рыбы': 'water'
        }

    async def get_daily_horoscope(self, sign_ru: str):
        """ Получение гороскопа с резервным каналом """
        sign_en = self.signs.get(sign_ru.lower())

        # 1. Попытка основного API
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/{sign_en}/", timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        raw_text = data.get('horoscope', '')
                        text_ru = await self.translator.translate_text(raw_text)
                        return self._format(sign_ru, text_ru)
        except Exception as e:
            print(f"API Error: {e}")  # Лог ошибки в консоль

        # 2. РЕЗЕРВНЫЙ ВАРИАНТ (Если API упал)
        return self._get_backup_prediction(sign_ru)
    # =================================================
    # СОВМЕСТИМОСТЬ ЗНАКОВ
    # =================================================
    def get_compatibility(self, sign1: str, sign2: str):
        elem1 = self.elements.get(sign1)
        elem2 = self.elements.get(sign2)

        score = random.randint(55, 75)
        description = "Звезды говорят, что многое зависит от ваших усилий."

        combos = {
            ('fire', 'fire'): (
                (80, 95),
                "Две искры превращаются в пламя.\n"
                "Ваш союз полон энергии, страсти и амбиций.\n"
                "Главное — не бороться за лидерство."
            ),
            ('earth', 'earth'): (
                (80, 95),
                "Прочный фундамент и общие ценности.\n"
                "Вы умеете строить долгие и стабильные отношения.\n"
                "Иногда стоит добавить спонтанности."
            ),
            ('air', 'air'): (
                (80, 95),
                "Легкость, разговоры и идеи.\n"
                "Вы вдохновляете друг друга и не терпите скуки.\n"
                "Важно не уходить от реальных чувств."
            ),
            ('water', 'water'): (
                (80, 95),
                "Глубокая эмоциональная связь.\n"
                "Вы чувствуете партнера на интуитивном уровне.\n"
                "Главное — не утонуть в эмоциях."
            ),
            ('fire', 'air'): (
                (75, 90),
                "Огонь и Воздух усиливают друг друга.\n"
                "Яркий союз, полный страсти и идей.\n"
                "Отличная пара для приключений."
            ),
            ('water', 'earth'): (
                (75, 90),
                "Вода питает Землю, помогая ей расти.\n"
                "Надежный союз заботы и стабильности.\n"
                "Хорошая основа для семьи."
            ),
            ('fire', 'water'): (
                (40, 60),
                "Пламя и вода создают пар.\n"
                "Эмоционально, но непросто.\n"
                "Потребуется терпение."
            ),
        }

        key = (elem1, elem2)
        rev_key = (elem2, elem1)

        if sign1 == sign2:
            score = random.randint(85, 100)
            description = (
                "Полное отражение друг друга.\n"
                "Вы понимаете партнера без слов.\n"
                "Идеально при зрелом подходе."
            )
        elif key in combos:
            (min_s, max_s), description = combos[key]
            score = random.randint(min_s, max_s)
        elif rev_key in combos:
            (min_s, max_s), description = combos[rev_key]
            score = random.randint(min_s, max_s)

        return (
            f"❤️ *Совместимость: {sign1.capitalize()} + {sign2.capitalize()}*\n"
            f"📊 *Результат:* {score}%\n\n"
            f"💬 {description}"
        )

    def _get_backup_prediction(self, sign):
        """ Локальный генератор, если интернет подвел """
        phrases = [
            "Звезды советуют сегодня уделить время себе и отдыху.",
            "Отличный день для новых начинаний и смелых идей.",
            "Сегодня ваша интуиция на высоте — доверяйте ей.",
            "Будьте внимательны к знакам судьбы, удача рядом.",
            "Финансовые вопросы сегодня решатся в вашу пользу."
        ]
        text = random.choice(phrases)
        return self._format(sign, f"{text} (Резервный канал связи)")

    def _format(self, sign, text):
        date = datetime.now().strftime("%d.%m")
        return f"🌟 *Гороскоп: {sign.capitalize()}* | {date}\n\n{text}"