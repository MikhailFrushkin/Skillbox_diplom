from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

is_photo = InlineKeyboardMarkup(row_width=2, inline_keyboard=[
    [
        InlineKeyboardButton(text='Да', callback_data='да'),
        InlineKeyboardButton(text='Нет', callback_data='нет')
    ]
])

