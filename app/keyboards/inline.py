# Все меню и кнопки

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu():
    """ Главное меню бота с основными функциями. """
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔮 Узнать гороскоп", callback_data="get_horo"))
    builder.row(InlineKeyboardButton(text="🔔 Настройка рассылки", callback_data="sub_manage"))
    builder.row(InlineKeyboardButton(text="🆘 Помощь", callback_data="help"))
    return builder.as_markup()

def signs_kb(is_sub=False):
    """ Динамическая клавиатура со списком всех знаков зодиака. """
    signs = ['Овен', 'Телец', 'Близнецы', 'Рак', 'Лев', 'Дева',
             'Весы', 'Скорпион', 'Стрелец', 'Козерог', 'Водолей', 'Рыбы']
    builder = InlineKeyboardBuilder()
    # Если мы в процессе подписки, callback будет другим
    prefix = "sub_sign_" if is_sub else "show_sign_"
    for s in signs:
        builder.add(InlineKeyboardButton(text=s, callback_data=f"{prefix}{s.lower()}"))
    builder.adjust(3) # Кнопки по 3 в ряд
    return builder.as_markup()

def unsubscribe_kb():
    """ Кнопка для отмены подписки. """
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отписаться от рассылки", callback_data="unsub")]
    ])