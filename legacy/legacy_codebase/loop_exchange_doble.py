import os
from bs4 import BeautifulSoup
import time
import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from base.base_connectors import insert_to_base
from base.base_handlers_bot import save_exhchange_to_bd
from utils.config import orders_chat_storage, PATH_TO_CHROMEDRIVER
from utils.errors import send_message_from_bot_synch
from utils.sberbank import my_options



def get_content(url):
    options = my_options()
    service = Service(PATH_TO_CHROMEDRIVER)
    driver = webdriver.Chrome(options=options, service=service)
    try:
        driver.maximize_window()
        print('driver get url = {url{')
        driver.get(url=url)
        print('driver get url ok')
        with open('utils/save.html', 'w', encoding='utf-8') as file:
            file.write(driver.page_source)
        print('file save ok.')
    except Exception as ER:
        raise ValueError(f'Cannot get content from {url} {ER}')
    finally:
        driver.close()
        driver.quit()


def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False


def parse_soup_for_exchange(spec):
    result = []
    print('parce exchange')
    with open('utils/save.html', 'r', encoding='utf-8') as file:
        f = file.read()
        soup = BeautifulSoup(f, 'html5lib')

    match spec:
        case "profinance":
            print('start')
            usd = soup.find(id="a_29")
            usd_value = usd.text
            usd_time = soup.find(id="t_29").text
            eur = soup.find(id="a_30")
            eur_value = eur.text
            eur_time = soup.find(id="t_30").text
            result = {'eur': {'price': eur_value, "time": eur_time},'usd': {'price': usd_value,"time": usd_time}}
            print(result)

        case 'sberbank':
            print('sberbank!')
    return result


def delete_save_html():
    file_path = "utils/save.html"
    os.remove(file_path)


def save_result(result):
    print("trying to save result")
    usd = result['usd']['price']
    eur = result['eur']['price']
    today = str(result['usd']['time']) + " " + str(datetime.date.today())
    string = f"{usd}|{eur}|{today}"
    print('[INFO] starting save result', string)
    save_exhchange_to_bd(usd, eur, today)


def get__content(variant='profinance'):
    if variant == 'profinance':
        url = 'https://www.profinance.ru/chart/usdrub/'
    elif variant == 'bankiros':
        url = 'https://bankiros.ru/currency/moex/usdrub-tod'
    elif variant == 'sberbank':
        url = 'https://www.sberbank.ru/ru/quotes/currencies?tab=kurs'
    else:
        print('fail')
        return
    get_content(url)


def main(spec):
    print(f"start stealing exchange spec = {spec}")
    try:
        print('start get content')
        get__content(variant=spec)
        print('get content success')
    except Exception as ER:
        print(ER)
        value = (f"UPDATE services SET status = False, report = 'Cannot to steal content from site' WHERE service_name "
                 f"= '{spec}';")
        insert_to_base(value)
        send_message_from_bot_synch(orders_chat_storage, f'[PARSER ERROR] Не удалось вытащить курсы с  {spec}')
        raise ConnectionError('Не удалось тырить с профинанс')
    try:
        result = parse_soup_for_exchange(spec)
        save_result(result)
    except Exception as ER:
        print("[ERROR]", ER)
        value = f"UPDATE services SET status = False, report = 'Cannot to parce content' WHERE service_name = '{spec}';"
        insert_to_base(value)
        send_message_from_bot_synch(orders_chat_storage, f'[PARSER ERROR] Не удалось разобрать данные с  {spec}')
        raise ConnectionError('Не удалось разобрать данные с профинансе')
    delete_save_html()
    print('[INFO] STEALING EXCHANGE end loop ,all is good')
    value = f"UPDATE services SET status = True, report = 'All is good' WHERE service_name = '{spec}';"
    insert_to_base(value)


def main_exchange_doble():
    while True:
        print('[EXCHANGE]')
        try:
            main(spec='profinance')
        except:
            send_message_from_bot_synch(orders_chat_storage, '[PARSER ] Запускаю резервный с bankiros.]')
            time.sleep(120)
            try:
                main(spec='bankiros')
                send_message_from_bot_synch(orders_chat_storage, '[PARSER]  bankiros success]')
            except:
                pass

        time.sleep(3723)


