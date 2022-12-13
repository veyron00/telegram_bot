from aiogram.dispatcher.filters.state import StatesGroup, State


class FSMLowPrise(StatesGroup):
    """
    Класс машины состояний для команды lowprice
    """
    user_request = State()  # Запрос пользователя
    command_name = State()  # Имя команды
    chat_id = State()  # ID чата
    city_id = State()  # ID города
    check_in_date = State()  # Дата заезда
    check_out_date = State()  # Дата выезда
    hotels_num = State()  # Количество отелей
    photo = State()  # Нужно ли фото да / нет
    num_photo = State()  # Количество фото


class FSMHighPrise(StatesGroup):
    """
    Класс машины состояний для команды highprice
    """
    user_request = State()  # Запрос пользователя
    command_name = State()  # Имя команды
    chat_id = State()  # ID чата
    city_id = State()  # ID города
    check_in_date = State()  # Дата заезда
    check_out_date = State()  # Дата выезда
    hotels_num = State()  # Количество отелей
    photo = State()  # Нужно ли фото да / нет
    num_photo = State()  # Количество фото


class FSMBestDeal(StatesGroup):
    """
    Класс машины состояний для команды bestdeal
    """
    user_request = State()  # Запрос пользователя
    command_name = State()  # Имя команды
    chat_id = State()  # ID чата
    city_id = State()  # ID города
    price_min = State()  # Минимальная цена
    price_max = State()  # Максимальная цена
    distance_min = State()  # Минимальная дистанция
    distance_max = State()  # Максимальная дистанция
    check_in_date = State()  # Дата заезда
    check_out_date = State()  # Дата выезда
    hotels_num = State()  # Количество отелей
    photo = State()  # Нужно ли фото да / нет
    num_photo = State()  # Количество фото
