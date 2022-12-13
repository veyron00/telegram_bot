import datetime
import re

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode, InputMediaPhoto
from loguru import logger

from database.connect_db import write_data
from functions.func import change_city, change_photo, miles_to_km, period_of_stay, hotel_stars, \
    price_range, check_price_value, distance_range, check_distance_value, search_bestdeal_hotels, checking_date_entry, \
    check_date_in, minimum_check_in_date, checking_departure_date, checking_date_entry_date_departure, \
    calc_departure_date
from keyboards.inline.choosing_city import choosing_city
from keyboards.inline.need_photo_yes_or_no import need_photo_yes_or_no
from keyboards.inline.url_button import url_button
from loader import dp, bot
from states.states import FSMBestDeal


@dp.message_handler(commands="bestdeal", state=None)
async def cmd_bestdeal(message: types.Message) -> None:
    """
    Хэндлер для отлавливания команды bestdeal.
    При нажатии вызове команды bestdeal бот предлагает ввести название города.

    :param message: types.Message
    :return: None
    """
    await FSMBestDeal.user_request.set()
    await message.reply("Введите название города")
    logger.info(f"user_id - {message['from']['id']}, command_name - {message.text}")


@dp.message_handler(state=FSMBestDeal.user_request)
async def choose_city_bd(message: types.Message, state: FSMContext) -> None:
    """
    Хэндлер отлавливает название введенное пользователем, и запускает машину состояний.
    Выводит в чат найденные варианты городов.

    :param message: types.Message Название города
    :param state: FSMContext
    :return: None
    """
    logger.info(f"user_id - {message['from']['id']}, entered_text - {message.text}")
    async with state.proxy() as data:
        data['user_request'] = message.text
    my_cities = change_city(data['user_request'])
    if len(my_cities) > 0:
        logger.info(f"user_id - {message['from']['id']}, found_cities - {[i_city for i_city in my_cities.keys()]}")
        await FSMBestDeal.next()
        chat_info = await message.answer("Выберите подходящий вариант", reply_markup=choosing_city(my_cities))
        async with state.proxy() as data:
            data['command_name'] = 'bestdeal'
        await FSMBestDeal.next()
        async with state.proxy() as data:
            data['chat_id'] = chat_info['chat']['id']
        await FSMBestDeal.next()
    else:
        logger.error(f"user_id - {message['from']['id']}, CITY NOT FOUND")
        await message.answer("Нет подходящих вариантов")
        await message.answer("Введите другое название города")
        await FSMBestDeal.user_request.set()


@dp.callback_query_handler(lambda query: query.data.startswith('next'), state=FSMBestDeal.city_id)
async def choose_price_range_bd(query: types.CallbackQuery, state: FSMContext) -> None:
    """
    Хэндлер отлавливает callback_data передаваемый при нажатии пользователем по названию города.
    Предлагает ввести диапазон цен в пределах которых необходимо найти отели.

    :param query: types.CallbackQuery Город выбранный пользователем
    :param state: FSMContext
    :return: None
    """
    logger.info(f"user_id - {query.message['chat']['id']}, "
                f"selected_city - "
                f"{[i_city[0]['text'] for i_city in query.values['message']['reply_markup']['inline_keyboard'] if query.data == i_city[0]['callback_data']][0]}")
    async with state.proxy() as data:
        data['city_id'] = re.search(r'\d\S+', query.data).group(0)
    await FSMBestDeal.next()
    await query.message.answer('Введите диапазон цен (в формате 100-1000)')
    await query.answer()


@dp.message_handler(state=FSMBestDeal.price_min)
async def choose_prices(message: types.Message, state: FSMContext) -> None:
    """
    Хэндлер отлавливает диапазон цен введенный пользователем, проверяет на корректность ввода.
    Предлагает ввести диапазон расстояния от центра города.

    :param message: types.Message Диапазон цен
    :param state: FSMContext
    :return: None
    """
    prices = price_range(message.text)
    if check_price_value(message.text):
        logger.info(f"user_id - {message['from']['id']}, entered_text - {message.text}")
        async with state.proxy() as data:
            data['price_min'] = min(prices)
        await FSMBestDeal.next()
        async with state.proxy() as data:
            data['price_max'] = max(prices)
        await FSMBestDeal.next()
        await message.answer("Введите диапазон расстояния до центра (в формате 1-100) км")
    else:
        await message.answer('Введено некорректное значение диапазона цен')
        logger.error(f"user_id - {message['from']['id']}, INCORRECT INPUT PRICE RANGE")


