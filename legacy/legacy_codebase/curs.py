import requests
import time
from bs4 import BeautifulSoup
from base.base_handlers_bot import save_exhchange_to_bd
from utils.config import orders_chat_storage
from utils.errors import send_message_from_bot_synch


def fetch_html_page_with_retries(url, max_retries=3, backoff_factor=1):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'DNT': '1',
        'Connection': 'close'
    }
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.text
            else:
                return "Failed to retrieve the page with status code: {}".format(response.status_code)
        except requests.exceptions.ConnectionError as e:
            print(f"Attempt {attempt + 1} of {max_retries} failed: {e}")
            time.sleep(backoff_factor * (2 ** attempt))  # Exponential backoff
    return "Failed to retrieve the page after {} retries".format(max_retries)


def get_CB_curs():
    url = "https://www.profinance.ru/"

    html_content = fetch_html_page_with_retries(url)

    if html_content:
        soup = BeautifulSoup(html_content, "html.parser")
        cur_trs = soup.select('tr.curs')
        for num, tr in enumerate(cur_trs):
            tdsss = tr.select('td')
            if num == 0:
                day1 = tdsss[1].get_text(strip=True)
                day2 = tdsss[2].get_text(strip=True)
            if num == 1:
                usd_1 = tdsss[1].get_text(strip=True)
                usd_2 = tdsss[2].get_text(strip=True)
            if num == 2:
                eur_1 = tdsss[1].get_text(strip=True)
                eur_2 = tdsss[2].get_text(strip=True)
        result = {'day1': day1, 'day2': day2, 'usd_1': usd_1, 'usd_2': usd_2, 'eur_1': eur_1, 'eur_2': eur_2}
        return result
    else:
        print("Failed to fetch the HTML content")


def main():
    while True:
        try:
            result = get_CB_curs()
        except:
            send_message_from_bot_synch(orders_chat_storage, '[PARSER] cant to parse data from profinance')
            return
        try:
            save_exhchange_to_bd(result['usd_1'], result['eur_1'], result['day1'])
        except:
            send_message_from_bot_synch(orders_chat_storage, '[PARSER] cant to save curs to db')
            return
        time.sleep(60 * 35)


if __name__ == "__main__":
    main()
