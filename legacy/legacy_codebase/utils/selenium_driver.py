from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import platform
from utils.config import PATH_TO_CHROMEDRIVER


def create_driver_linux():
    path_to_chromedriver = PATH_TO_CHROMEDRIVER
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                "Chrome/58.0.3029.110 Safari/537.3")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--window-size=1920,1080")
    service = Service(path_to_chromedriver)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def create_driver_windows():
    win_chrome = "C:\\Users\\Asus\\PycharmProjects\\askar_bot\\chrome-win32\\chrome.exe"
    win_chromedriver = "C:\\Users\\Asus\\PycharmProjects\\askar_bot\\chromedriver-win32\\chromedriver.exe"
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = win_chrome
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                "Chrome/58.0.3029.110 Safari/537.3")
    chrome_options.add_argument("--ignore-certificate-errors")
    service = Service(win_chromedriver)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def selenium_driver():
    """Function to create selenium driver"""
    os_name = platform.system()
    if os_name == 'Windows':
        print('run win driver')
        return create_driver_windows()
    elif os_name == 'Linux':
        print('run linux driver')
        return create_driver_linux()
    else:
        raise Exception('Unknown OS')


