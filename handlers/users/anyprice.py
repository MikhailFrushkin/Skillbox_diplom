import asyncio
from datetime import datetime, date

from aiogram import types
from aiogram.dispatcher import FSMContext
from loguru import logger
from telegram_bot_calendar import DetailedTelegramCalendar

from data import config
from data.config import path
from data.handler_request import handler_request
from data.requests import get_city_id, get_hotels
from handlers.users.back import back
from keyboards.default.menu import back_button, menu
from keyboards.inline.is_photo import is_photo
from loader import dp, bot
from states.States import Anyprice
from utils.chek_local import locale_check
from utils.del_message import delete_message


async def get_any_price(message: types.Message, state: FSMContext) -> None:
    """
    По нажатию на команду /lowprice или /highprice запускает серию хендлеров для уточнения информации
    Сохраняет ответы в машину состояний states.Anyprice
    :param state: Данные из контекста
    :param message: Входящее сообщение
    """
    logger.info('Пользователь {}: {} запросил команду /lowprice или  /highprice'.format(
        message.from_user.id,
        message.from_user.username))
    mes = await message.answer('Напишите город, где хотите подобрать отель.', reply_markup=back_button)
    await bot.delete_message(message.chat.id, message.message_id)
    async with state.proxy() as data:
        data['command'] = message.get_command()
        data['temp_mes'] = mes

        if message.get_command() == '/lowprice' or message.text == 'Поиск по убыванию цены':
            data['price_sort'] = 'PRICE'
        elif message.get_command() == '/highprice' or message.text == 'Поиск по возрастанию цены':
            data['price_sort'] = 'PRICE_HIGHEST_FIRST'

    await Anyprice.city.set()


@dp.message_handler(state=Anyprice.city)
async def answer_city(message: types.Message, state: FSMContext) -> None:
    """
    Получает ответ из get_any_price хэндлера, сохраняет в кэш, спрашивает следующий вопрос,
    сохраняет в state следующего вопроса.
    :param message: входящее сообщение из state
    :param state: Переданный контекст
    """
    if message.text == 'В главное меню':
        await back(message, state)
    else:
        async with state.proxy() as data:
            await bot.send_message(message.from_user.id, 'Вы выбрали город: {}'.format(message.text.title()),
                                   reply_markup=back_button)
            asyncio.create_task(delete_message(message))
            answer = message.text.lower()
            locale = config.locales[locale_check(answer)].get('locale')
            currency = config.locales[locale_check(answer)].get('currency')
            with open('{}/stikers/seach.tgs'.format(path), 'rb') as sticker:
                sticker = await message.answer_sticker(sticker)
            city_id = await get_city_id(answer, locale)
            if city_id:
                logger.info('Сохраняю ответ в state: city')

                asyncio.create_task(delete_message(data['temp_mes']))
                mes = await message.answer('Сколько отелей показать? (Максимально: {})'.format(config.MAX_HOTELS_TO_SHOW))
                data['city'] = answer
                data['city_id'] = city_id
                data['locale'] = locale
                data['currency'] = currency
                data['temp_mes'] = mes

                logger.info('Сохраняю ответ в state: hotel_amount')
                await Anyprice.next()
            else:
                await bot.send_message(message.from_user.id, '😓Упс.Неверно указан город, пожалуйста повторите ввод.')
            asyncio.create_task(delete_message(sticker))


@dp.message_handler(state=Anyprice.hotel_amount)
async def answer_hotel_amount(message: types.Message, state: FSMContext) -> None:
    """
       Получает ответ из answer_city хэндлера, сохраняет в кэш, спрашивает следующий вопрос,
       сохраняет в state следующего вопроса.
       :param message: входящее сообщение из state
       :param state: Переданный контекст
       """
    if message.text == 'В главное меню':
        await back(message, state)
    else:
        if not message.text.isdigit():
            await message.answer('Введите цифрами')
            await answer_hotel_amount(message, state)
        else:
            logger.info('Получил ответ: {}. Сохраняю в state'.format(message.text))
            asyncio.create_task(delete_message(message))
            await bot.send_message(message.from_user.id, 'Вы выбрали для показа отелей: {}'.format(message.text),
                                   reply_markup=back_button)
            async with state.proxy() as data:
                data['hotels_amount'] = int(message.text)
                asyncio.create_task(delete_message(data['temp_mes']))
                mes = await message.answer('Выберите дату заезда')
                data['temp_mes'] = mes
                logger.info('Вызываю Календарь заезда')
            LSTEP = {'y': 'год', 'm': 'месяц', 'd': 'день'}
            min_date = list(map(lambda x: int(x), datetime.now().strftime('%Y %m %d').split()))
            calendar, step = DetailedTelegramCalendar(locale='ru', min_date=date(*min_date)).build()
            await message.answer('Выберите {}'.format(LSTEP[step]), reply_markup=calendar)
            await Anyprice.next()


