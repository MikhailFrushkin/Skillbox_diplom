from data.requests import get_photos


async def prepare_data(hotel, is_photo, message_data) -> dict:
    """
    Вывод результата пользователю
    :param hotel:
    :param is_photo: вывод фото
    :param message_data:
    """
    hotel_id = hotel.get('id')
    hotel_name = hotel.get('name')
    base_address = hotel.get('address')
    address = 'Город {}, {}, {}'.format(
        base_address.get("region"), base_address.get("locality"), hotel.get("address").get("streetAddress")
    )
    price = hotel.get('ratePlan').get('price').get('current')
    distance_from_center = hotel.get('landmarks')[0].get('distance')

    if is_photo:
        photo_url_list = await get_photos(hotel_id=hotel['id'], photo_amount=message_data.get('photo_amount'))
    data_to_return = {
        'hotel_id': hotel_id,
        'hotel_name': hotel_name,
        'address': address,
        'distance_from_center': distance_from_center,
        'price': price,
        'photo_url': photo_url_list if is_photo else None
    }
    return data_to_return


async def handler_request(request: list, message_data: dict, is_photo: bool) -> list:
    """
    Обрабатывает ответ от сервера на запрос отелей. Если необходимы фото, делает запрос за фото.
    И возвращает данные для ответа в виде списка.
    :param is_photo:
    :param request:
    :param message_data:
    """
    data_to_return: list = []
    for hotel in request:
        hotel_data = await prepare_data(hotel, is_photo, message_data)
        data_to_return.append(hotel_data)
    return data_to_return
