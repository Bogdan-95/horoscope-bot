# Обработчик событий

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
import app.keyboards.inline as kb
import app.database.requests as rq
from app.services.horoscope_api import HoroscopeAPI

router = Router()
api = HoroscopeAPI()

@router.message(CommandStart())
async def cmd_start(message: Message):
    """ Обработка команды /start. Приветствие и регистрация в БД. """
    await rq.set_user(message.from_user.id, message.from_user.username)
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}! Я твой современный астро-бот.\n"
        "Хочешь получить прогноз или настроить ежедневную рассылку?",
        reply_markup=kb.main_menu()
    )

@router.callback_query(F.data == "get_horo")
async def list_signs(callback: CallbackQuery):
    """ Показ списка знаков для разового получения гороскопа. """
    await callback.message.edit_text("✨ Выберите ваш знак зодиака:", reply_markup=kb.signs_kb())

@router.callback_query(F.data.startswith("show_sign_"))
async def show_horo(callback: CallbackQuery):
    """ Получение и вывод гороскопа для выбранного знака. """
    sign = callback.data.split("_")[2]
    await callback.answer("Считываю положение планет...")
    text = await api.get_daily_horoscope(sign)
    await callback.message.answer(text, parse_mode="Markdown")

@router.callback_query(F.data == "sub_manage")
async def sub_menu(callback: CallbackQuery):
    """ Меню управления подпиской (проверка статуса из БД). """
    sub = await rq.get_user_sub(callback.from_user.id)
    if sub and sub[0]:
        await callback.message.edit_text(
            f"✅ Вы подписаны на знак: *{sub[1].capitalize()}*\n"
            f"Рассылка приходит ежедневно в 07:00 (МСК).",
            parse_mode="Markdown",
            reply_markup=kb.unsubscribe_kb()
        )
    else:
        await callback.message.edit_text(
            "🔔 Здесь можно оформить бесплатную подписку.\n"
            "Выберите ваш знак, и я буду присылать гороскоп каждое утро:",
            reply_markup=kb.signs_kb(is_sub=True)
        )

@router.callback_query(F.data.startswith("sub_sign_"))
async def sub_confirm(callback: CallbackQuery):
    """ Подтверждение подписки и сохранение в базу. """
    sign = callback.data.split("_")[2]
    await rq.update_subscription(callback.from_user.id, True, sign)
    await callback.message.edit_text(
        f"🚀 Готово! Теперь каждое утро в 07:00 (МСК) я буду радовать вас прогнозом для знака {sign.capitalize()}."
    )

@router.callback_query(F.data == "unsub")
async def unsub(callback: CallbackQuery):
    """ Удаление подписки из базы данных. """
    await rq.update_subscription(callback.from_user.id, False)
    await callback.message.edit_text("Вы успешно отписались от утренних уведомлений. 🌙")