@dp.message_handler(state=FSMBestDeal.distance_min)
async def choose_distance(message: types.Message, state: FSMContext) -> None:
    """
    Хэндлер отлавливает диапазон расстояния введенный пользователем, проверяет на корректность ввода.
    Предлагает ввести дату заезда.

    :param message: types.Message Диапазон расстояния
    :param state: FSMContext
    :return: None
    """
    distance = distance_range(message.text)
    if check_distance_value(message.text):
        logger.info(f"user_id - {message['from']['id']}, entered_text - {message.text}")
        async with state.proxy() as data:
            data['distance_min'] = min(distance)
        await FSMBestDeal.next()
        async with state.proxy() as data:
            data['distance_max'] = max(distance)
        await FSMBestDeal.next()
        await message.answer("Введите дату заезда 📅 (в формате ДД.ММ.ГГГГ)")
    else:
        await message.answer('Введено некорректное значение диапазона расстояния до центра'
                             '\nВведите диапазон расстояния до центра (в формате 1-100) км')
        logger.error(f"user_id - {message['from']['id']}, INCORRECT INPUT DISTANCE RANGE")


@dp.message_handler(state=FSMBestDeal.check_in_date)
async def choose_date_in_bd(query: types.Message, state: FSMContext) -> None:
    """
    Хэндлер отлавливает дату, введенную пользователем, проверяет ее на корректность.
    Предлагает ввести дату выезда.

    :param query: types.Message Дата заезда введенная пользователем
    :param state: FSMContext
    :return: None
    """
    if checking_date_entry(query.text):
        if check_date_in(query.text):
            async with state.proxy() as data:
                data['check_in_date'] = '-'.join(reversed('.'.join((re.split('[./,;:]', query.text))).split('.')))
            await FSMBestDeal.next()
            logger.info(f"user_id - {query['from']['id']}, entered_text - {query.text}")
            await query.answer('Введите дату выезда 📅 (в формате ДД.ММ.ГГГГ)')
        else:
            await query.answer(f'Дата заезда должна быть не ранее {minimum_check_in_date()}'
                               f'\nПопробуйте еще раз, 📅 (в формате ДД.ММ.ГГГГ)')
            logger.error(f"user_id - {query['from']['id']}, CHECK-IN DATE ENTERED TOO EARLY")

    else:
        await query.answer('Дата введена не корректно.'
                           '\nПопробуйте еще раз, 📅 (в формате ДД.ММ.ГГГГ)')
        logger.error(f"user_id - {query['from']['id']}, DATE ENTERED INCORRECTLY")


@dp.message_handler(state=FSMBestDeal.check_out_date)
async def choose_date_out_bd(message: types.Message, state: FSMContext) -> None:
    """
    Хэндлер отлавливает дату выезда введенную пользователем, проверяет ее на корректность.
    Предлагает ввести количество отелей которое необходимо вывести.

    :param message: types.Message Дата выезда введенная пользователем
    :param state: FSMContext
    :return: None
    """
    if checking_date_entry(message.text):
        async with state.proxy() as data:
            if checking_departure_date(data['check_in_date'], message.text):
                if checking_date_entry_date_departure(data['check_in_date'], message.text):
                    data['check_out_date'] = '-'.join(
                        reversed('.'.join((re.split('[./,;:]', message.text))).split('.')))
                    await FSMBestDeal.next()
                    logger.info(f"user_id - {message['from']['id']}, entered_text - {message.text}")
                    await message.answer("Какое количество отелей вывести? (не более 25)")
                else:
                    await message.reply("<b>Дата выезда не может быть раньше даты заезда."
                                        "\nПопробуйте ввести другую дату.</b>", parse_mode=ParseMode.HTML)
                    logger.error(f"user_id - {message['from']['id']}, "
                                 f"THE ARRIVAL DATE CANNOT BE EARLIER THAN THE DEPARTURE DATE")
            else:
                await message.answer(f"Дата выезда не должна превышать 28 дней с даты заезда."
                                     f"\nКрайняя дата выезда "
                                     f"{calc_departure_date('.'.join(list(reversed(data['check_in_date'].split('-')))))}"
                                     f"\nПопробуйте еще раз, 📅 (в формате ДД.ММ.ГГГГ)")
                logger.error(f"user_id - {message['from']['id']}, YOU CAN ONLY BOOK A HOTEL FOR 28 DAYS")

    else:
        await message.answer('Дата введена не корректно.'
                             '\nПопробуйте еще раз, 📅 (в формате ДД.ММ.ГГГГ)')
        logger.error(f"user_id - {message['from']['id']}, DATE ENTERED INCORRECTLY")


