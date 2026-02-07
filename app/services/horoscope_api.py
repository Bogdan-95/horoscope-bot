import aiohttp
import random
from app.services.translator_service import SimpleTranslator
from app.utils.logger import logger



class HoroscopeAPI:
    BASE_URL = "https://ohmanda.com/api/horoscope"

    def __init__(self):
        self.translator = SimpleTranslator()
        self.signs = {
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

    async def get_daily_horoscope(self, sign_ru: str) -> str:
        logger.info(f"[API] Horoscope request | sign={sign_ru}")

        sign_en = self.signs.get(sign_ru.lower())
        if not sign_en:
            logger.warning(f"[API] Unknown sign: {sign_ru}")
            return "❌ Неизвестный знак зодиака"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                        f"{self.BASE_URL}/{sign_en}/", timeout=5
                ) as response:
                    data = await response.json()
                    raw = data.get("horoscope", "")

                    logger.debug(f"[API] Raw horoscope received")

                    text = await self.translator.translate_text(raw)
                    return self._format(sign_ru, text)

        except aiohttp.ClientError as e:
            logger.error(f"[API] Network error: {e}")
            return self._backup(sign_ru)

        except Exception as e:
            logger.exception(f"[API] Unexpected error: {e}")
            return "⚠️ Сервис гороскопов временно недоступен"

    def _backup(self, sign: str) -> str:
        phrases = [
            "Сегодня важно слушать интуицию.",
            "Хороший день для новых решений.",
            "Звезды советуют не спешить.",
        ]
        return self._format(sign, random.choice(phrases))

    def _format(self, sign: str, text: str) -> str:
        return f"🔮 *{sign.capitalize()}*\n\n{text}"


