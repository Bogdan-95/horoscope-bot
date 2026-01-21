import aiohttp
import random
from datetime import datetime
from .translator_service import SimpleTranslator


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

    def get_compatibility(self, sign1: str, sign2: str):
        """ Расчет совместимости """
        elem1 = self.elements.get(sign1)
        elem2 = self.elements.get(sign2)

        # Базовая логика совместимости стихий
        score = random.randint(50, 80)  # Случайная база

        if sign1 == sign2:
            score = random.randint(85, 100)
            text = "Идеальное зеркало! Вы понимаете друг друга без слов."
        elif elem1 == elem2:
            score = random.randint(80, 95)
            text = "Одна стихия! Ваш союз полон гармонии и поддержки."
        elif (elem1 == 'fire' and elem2 == 'air') or (elem1 == 'air' and elem2 == 'fire'):
            score = random.randint(75, 90)
            text = "Огонь и Воздух раздувают страсть! Яркая пара."
        elif (elem1 == 'water' and elem2 == 'earth') or (elem1 == 'earth' and elem2 == 'water'):
            score = random.randint(75, 90)
            text = "Вода питает Землю. Надежный и плодотворный союз."
        elif (elem1 == 'fire' and elem2 == 'water') or (elem1 == 'water' and elem2 == 'fire'):
            score = random.randint(40, 60)
            text = "Пар и пламя. Сложно, но очень эмоционально."
        else:
            text = "Звезды говорят, что все зависит от вас! Противоположности притягиваются."

        return (
            f"❤️ *Совместимость: {sign1.capitalize()} + {sign2.capitalize()}*\n"
            f"📊 *Результат:* {score}%\n\n"
            f"💬 {text}"
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