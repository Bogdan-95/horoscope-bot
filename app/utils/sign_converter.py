# app/utils/sign_converter.py
# Конвертация знаков зодиака между русским и английским

RUS_TO_ENG = {
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
    "рыбы": "pisces"
}

ENG_TO_RUS = {v: k for k, v in RUS_TO_ENG.items()}

def rus_to_eng(sign: str) -> str:
    """Конвертирует русское название знака в английское"""
    return RUS_TO_ENG.get(sign.lower(), sign.lower())

def eng_to_rus(sign: str) -> str:
    """Конвертирует английское название знака в русское"""
    return ENG_TO_RUS.get(sign.lower(), sign.lower())

def normalize_sign(sign: str) -> tuple:
    """Нормализует знак: возвращает (русский, английский)"""
    sign_lower = sign.lower()
    if sign_lower in RUS_TO_ENG:
        return sign_lower, RUS_TO_ENG[sign_lower]
    elif sign_lower in ENG_TO_RUS:
        return ENG_TO_RUS[sign_lower], sign_lower
    return sign_lower, sign_lower