@dp.message_handler(state=FSMBestDeal.hotels_num)
async def need_photo_bd(message: types.Message, state: FSMContext) -> None:
    """
    Хэндлер отлавливает введенное количество отелей пользователем.
    И спрашивает нужно ли показывать фото отелей.

    :param message: types.Message Количество отелей введенное пользователем
    :param state: FSMContext
    :return: None
    """
    if 0 < int(message.text) <= 25 and message.text.isdigit():
        async with state.proxy() as data:
            data['hotels_num'] = message.text
        await FSMBestDeal.next()
        logger.info(f"user_id - {message['from']['id']}, entered_text - {message.text}")

        await message.answer("Показывать фото 🏞 отелей?", reply_markup=need_photo_yes_or_no())
    else:
        await message.answer('Введено не корректное число количества отелей'
                             '\nВведите число от 1 до 25.')
        logger.error(f"user_id - {message['from']['id']}, YOU CAN WITHDRAW NO MORE THAN 25 HOTELS")


@dp.callback_query_handler(text='yes', state=FSMBestDeal.photo)
async def choose_photo_num_bd(callback: types.CallbackQuery, state: FSMContext) -> None:
    """
    Хендлер отлавливает callback_data со значением 'yes', и спрашивает какое количество фото
    выводить.

    :param callback: types.CallbackQuery callback_data со значением 'yes'
    :param state: FSMContext
    :return: None
    """
    logger.info(f"user_id - {callback['from']['id']}, selected_parameter - {callback.data}")
    async with state.proxy() as data:
        data['photo'] = callback.data
    await FSMBestDeal.next()
    await callback.message.answer("<b>Сколько фото показать? (не более 10)</b>", parse_mode=ParseMode.HTML)
    await callback.answer()


@dp.callback_query_handler(text='no', state=FSMBestDeal.photo)
async def no_photo_bd(callback: types.CallbackQuery, state: FSMContext) -> None:
    """
    Хендлер отлавливает callback_data со значением 'no', и выводит найденные отели.

    :param callback: types.CallbackQuery callback_data со значением 'no'
    :param state: FSMContext
    :return: None
    """
    async with state.proxy() as data:
        data['photo'] = callback.data
    await FSMBestDeal.next()
    logger.info(f"user_id - {callback['from']['id']}, selected_parameter - {callback.data}")
    async with state.proxy() as data:
        data['num_photo'] = 0
    await state.finish()
    await callback.message.answer("Спасибо данные сохранены")
    hotels = search_bestdeal_hotels(data['city_id'], data['check_in_date'], data['check_out_date'],
                                    data['hotels_num'], (data['price_min'], data['price_max']),
                                    (data['distance_min'], data['distance_max']))

    if len(hotels) > 0:
        logger.info(f"user_id - {callback['from']['id']}, "
                    f"number_of_hotels - {len(hotels)}, "
                    f"found_hotels - {[i_hotel for i_hotel in hotels]}")
        await callback.message.answer(f'{15 * "-"} Найдено {len(hotels)} отелей {15 * "-"}')
        days_of_stay = period_of_stay(data['check_in_date'], data['check_out_date'])
        nums = 0
        search_history_data = {
            'command_name': data['command_name'],
            'user_request': data['user_request'],
            'chat_id': data['chat_id'],
            'datetime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'hotels': '\n'.join([i_hotel for i_hotel in hotels.keys()])
        }
        write_data(search_history_data)
        for key, value in hotels.items():
            nums += 1
            hotel_star = hotel_stars(value[3])
            await callback.message.answer(f'{28 * "-"} Отель {nums} {27 * "-"}'
                                          f'\n🏨 <i><b>{key}</b></i>, '
                                          f'\n{70 * "-"}'
                                          f'\nHotel stars - {hotel_star}'
                                          f'\nРейтинг отеля <i>{value[2]}/10</i>'
                                          f'\nАдрес: <i>{value[4]}, {value[5]}</i>'
                                          f'\nРасстояние до центра <i>{miles_to_km(value[6])} км.</i>'
                                          f'\nСтоимость за ночь <i><b>{round(int(value[0]) / days_of_stay)}</b></i> RUB'
                                          f'\nСтоимость за весь период <i><b>{value[0]}</b></i> RUB'
                                          f'\n{70 * "-"}',
                                          parse_mode=ParseMode.HTML, reply_markup=url_button(value))
            await callback.answer()
        logger.info('search completed successfully'.upper())
    else:
        logger.error(f"user_id - {callback['from']['id']}, NO HOTELS FOUND")
        await callback.message.answer('<b>По вашему запросу отелей не найдено.'
                                      'Попробуйте поискать заново.</b>', parse_mode=ParseMode.HTML)
        await callback.answer()


