import os

from dotenv import load_dotenv, find_dotenv

from database.connect_db import sql_start

if not find_dotenv('.env'):
    exit('Переменные окружения не загружены т.к отсутствует файл .env')
else:
    load_dotenv('.env')
    sql_start()

BOT_TOKEN = os.getenv('BOT_TOKEN')
RAPID_API_KEY = os.getenv('RAPID_API_KEY')

