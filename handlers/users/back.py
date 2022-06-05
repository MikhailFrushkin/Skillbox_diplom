from aiogram import types
from aiogram.dispatcher import FSMContext
from loguru import logger
from keyboards.default import menu
from loader import bot


async def back(message: types.Message, state: FSMContext):
    """Кнопка , скидывает стейты и возвращает в главное меню"""
    logger.info('Нажата кнопка "В главное меню"')
    await bot.send_message(message.from_user.id, 'Выберите пункт меню. ', reply_markup=menu)
    await state.reset_state()
