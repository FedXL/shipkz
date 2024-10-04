import logging
import time
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from utils.selenium_driver import selenium_driver


def extract_money(login_value, password_value):
    print("[INFO] start to parce money")
    logging.debug("[INFO] start to parce money")
    driver = selenium_driver()
    driver.maximize_window()

    driver.get("https://tradeinn.com/")
    print("[INFO] getting page ... ok")
    logging.debug('[INFO] success parsing main page ... ok')
    time.sleep(8)
    driver.save_screenshot('start_page.jpg')
    try:
        #choise delivery country and language
        language_button = driver.find_element(By.ID, "div_cargar_paisos")
        logging.debug('[INFO] find delivery choice button ... ok')
        language_button.click()
        time.sleep(3)
        logging.debug('[INFO] click delivery choice button ... ok')
        field_to_input = driver.find_element(By.ID, "js-buscador_paises")
        field_to_input.send_keys('Russian')
        logging.debug('[INFO] find input delivery field key and send Russian ... ok')
        time.sleep(3)
        actions = ActionChains(driver)
        actions.move_to_element(field_to_input).move_by_offset(0, 40).click().perform()
        logging.debug('[INFO] click 0,40 offset (Delivery country Russian was chosen ... ok')
        time.sleep(3)
        # make english language
        element = driver.find_elements(By.CSS_SELECTOR,'.supnav-menu.pointer')

        for num, i in enumerate(element,start=1):
            print('----------------------')
            print(i.get_attribute('innerHTML'))
            if num == 2:
                i.find_element(By.TAG_NAME,'img').click()
        time.sleep(2)
        # create english choice
        language_list = driver.find_element(By.ID, "js-list_idiomas")
        print(language_list.get_attribute('innerHTML'))
        lilist = language_list.find_elements(By.TAG_NAME,'li')
        for li in lilist:
            print('|||||||')
            print(li.get_attribute('innerHTML'))

            if 'English' in li.get_attribute('innerHTML'):
                print('find english in li ')
                print(li.get_attribute('innerHTML'))
                a = li.find_element(By.TAG_NAME,'a')
                print('get a')
                print(a.get_attribute('innerHTML'))
                print('click a')
                a.click()
                break
        login_button = driver.find_element(By.CLASS_NAME, "txt-base.txt-base__gris.visible_mobile")
        print('[INFO] find input login button ... ok')
        logging.debug('[INFO] find input login button ... ok')
        login_button.click()
        print('[INFO] click ... ok')
        time.sleep(4)
        login = driver.find_element(By.ID, 'email_login')
        print('[INFO] find login input ... ok')
        logging.debug('[INFO] find login input ... ok')
        password = driver.find_element(By.ID, 'pass_login')
        print('[INFO] find password input ... ok')
        logging.debug('[INFO] find password input ... ok')
        time.sleep(2)
        login.send_keys(login_value)
        print('[INFO] password input ... ok')
        logging.debug('[INFO] password input ... ok')
        time.sleep(2)
        password.send_keys(password_value)
        print('[INFO] login input ... ok')
        logging.debug('[INFO] login input ... ok')
        time.sleep(4)
        form_login = driver.find_element(By.ID, "js-login_header")
        button_enter = form_login.find_element(By.CLASS_NAME,'btn-shop__primary')
        button_enter.click()
        print('[INFO] login click ... ok')
        logging.debug('[INFO] login click ... ok')
        time.sleep(4)
        form_login = driver.find_element(By.ID, "js-mensaje_login_header")
        class_form_login = form_login.get_attribute("class")
        if '-novisibility' in class_form_login:
            print('good login')
        else:
            print('incorrect password')
            return 'Incorrect password'
        # basket way
        basket_btw = driver.find_element(By.ID, "no-menu__on3")
        print('[INFO] find basked button ... ok')
        logging.debug('[INFO] find basked button ... ok')
        time.sleep(2)
        basket_a = basket_btw.find_element(By.TAG_NAME,'a')
        print(basket_a.get_attribute('innerHTML'))
        basket_a.click()
        print('[INFO] baked click ... ok')
        logging.debug('[INFO] click to busked button ... ok')
        time.sleep(2)
        total = driver.find_element(By.ID, "total_price")
        print('[INFO] find money element ... ok')
        logging.debug('[INFO] find money element ... ok')
        money =total.text
        logging.debug('[INFO] extract money price ... ok')
        print('[INFO]', money)
        return money
    except Exception as ER:
        print("[ERROR] ", ER)
        logging.error(f"[ERROR] {ER}")
        driver.quit()
        return f"ERROR"
    finally:
        driver.quit()


