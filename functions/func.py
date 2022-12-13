import datetime
import json
import re

import requests

from config_data.config import RAPID_API_KEY


def search_hotels(id_city: str, date1: str, date2: str, hotels_num: str, sort_order: str) -> dict:
    """
    Ищет отели по заданным параметрам.

    :param id_city: ID отеля/ hotel ID
    :param date1: Дата заезда / Check in date
    :param date2: Дата выезда / Check out date
    :param hotels_num: Количество отелей которое для показа / The number of hotels to display
    :param sort_order: Параметр сортировки / Sorting Parameter
    :return: dict
    """

    url = "https://hotels4.p.rapidapi.com/properties/list"

    querystring = {"destinationId": id_city, "pageNumber": "1", "pageSize": hotels_num, "checkIn": date1,
                   "checkOut": date2, "adults1": "1", "sortOrder": sort_order, "locale": "en_US", "currency": "RUB",
                   "guestRatingMin": "1"}

    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    to_json = json.loads(response.text)
    hotels_names = to_json['data']['body']['searchResults']['results']
    if querystring["currency"] == 'USD':
        hotels = {i_hotel['name']: [re.search(r'(?<=\$)\S+', i_hotel['ratePlan']['price']['fullyBundledPricePerStay']).
                                    group(0).replace(',', ''),
                                    str(i_hotel['id']),
                                    i_hotel.get('guestReviews', {}).get('unformattedRating', '0'),
                                    i_hotel["starRating"],
                                    i_hotel["address"]["locality"],
                                    i_hotel["address"].get("streetAddress", 'не определен'),
                                    i_hotel["landmarks"][0]['distance']
                                    ]
                  for i_hotel in hotels_names
                  }
        return hotels
    elif querystring["currency"] == 'RUB':
        hotels = {i_hotel['name']: [re.search(r'\S*(?= RUB)',
                                              i_hotel['ratePlan']['price']['fullyBundledPricePerStay']).group(0).replace
                                    (',', ''),
                                    str(i_hotel['id']),
                                    i_hotel.get('guestReviews', {}).get('unformattedRating', '0'),
                                    i_hotel["starRating"],
                                    i_hotel["address"]["locality"],
                                    i_hotel["address"].get("streetAddress", 'не определен'),
                                    i_hotel["landmarks"][0]['distance']
                                    ]
                  for i_hotel in hotels_names
                  }
        return hotels

    # Возвращает словарь вида {"Название отеля" : ["Стоимость проживания за период", "ID отеля", "Рейтинг",
    # "Звезд отеля", "Город", "Дом-Улица", "Удаленность от центра"]
    # Returns a dictionary of the form {"Hotel name" : ["Cost of accommodation for the period",
    # "Rating","Hotel ID", "starRating", "City", "House-Street", "Distance from the center"]


def change_city(city: str) -> dict:
    """
    Подбирает город на основе введенных данных пользователем

    :param city: название города / name of the city
    :return: dict
    """
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"

    querystring = {f"query": city, "locale": "en_US", "currency": "USD"}

    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    to_json = json.loads(response.text)
    cities = {i_city['name']: i_city['destinationId']
              for i_city in to_json['suggestions'][0]['entities']}
    # Возвращает словарь вида {''название города: ''id города}
    return cities


def change_photo(hotel_id: str, photo_num: int) -> list:
    """
    Находит фото отеля по заданным параметрам.

    :param hotel_id: ID отеля / Hotel ID
    :param photo_num: Количество фото для показа / Number of photos to show
    :return: list: Список ссылок на фотографии / List of links to photos
    """
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

    querystring = {"id": hotel_id}

    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    to_json = json.loads(response.text)

    hotel_photos = [to_json['hotelImages'][i_url]['baseUrl'].format(size='y') for i_url in range(photo_num)
                    ]

    return hotel_photos


def miles_to_km(miles: str) -> float:
    """
    Переводит мили в километры.

    :param miles: Количество миль / Number of miles
    :return: float: Значение в километрах / Value in kilometers
    """
    mile = (re.search(r'^\d*.\d*', miles)).group(0)
    km = round(float(mile) * 1.6093, 1)
    return km


def period_of_stay(date_in: str, date_out: str) -> int:
    """
    Считает количество дней которые планируется прожить в отеле исходя из полученных дат
    заезда и даты выезда из отеля. Возвращает целое число (число ночей в отеле)

    :param date_in: дата заезда. / check-in date.
    :param date_out: дата выезда / check-out date.
    :return: int
    """
    days = (datetime.datetime.strptime(date_out, '%Y-%m-%d') -
            datetime.datetime.strptime(date_in, '%Y-%m-%d')).days
    return days


