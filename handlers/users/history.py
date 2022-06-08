from aiogram import types
from aiogram.dispatcher.filters import Command

from loader import dp


@dp.message_handler(Command('history'))
async def history_person(message: types.Message) -> None:
    await message.answer('История запросов:')
