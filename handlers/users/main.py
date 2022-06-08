from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart, CommandHelp

from handlers.users.anyprice import get_any_price
from handlers.users.back import back
from handlers.users.bestdeal import bestdeal
from handlers.users.history import history_person
from keyboards.default import menu
from loader import dp, bot
from aiogram.dispatcher.filters import Command


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message) -> None:
    await message.answer('Добро пожаловать, {}!'
                         '\nЯ бот - HotelsOnTheTrip'
                         '\nИ я помогу, подобрать отель на время поездки.'
                         '\nДля вызова справки введите /help'.format(message.from_user.first_name), reply_markup=menu)


@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message) -> None:
    text = '● /help — помощь по командам бота\n' \
           '● /lowprice — вывод самых дешёвых отелей в городе\n' \
           '● /highprice — вывод самых дорогих отелей в городе\n' \
           '● /bestdeal — вывод отелей, наиболее подходящих' \
           'по цене и расположению от центра.\n' \
           '● /history — вывод истории поиска отелей'
    await message.answer(text)


@dp.message_handler(Command('history'))
async def history(message: types.Message) -> None:
    await history_person(message)


@dp.message_handler(commands=['lowprice', 'highprice'], state='*')
async def anyprice(message: types.Message, state: FSMContext) -> None:
    await get_any_price(message, state)


@dp.message_handler(content_types=['text'], state='*')
async def bot_message(message: types.Message, state: FSMContext) -> None:
    if message.text == 'Поиск по убыванию цены' or message.text == 'Поиск по возрастанию цены':
        await get_any_price(message, state)
    elif message.text == 'Поиск по точным параметрам':
        await bestdeal(message, state)
    elif message.text == 'Помощь':
        await bot_help(message)
    elif message.text == 'История':
        await history_person(message)
    elif message.text == 'В главное меню':
        await back(message, state)
    else:
        await bot.send_message(message.from_user.id, message.text)
