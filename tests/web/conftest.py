import pytest
import requests
import auth_data
import random
import string

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Фикстура Открытие браузера
@pytest.fixture(scope="function")
def browser():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    #chrome_options.add_argument("start-maximized") # открываем на полный экран
    chrome_options.add_argument("--disable-infobars") # отключаем инфо сообщения
    chrome_options.add_argument("--disable-extensions") # отключаем расширения
    chrome_options.add_argument("--disable-gpu") # отключаем использование gpu
    chrome_options.add_argument("--disable-dev-shm-usage") # лимитируем ресурсы
    chrome_options.add_argument("--headless") # спец. режим "без браузера"

    service = Service()
    # запускаем браузер с указанными выше настройками
    driver = webdriver.Chrome(service=service, options=chrome_options)

    yield driver
    driver.quit()

# Фикстура для подготовки тестового окружения
@pytest.fixture(scope="function")
def knockout():
    pokemons = requests.get(url=auth_data.URL_pokemons, params=auth_data.Trainer_id)
    for pokemon in pokemons.json()['data']:
        if pokemon['status'] != 0:
            requests.post(url=auth_data.URL_knockout, headers=auth_data.HEADER, json={"pokemon_id" : pokemon['id']})

# Фикстура для создания покемона
@pytest.fixture(scope="function")
def pokemon_create_body():
    russian_letters = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
    all_characters = string.ascii_letters + russian_letters
    random_name = ''.join(random.choice(all_characters) for _ in range(12))
    
    return {
    "name": random_name,
    "photo_id": 12
    }
    
    