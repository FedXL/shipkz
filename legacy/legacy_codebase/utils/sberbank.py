import asyncio
import logging
import time
from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from base.good_db_handlers import update_sberbank_exchange
from utils.config import orders_chat_storage, PATH_TO_CHROMEDRIVER
from utils.errors import send_message_from_bot


def my_options():
    options = Options()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-insecure-localhost')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-automation')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/58.0.3029.110 Safari/537.36")
    options.add_argument("--window-size=1920,1080")
    options.add_argument('--incognito')
    return options


def parce_sberbank():
    print('START foo')
    exchange_rates = {}
    try:
        options = my_options()
        service = Service(PATH_TO_CHROMEDRIVER)
        driver = webdriver.Chrome(options=options, service=service)
        url = "http://www.sberbank.ru/ru/quotes/currencies?tab=kurs"
        wait = WebDriverWait(driver, 60)
        driver.get(url)
        driver.save_screenshot('sberbank_start.jpg')
        for i in range(10):
            print(10 - i)
            time.sleep(1)
        driver.execute_script("window.scrollBy(0, 150);")
        driver.save_screenshot('sberbank_start2.jpg')
        component0 = driver.find_element(By.ID, 'rates-form-nova-card')
        print('[INFO]component0')
        component = component0.find_element(By.CLASS_NAME, 'rfn-cards-selector__main-wrap')
        print('[INFO]component')
        table = component.find_element(By.CLASS_NAME, 'rfn-table')
        print('[INFO]table')
        print(table.get_attribute('innerHTML'))
        parent_elements = table.find_elements(By.CLASS_NAME, 'rfn-table-row__price.rfn-table-row__price_main')
        for i in parent_elements:
            print('--------')
            print(i.get_attribute('innerHTML'))
        driver.save_screenshot('sberbank2_d.jpg')
        if parent_elements:
            parent_elements.pop(0)
            money_list = []
            for num, parent_element in enumerate(parent_elements):
                money = parent_element.find_elements(By.CLASS_NAME, 'rfn-table-row__col')
                money.pop(0)
                for num, money_element in enumerate(money, start=1):
                    print(money_element.get_attribute('innerHTML'))
                    price = money_element.text
                    exchange_rate = float(price.replace(',', '.'))
                    money_list.append(exchange_rate)
            data_text = table.find_element(By.CLASS_NAME, 'rfn-table__footer').text
            exchange_rates = {
                "USD": {"sell": money_list[0], "buy": money_list[1]},
                "EUR": {"sell": money_list[2], "buy": money_list[3]},
                "DATA": data_text
            }
            print(exchange_rates)
            return exchange_rates
        else:
            raise NoSuchElementException("No elements found")

    except TimeoutException as e:
        logging.error("Timeout occurred: %s", e)
    except Exception as e:
        logging.error("An error occurred: %s", e)
    finally:
        driver.quit()


async def update_exchange_data():
    try:
        data = parce_sberbank()
        if data:
            await update_sberbank_exchange(data)
        else:
            await send_message_from_bot(orders_chat_storage, 'Сбербанк сдох')
    except Exception as e:
        logging.error("Failed to update data: %s", e)


async def periodic_task(interval, func):
    while True:
        try:
            print('[SBERBANK]')
            await func()
        except Exception as e:
            logging.error(f"Ошибка при выполнении задачи: {e}")
            await asyncio.sleep(60 * 60 * 3)
        await asyncio.sleep(interval)
