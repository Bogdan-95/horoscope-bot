# Клавиатуры бота
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Главная клавиатура под сообщением
def main_menu():
    """ Главное меню (кнопки под сообщением) """
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔮 Узнать гороскоп", callback_data="get_horo"))
    builder.row(InlineKeyboardButton(text="❤️ Совместимость", callback_data="compat_start"))
    builder.row(InlineKeyboardButton(text="🔔 Настройка рассылки", callback_data="sub_manage"))
    builder.row(InlineKeyboardButton(text="🆘 Помощь", callback_data="help_guide"))
    builder.adjust(1)  # Кнопки в один столбик для красоты
    return builder.as_markup()


def back_to_main_kb():
    """ Кнопка возврата """
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 В главное меню", callback_data="to_main"))
    return builder.as_markup()


def signs_kb(prefix="show_sign_"):
    """ Список знаков. prefix меняет поведение (гороскоп или подписка) """
    signs = ['Овен', 'Телец', 'Близнецы', 'Рак', 'Лев', 'Дева',
             'Весы', 'Скорпион', 'Стрелец', 'Козерог', 'Водолей', 'Рыбы']
    builder = InlineKeyboardBuilder()

    for s in signs:
        builder.add(InlineKeyboardButton(text=s, callback_data=f"{prefix}{s.lower()}"))

    builder.adjust(3)
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="to_main"))
    return builder.as_markup()


def compat_signs_kb(step="first", sign1=None):
    """ Клавиатура для выбора знаков в совместимости """
    signs = ['Овен', 'Телец', 'Близнецы', 'Рак', 'Лев', 'Дева',
             'Весы', 'Скорпион', 'Стрелец', 'Козерог', 'Водолей', 'Рыбы']
    builder = InlineKeyboardBuilder()

    for s in signs:
        if step == "first":
            # Выбираем первый знак
            callback = f"compat_1_{s.lower()}"
        else:
            # Выбираем второй знак (передаем первый в callback)
            callback = f"compat_calc_{sign1}_{s.lower()}"

        builder.add(InlineKeyboardButton(text=s, callback_data=callback))

    builder.adjust(3)
    builder.row(InlineKeyboardButton(text="🔙 Отмена", callback_data="to_main"))
    return builder.as_markup()


def unsubscribe_kb():
    """ Если уже подписан """
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="❌ Отписаться", callback_data="unsub"))
    builder.row(InlineKeyboardButton(text="🔙 В главное меню", callback_data="to_main"))
    return builder.as_markup()


def reply_main_menu():
    """ Нижняя клавиатура """
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✨ Главное меню")]
        ],
        resize_keyboard=True
    )


def time_kb(sign: str):
    """ Выбор времени с шагом 30 минут """
    builder = InlineKeyboardBuilder()
    # Генерируем список: 06:00, 06:30 ... 11:00
    times = []
    for h in range(6, 12):  # 6 to 11
        times.append(f"{h:02d}:00")
        if h != 11:  # Добавляем половинки для всех кроме последнего, если нужно до 11:00 ровно
            times.append(f"{h:02d}:30")

    for t in times:
        builder.add(InlineKeyboardButton(text=t, callback_data=f"set_time_{t}_{sign}"))

    builder.adjust(4)  # По 4 времени в ряд
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="sub_manage"))
    return builder.as_markup()