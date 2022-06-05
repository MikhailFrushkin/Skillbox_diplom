from aiogram import types


async def set_default_commands(dp):
    """команды бота в меню"""
    await dp.bot.set_my_commands(
        [
            types.BotCommand('start', 'Запустить бота'),
            types.BotCommand('help', 'Вывести справку'),
            types.BotCommand('lowprice', 'Поиск по возрастанию цены'),
            types.BotCommand('highprice', 'Поиск по убыванию цены'),
            types.BotCommand('bestdeal', 'Поиск по точным параметрам'),
            types.BotCommand('history', 'История'),

        ]
    )