@dp.callback_query_handler(DetailedTelegramCalendar.func(), state=Anyprice.check_in_date)
async def inline_kb_answer_callback_handler(call: types.CallbackQuery, state: FSMContext) -> None:
    """
    Получает ответ из хэндлера о дате заезда и сохраняет в state
    :param call: входящее сообщение из state
    :param state: Переданный контекст
    """
    LSTEP = {'y': 'год', 'm': 'месяц', 'd': 'день'}
    min_date = list(map(lambda x: int(x), datetime.now().strftime('%Y %m %d').split()))
    result, key, step = DetailedTelegramCalendar(locale='ru', min_date=date(*min_date)).process(call.data)
    async with state.proxy() as data:
        if not result and key:
            await bot.edit_message_text('Выберите {}'.format(LSTEP[step]),
                                        call.message.chat.id,
                                        call.message.message_id,
                                        reply_markup=key)
        elif result:
            result_list = str(result).split('-')
            await bot.edit_message_text('Дата заезда: {}-{}-{}'.format(result_list[2],
                                                                       result_list[1],
                                                                       result_list[0]),
                                        call.message.chat.id,
                                        call.message.message_id)
            logger.info('Получили дату заезда: - {}'.format(result))
            data['check_in'] = str(result)
            logger.info('Сохраняю ответ в state: check_in_date')
            asyncio.create_task(delete_message(data['temp_mes']))
            mes = await call.message.answer('Выберите дату выезда')
            data['temp_mes'] = mes
            logger.info('Вызываю Календарь выезда')
            calendar, step = DetailedTelegramCalendar(locale='ru', min_date=date(*min_date)).build()
            await call.message.answer('Выберите {}'.format(LSTEP[step]), reply_markup=calendar)
            await Anyprice.next()


@dp.callback_query_handler(DetailedTelegramCalendar.func(), state=Anyprice.check_out_date)
async def inline_kb_answer_callback_handler(call: types.CallbackQuery, state: FSMContext) -> None:
    """
    Получает ответ из хэндлера о дате выезда и сохраняет в state
    :param call: входящее сообщение из state
    :param state: Переданный контекст
    """
    LSTEP = {'y': 'год', 'm': 'месяц', 'd': 'день'}
    min_date = list(map(lambda x: int(x), datetime.now().strftime('%Y %m %d').split()))
    result, key, step = DetailedTelegramCalendar(locale='ru', min_date=date(*min_date)).process(call.data)
    async with state.proxy() as data:
        if not result and key:
            await bot.edit_message_text('Выберите {}'.format(LSTEP[step]),
                                        call.message.chat.id,
                                        call.message.message_id,
                                        reply_markup=key)
        elif result:
            result_list = str(result).split('-')
            await bot.edit_message_text('Дата выезда: {}-{}-{}'.format(result_list[2],
                                                                       result_list[1],
                                                                       result_list[0]),
                                        call.message.chat.id,
                                        call.message.message_id)
            logger.info('Получили дату выезда: - {}'.format(result))
            data['check_out'] = str(result)
            asyncio.create_task(delete_message(data['temp_mes']))
            logger.info('Сохраняю ответ в state: check_out_date')
            mes = await call.message.answer('Загрузить фотографии?', reply_markup=is_photo)
            data['temp_mes'] = mes
            await Anyprice.next()


