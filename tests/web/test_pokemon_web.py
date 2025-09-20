import pytest
import requests
import auth_data

from loguru import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Позитивный логин
def test_positive_login(browser):
    browser.get(auth_data.URL_login)

    # Ввод логина
    email_input = browser.find_element(by=By.CSS_SELECTOR, value='[class*="k_form_f_email"]')
    email_input.click()
    email_input.send_keys(auth_data.True_email)
    
    # Ввод пароля
    password_input = browser.find_element(by=By.ID, value='k_password')
    password_input.click()
    password_input.send_keys(auth_data.True_password)

    # Нажатие кнопки
    browser.find_element(by=By.CSS_SELECTOR, value='[class*="k_form_send_auth"]').click()

    # Ожидание перенаправления на главную страницу
    WebDriverWait(browser, timeout=10, poll_frequency=2).until(EC.url_to_be(auth_data.URL_main))

    # Проверка id на карточке тренера
    trainer_id = browser.find_element(by=By.CSS_SELECTOR, value='[class="header_card_trainer_id_num"]')
    assert trainer_id.text == '39589', 'Unexpected trainer id'

# Тестовые данные для негативных сценариев
CASES = [
    ('1', 'email', 'password', ['Введите корректную почту']),
    ('2', 'email', 'password', ['Неверные логин или пароль']),
    ('3', 'email', 'password', ['Введите корректную почту']),
    ('4', '', 'password', ['Введите почту']),
    ('5', 'email', '', ['Введите пароль'])
]

# Негативный логин
@pytest.mark.parametrize('case_number, email, password, alerts', CASES)
def test_negative_login(case_number, email, password, alerts, browser):
    # Пояснения для логов
    logger.info(f'CASE : {case_number}')

    browser.get(auth_data.URL_login)

    # Ввод логина
    email_input = browser.find_element(by=By.CSS_SELECTOR, value='[class*="k_form_f_email"]')
    email_input.click()
    email_input.send_keys(email)
    
    # Ввод пароля
    password_input = browser.find_element(by=By.ID, value='k_password')
    password_input.click()
    password_input.send_keys(password)

    # Нажатие кнопки "Войти"
    browser.find_element(by=By.CSS_SELECTOR, value='[class*="k_form_send_auth"]').click()

    # Ожидание появления сообщения об ошибке
    alerts_messages = WebDriverWait(browser, 10).until(
        EC.visibility_of_any_elements_located((By.CSS_SELECTOR, '[class*="auth__error"]'))
    )

    # Сбор текстов всех обнаруженных ошибок
    alerts_messages = browser.find_elements(by=By.CSS_SELECTOR, value='[class*="auth__error"]')
    
    alerts_list = []
    for element in alerts_messages: 
        alerts_list.append(element.text)
    
    # Верификация: сравнение фактических и ожидаемых ошибок
    assert alerts_list == alerts, f'Unexpected alerts. Expected: {alerts}, Actual: {alerts_list}'

# Сквозной сценарий тестирования
def test_check_api(browser, knockout, pokemon_create_body):
    browser.get(auth_data.URL_login)
    WebDriverWait(browser, timeout=10, poll_frequency=2).until(EC.url_to_be(auth_data.URL_login))

    # Ввод логина
    email_input = browser.find_element(by=By.CSS_SELECTOR, value='[class*="k_form_f_email"]')
    email_input.click()
    email_input.send_keys(auth_data.True_email)

    # Ввод пароля
    password_input = browser.find_element(by=By.ID, value='k_password')
    password_input.click()
    password_input.send_keys(auth_data.True_password)

    # Нажатие кнопки "Войти"
    browser.find_element(by=By.CSS_SELECTOR, value='[class*="k_form_send_auth"]').click()
    WebDriverWait(browser, timeout=10, poll_frequency=2).until(EC.url_to_be(auth_data.URL_main))

    # Нажатие кнопки с id тренера
    browser.find_element(by=By.CSS_SELECTOR, value='[class="header_card_trainer style_1_interactive_button_link"]').click()
    WebDriverWait(browser, timeout=10, poll_frequency=2).until(EC.url_to_be(auth_data.URL_trainer))

    # Кол-во покемонов до обновы
    # Ожидание, пока элемент будет иметь непустой текст
    WebDriverWait(browser, 10).until(
        lambda driver: driver.find_element(By.CSS_SELECTOR, '[class="total-count history-info_count"]').text.strip() != '' and
                       driver.find_element(By.CSS_SELECTOR, '[class="total-count history-info_count"]').text.strip() != '0'
    )
    
    pokemon_count_before = browser.find_element(by=By.CSS_SELECTOR, value='[class="total-count history-info_count"]')
    count_before = int(pokemon_count_before.text)

    # Создание покемона
    response_create = requests.post(url=auth_data.URL_pokemons, headers=auth_data.HEADER, json=pokemon_create_body)
    assert response_create.status_code == 201, 'Unexpected status code'
    
    # Обновить страницу
    browser.refresh()

    # Ожидание появления селектора на странице
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[class="total-count history-info_count"]'))
    )

    # Кол-во покемонов после обновы
    pokemon_count_after = browser.find_element(by=By.CSS_SELECTOR, value='[class="total-count history-info_count"]')
    count_after = int(pokemon_count_after.text)

    # Проверка, что кол-во увеличилось ровно на 1
    assert count_after - count_before == 1