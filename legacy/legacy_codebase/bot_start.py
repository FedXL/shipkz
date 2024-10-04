import requests
from utils.config import TOKEN_ASKAR
bot_token = TOKEN_ASKAR
url = f'https://api.telegram.org/bot{bot_token}/getMe'
response = requests.get(url)
if response.status_code == 200:
    print("Сервис Telegram API доступен.")
    print("Ответ сервера:")
    print(response.json())
else:
    print(f"Проблема с доступом к сервису Telegram API. Код состояния: {response.status_code}")