def hotel_stars(stars: float) -> str:
    """
    Выводит соответствующее количество звезд отеля согласно полученным данным.


    :param stars: Количество звезд отеля.
    :return: str строка с количеством звезд отеля из 5 звезд
    """
    star = '&#9733;'
    empty_star = '&#9734;'
    half_star = '+'
    hotel_star = stars
    if hotel_star == int(stars):
        hotel_star = int(stars)
        half = 0
    else:
        hotel_star = int(stars)
        half = 1
    return f'{star * hotel_star}{(5 - hotel_star) * empty_star}{half_star * half}'


def price_range(prices: str) -> tuple:
    """
    Переводит полученный диапазон цен от пользователя в минимальный и
    максимальный порог цен. Возвращает значение в виде кортежа только если
    введенные данные являются цифрами.

    :param prices: Диапазон цен имеет вид "100-1000"
    :return: tuple(100, 1000)
    """
    prices = re.split('[.,:;/-]', prices)
    if len(prices) == 2 and prices[0].isdigit() and prices[1].isdigit():
        price_min = min(prices)
        price_max = max(prices)
        return int(price_min), int(price_max)


def distance_range(distance: str) -> tuple:
    """
    Переводит полученный диапазон расстояния от пользователя в минимальный и
    максимальный порог расстояния. Возвращает значение в виде кортежа только если
    введенные данные являются цифрами.

    :param distance: Диапазон цен имеет вид "1-100"
    :return: tuple(1, 100)
    """
    distance = re.split('[.,:;/-]', distance)
    if len(distance) == 2 and distance[0].isdigit() and distance[1].isdigit():
        distance_min = min(distance)
        distance_max = max(distance)
        return int(distance_min), int(distance_max)


def check_price_value(value: str) -> bool:
    """
    Проверяет полученные данные от пользователя.

    :param value: Полученные данные от пользователя. / Received data from the user.
    :return: bool
    """
    price = price_range(value)
    if price:
        return True
    else:
        return False


def check_distance_value(value: str) -> bool:
    """
    Проверяет полученные данные от пользователя.

    :param value: Полученные данные от пользователя. / Received data from the user.
    :return: bool
    """
    distance = distance_range(value)
    if distance:
        return True
    else:
        return False


def search_bestdeal_hotels(id_city: str, date1: str, date2: str, hotels_num: str, price: tuple,
                           distance: tuple) -> dict:
    """
    Ищет отели по заданным параметрам.

    :param id_city: ID отеля/ hotel ID
    :param date1: Дата заезда / Check in date
    :param date2: Дата выезда / Check out date
    :param hotels_num: Количество отелей которое для показа / The number of hotels to display
    :param price: Диапазон цен / Price range
    :param distance: Диапазон расстояния / Distance range
    :return: dict
    """

    url = "https://hotels4.p.rapidapi.com/properties/list"

    querystring = {"destinationId": id_city, "pageNumber": "1", "pageSize": hotels_num, "checkIn": date1,
                   "checkOut": date2, "adults1": "1", "priceMin": str(price[0]), "priceMax": str(price[1]),
                   "sortOrder": 'PRICE', "locale": "en_US", "currency": "RUB", "guestRatingMin": "1"
                   }

    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    to_json = json.loads(response.text)
    hotels_names = to_json['data']['body']['searchResults']['results']
    if querystring["currency"] == 'USD':
        hotels = {i_hotel['name']: [i_hotel['ratePlan']['price']['exactCurrent'],
                                    str(i_hotel['id']),
                                    i_hotel.get('guestReviews', {}).get('unformattedRating', '0'),
                                    i_hotel["starRating"],
                                    i_hotel["address"]["locality"],
                                    i_hotel["address"].get("streetAddress", 'не определен'),
                                    i_hotel["landmarks"][0]['distance']
                                    ]
                  for i_hotel in hotels_names
                  }
        return hotels
    elif querystring["currency"] == 'RUB':
        hotels = {i_hotel['name']: [i_hotel['ratePlan']['price']['exactCurrent'],
                                    str(i_hotel['id']),
                                    i_hotel.get('guestReviews', {}).get('unformattedRating', '0'),
                                    # Если не находит ключ "guestReviews", то рейтинг по умолчанию 0
                                    i_hotel["starRating"],
                                    i_hotel["address"]["locality"],
                                    i_hotel["address"].get("streetAddress", 'не определен'),
                                    # Если ключа "streetAddress", то по умолчанию ставится адрес не определен.
                                    i_hotel["landmarks"][0]['distance']
                                    ]
                  for i_hotel in hotels_names}
        hotels = dict(tuple(filter(lambda x: distance[0] <= miles_to_km(x[1][6]) <= distance[1], hotels.items())))
        return hotels

    # Возвращает словарь вида {"Название отеля" : ["Стоимость проживания за ночь", "ID отеля", "Рейтинг",
    # "Звезд отеля", "Город", "Дом-Улица", "Удаленность от центра"]
    # Returns a dictionary of the form {"Hotel name" : ["Cost of accommodation per night",
    # "Rating","Hotel ID", "starRating", "City", "House-Street", "Distance from the center"]


