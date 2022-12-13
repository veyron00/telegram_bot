import sqlite3 as sq


def sql_start() -> None:
    """
    Создает подключение к БД если БД отсутствует, то создает БД history.db БД
    Далее в БД создается таблица с необходимыми полями.

    :return: None
    """
    with sq.connect('database/history.db') as con:
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS user_search_history (
        command_name TEXT,
        user_request TEXT,
        chat_id INT,
        date_request DATETIME,
        hotel_name TEXT
        )""")


def write_data(data: dict) -> None:
    """
    Принимает словарь с данными которые необходимо записать в БД.

    :param data: Словарь с данными.
    :return: None
    """
    with sq.connect('database/history.db') as con:
        cur = con.cursor()
        cur.execute("INSERT INTO user_search_history VALUES (?, ?, ?, ?, ?)", tuple(data.values())
                    )


def view_history(msg: dict) -> list[tuple]:
    """
    Функция получает словарь с данными чата в котором содержится id чата,
    и по нему ищет в БД записи истории поиска пользователя. Возвращает найденные записи
    в виде списка кортежей.

    :param msg: Словарь с данными чата, ID чата, имя пользователя и т.д.
    :return: Список кортежей (каждый кортеж это запись истории поиска в БД)
    """
    with sq.connect('database/history.db') as con:
        cur = con.cursor()
        # for i in cur.execute("SELECT * FROM user_search_history").fetchall():
        # await bot.message.answer(i[0], i[1], i[2], i[3], i[4])
        return cur.execute("SELECT command_name, user_request, date_request, hotel_name "
                           "FROM user_search_history "
                           "WHERE chat_id = ?", (msg['chat']['id'],)).fetchall()