@dp.callback_query_handler(state=Anyprice.IsPhoto)
async def answer_is_photo(call: types.CallbackQuery, state: FSMContext) -> None:
    """
        Получает ответ , сохраняет в кэш, в зависимости от результата прошлого ответа,
        если ответ нет, выводим результат, иначе идем в следующий state
        :param call: входящее сообщение из state
        :param state: Переданный контекст
        """
    await call.answer(cache_time=60)
    answer: str = call.data
    logger.info('Получил ответ: {}. Сохраняю в state'.format(answer))
    async with state.proxy() as data:
        asyncio.create_task(delete_message(data['temp_mes']))
        data['is_photo']: str = answer
        if data['is_photo'] == 'да':
            mes = await call.message.answer('Укажите количество фотографий. (max: {})'.format(config.MAX_PHOTO_TO_SHOW))
            data['temp_mes'] = mes
            await Anyprice.next()
        elif data['is_photo'] == 'нет':
            mes = await call.message.answer('Загружаю информацию, ожидайте...')
            with open('{}/stikers/seach.tgs'.format(path), 'rb') as sticker:
                sticker = await call.message.answer_sticker(sticker)
            data['temp_mes'] = mes
            hotels = await get_hotels(city_id=data['city_id'], hotels_amount=data['hotels_amount'],
                                      currency=data['currency'], locale=data['locale'],
                                      check_in=data['check_in'], check_out=data['check_out'],
                                      price_sort=data['price_sort'])
            if not hotels:
                mes = await call.message.answer('😓Гостиниц по Вашему запросу не найдено.')
                data['temp_mes'] = mes
            else:
                data_to_user_response = await handler_request(request=hotels, message_data=data, is_photo=False)
                for hotel in data_to_user_response:
                    hotel_id = hotel.get('hotel_id')
                    answer_message = 'Название: {name}\n' \
                                     'Адрес: {adress}\n' \
                                     'Расстояние от центра: {dist}\n' \
                                     'Цена за сутки: {price}\n' \
                                     'Ссылка на отель: {url}'.format(name=hotel.get("hotel_name"),
                                                                     adress=hotel.get("address"),
                                                                     dist=hotel.get("distance_from_center"),
                                                                     price=hotel.get("price"),
                                                                     url='ru.hotels.com/ho{}'.format(
                                                                         hotel_id
                                                                     )
                                                                     )
                    await call.message.answer(answer_message)
                    asyncio.create_task(delete_message(data['temp_mes']))
                asyncio.create_task(delete_message(sticker))
            await state.reset_state()
            logger.info('Очистил state')


@dp.message_handler(state=Anyprice.Photo_amount)
async def answer_photo_amount(message: types.Message, state: FSMContext) -> None:
    """
       Получает ответ из answer_is_photo хэндлера, сохраняет в кэш.
       Делает запрос к RapidApi, возвращает ответ пользователю.

       :param message: входящее сообщение из state
       :param state: Переданный контекст
       """
    if message.text == 'В главное меню':
        await back(message, state)
    else:
        asyncio.create_task(delete_message(message))
        answer = message.text
        if not message.text.isdigit():
            await message.answer('Введите цифрами')
            await answer_photo_amount(message, state)
        else:
            await bot.send_message(message.from_user.id, 'Выбрано к показу фотографий: {}'.format(message.text),
                                   reply_markup=back_button)
            asyncio.create_task(delete_message(message))
            logger.info('Получил ответ: {}. Сохраняю в state'.format(answer))
            async with state.proxy() as data:
                asyncio.create_task(delete_message(data['temp_mes']))
                data['photo_amount'] = int(answer)
                mes = await message.answer('Загружаю информацию, ожидайте...')
                with open('{}/stikers/seach.tgs'.format(path), 'rb') as sticker:
                    sticker = await message.answer_sticker(sticker)
                data['temp_mes'] = mes
                hotels: list = await get_hotels(city_id=data['city_id'], hotels_amount=data['hotels_amount'],
                                                currency=data['currency'], locale=data['locale'],
                                                check_in=data['check_in'], check_out=data['check_out'],
                                                price_sort=data['price_sort'])

                if not hotels:
                    await message.answer('Гостиниц по Вашему запросу не найдено!')
                else:
                    data_to_user_response = await handler_request(request=hotels, message_data=data, is_photo=True)
                    for hotel in data_to_user_response:
                        try:
                            if len(hotel['photo_url']) >= 2:
                                media = types.MediaGroup()
                                for photo in hotel['photo_url']:
                                    media.attach_photo(photo)
                                await message.answer_media_group(media)
                            else:
                                await message.answer_photo(hotel['photo_url'][0])

                            hotel_id = hotel.get('hotel_id')
                            answer_message = 'Наименование: {name}\n' \
                                             'Адрес: {adress}\n' \
                                             'Расстояние от центра: {dist}\n' \
                                             'Цена: {price}\n' \
                                             'Ссылка на отель: {url}'.format(name=hotel.get("hotel_name"),
                                                                             adress=hotel.get("address"),
                                                                             dist=hotel.get("distance_from_center"),
                                                                             price=hotel.get("price"),
                                                                             url='ru.hotels.com/ho{}'.format(
                                                                                 hotel_id
                                                                             )
                                                                             )

                            await message.answer(answer_message, disable_web_page_preview=True, reply_markup=menu)
                        except Exception as ex:
                            logger.debug('Ошибка в выводе фото {}'.format(ex))
                            continue
                    asyncio.create_task(delete_message(sticker))
                    asyncio.create_task(delete_message(data['temp_mes']))
            await state.reset_state()
            logger.info('Очистил state')