def checking_date_numbers(date: str) -> bool:
    """
    Проверяет чтобы дата полученная от пользователя, была указана в соответствующем диапазоне.
    Число от 1 до 31.
    Месяц от 1 до 12.
    Год от 2022.

    :param date: Дата введенная пользователем.
    :return: bool
    """
    date_to_list = re.split('[./,;:]', date)
    if 0 < int(date_to_list[0]) <= 31 and 0 < int(date_to_list[1]) <= 12 and int(date_to_list[2]) >= 2022:
        return True
    return False


def checking_date_entry(date: str) -> bool:
    """
    Проверяет дату, полученную от пользователя, что она имеет формат ввода ДД.ММ.ГГГГ.

    :param date: Дата введенная пользователем.
    :return: bool
    """
    date = '.'.join((re.split('[./,;:]', date)))
    val = re.findall(r'^\d\d.\d\d.\d\d\d\d$', date)
    if val and checking_date_numbers(date):
        return True
    else:
        return False


def check_date_in(date: str) -> bool:
    """
    Проверка даты заезда в отель введенной пользователем.
    Что дата не является прошедшим и сегодняшним числом.
    По логике отель можно забронировать только на следующий день.

    :param date: Дата введенная пользователем.
    :return: bool
    """
    date = '.'.join((re.split('[./,;:]', date)))
    today = datetime.datetime.now()
    if today >= datetime.datetime.strptime(date, '%d.%m.%Y'):
        return False
    return True


def minimum_check_in_date() -> str:
    """
    Вычисляет минимальную дату заезда в отель.
    К сегодняшнему числу прибавляет 1 день.

    :return: str ('01.01.2000')
    """
    today = datetime.datetime.now()
    check_in_date = (today + datetime.timedelta(days=1)).strftime('%d.%m.%Y')
    return check_in_date


def calc_departure_date(date: str) -> str:
    """
    Вычисляет крайнюю дату выезда, согласно сайту hotels.com забронировать номер можно
    на не более чем 28 дней с даты заезда.
    Возвращает крайнюю дату выезда.

    :param date: Дата введенная пользователем.
    :return: Крайняя дата выезда.
    """
    date = '.'.join((re.split('[./,;:]', date)))
    check_in_date = datetime.datetime.strptime(date, '%d.%m.%Y').date()
    check_out_date = (check_in_date + datetime.timedelta(28)).strftime('%d.%m.%Y')
    return check_out_date


def checking_departure_date(date_in: str, date_out: str) -> bool:
    """
    Проверяет что период пребывания в отеле не больше 28 дней.

    :param date_in: Дата заезда
    :param date_out: Дата выезда
    :return: bool
    """
    date_out = '.'.join((re.split('[./,;:]', date_out)))
    date1 = datetime.datetime.strptime(date_in, '%Y-%m-%d').date()
    date2 = datetime.datetime.strptime(date_out, '%d.%m.%Y').date()
    delta = (date2 - date1).days
    if delta <= 28:
        return True
    return False


def checking_date_entry_date_departure(date_in: str, date_out: str) -> bool:
    """
    Проверяет чтобы дата выезда была больше чем дата заезда.

    :param date_in: Дата заезда
    :param date_out: Дата выезда
    :return: bool
    """
    date_out = '.'.join((re.split('[./,;:]', date_out)))
    date1 = datetime.datetime.strptime(date_in, '%Y-%m-%d').date()
    date2 = datetime.datetime.strptime(date_out, '%d.%m.%Y').date()
    if date1 < date2:
        return True
    return False
