# Внешние сервисы (API)

import aiohttp
from datetime import datetime
from .translator_service import SimpleTranslator

class HoroscopeAPI:
    def __init__(self):
        """ Настройка клиента для получения гороскопов и словаря маппинга знаков. """
        self.base_url = "https://ohmanda.com/api/horoscope"
        self.translator = SimpleTranslator()
        self.signs = {
            'овен': 'aries', 'телец': 'taurus', 'близнецы': 'gemini',
            'рак': 'cancer', 'лев': 'leo', 'дева': 'virgo',
            'весы': 'libra', 'скорпион': 'scorpio', 'стрелец': 'sagittarius',
            'козерог': 'capricorn', 'водолей': 'aquarius', 'рыбы': 'pisces'
        }

    async def get_daily_horoscope(self, sign_ru: str):
        """
                Запрашивает гороскоп у API, переводит его на русский язык
                и возвращает отформатированный текст.
                """
        sign_en = self.signs.get(sign_ru.lower())
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.base_url}/{sign_en}/") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        raw_text = data.get('horoscope', '')
                        text_ru = await self.translator.translate_text(raw_text)
                        return self._format(sign_ru, text_ru)
            except Exception:
                return "⚠️ Не удалось связаться со звездами. Попробуйте позже."
        return None

    def _format(self, sign, text):
        """ Придает тексту гороскопа красивый вид с эмодзи. """
        date = datetime.now().strftime("%d.%m")
        return f"🌟 *Гороскоп: {sign.capitalize()}* | {date}\n\n{text}"