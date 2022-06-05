from aiogram import types
from aiogram.dispatcher.filters import Command

from loader import dp


@dp.message_handler(Command('bestdeal'))
async def bestdeal(message: types.Message):
    await message.answer('Вы выбрали поиск по точным параметрам\n'
                         'введите название города')
