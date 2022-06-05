from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton('Поиск по убыванию цены'),
     KeyboardButton('Поиск по возрастанию цены')],
    [KeyboardButton('Поиск по точным параметрам'),
     KeyboardButton('Помощь')],
    [KeyboardButton('История')]],
    resize_keyboard=True)

back_button = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton('В главное меню')]],
    resize_keyboard=True)