@dp.message_handler(state=FSMBestDeal.num_photo)
async def with_photo_bd(message: types.Message, state: FSMContext) -> None:
    """
    Хендлер отлавливает количество фото введенное пользователем, и выводит найденные отели
    с фото.

    :param message: types.Message Количество фото
    :param state: FSMContext
    :return: None
    """
    if message.text.isdigit() and 0 < int(message.text) <= 10:
        async with state.proxy() as data:
            data['num_photo'] = message.text
        await state.finish()

        await message.answer("Спасибо данные сохранены")
        hotels = search_bestdeal_hotels(data['city_id'], data['check_in_date'], data['check_out_date'],
                                        data['hotels_num'], (data['price_min'], data['price_max']),
                                        (data['distance_min'], data['distance_max']))
        if len(hotels) > 0:
            logger.info(f"user_id - {message['from']['id']}, "
                        f"entered_text - {message.text}, "
                        f"number_of_hotels - {len(hotels)}, "
                        f"found_hotels - {[i_hotel for i_hotel in hotels]}")
            await message.answer(f'{15 * "-"} Найдено {len(hotels)} отелей {15 * "-"}')
            days_of_stay = period_of_stay(data['check_in_date'], data['check_out_date'])
            nums = 0
            search_history_data = {
                'command_name': data['command_name'],
                'user_request': data['user_request'],
                'chat_id': data['chat_id'],
                'datetime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'hotels': '\n'.join([i_hotel for i_hotel in hotels.keys()])
            }
            write_data(search_history_data)
            for key, value in hotels.items():
                hotel_star = hotel_stars(value[3])
                media_group = []
                nums += 1
                for i_photo in change_photo(value[1], int(data['num_photo'])):
                    media_group.append(InputMediaPhoto(i_photo))
                await bot.send_media_group(message.chat.id, media_group)
                await message.answer(f'{28 * "-"} Отель {nums} {27 * "-"}'
                                     f'\n🏨 <i><b>{key}</b></i>, '
                                     f'\n{70 * "-"}'
                                     f'\nHotel stars - {hotel_star}'
                                     f'\nРейтинг отеля <i>{value[2]}/10</i>'
                                     f'\nАдрес: <i>{value[4]}, {value[5]}</i>'
                                     f'\nРасстояние до центра <i>{miles_to_km(value[6])} км.</i>'
                                     f'\nСтоимость за ночь <i><b>{round(int(value[0]) / days_of_stay)}</b></i> RUB'
                                     f'\nСтоимость за весь период <i><b>{value[0]}</b></i> RUB'
                                     f'\n{70 * "-"}',
                                     parse_mode=ParseMode.HTML, reply_markup=url_button(value))
            logger.info('search completed successfully'.upper())
        else:
            logger.error(f"user_id - {message ['from']['id']}, NO HOTELS FOUND")
            await message.answer('<b>По вашему запросу отелей не найдено.'
                                 'Попробуйте поискать заново.</b>', parse_mode=ParseMode.HTML)

    else:
        await message.answer('Введено не корректное значение количества фотографий'
                             '\nСколько фото показать? (не более 10)')
        logger.error(f"user_id - {message['from']['id']}, YOU CAN OUTPUT NO MORE THAN 10 PHOTOS")


def register_handler_bestdeal(dp: Dispatcher):
    dp.register_message_handler(cmd_bestdeal, commands="bestdeal", state=None)
    dp.register_message_handler(choose_city_bd, state=FSMBestDeal.user_request)
    dp.register_callback_query_handler(choose_price_range_bd, lambda query: query.data.startswith('next'),
                                       state=FSMBestDeal.city_id)
    dp.register_message_handler(choose_prices, state=FSMBestDeal.price_min)
    dp.register_message_handler(choose_distance, state=FSMBestDeal.distance_min)
    dp.register_message_handler(choose_date_in_bd, state=FSMBestDeal.check_in_date)
    dp.register_message_handler(choose_date_out_bd, state=FSMBestDeal.check_out_date)
    dp.register_message_handler(need_photo_bd, state=FSMBestDeal.hotels_num)
    dp.register_callback_query_handler(choose_photo_num_bd, text='yes', state=FSMBestDeal.photo)
    dp.register_callback_query_handler(no_photo_bd, text='no', state=FSMBestDeal.photo)
    dp.register_message_handler(with_photo_bd, state=FSMBestDeal.num_photo)
