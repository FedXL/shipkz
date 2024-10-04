import asyncio
import time

from handlers.email_sender.email_sender import execute_email_tasks
from utils.config import orders_chat_storage
from utils.errors import send_message_from_bot_synch


def main():
    try:
        while True:
            task = execute_email_tasks()
            time.sleep(60)
    except Exception as ER:
        print(ER)
        send_message_from_bot_synch(orders_chat_storage,
                                    f'[EMAIL SENDER ERROR] Почтовый модуль помер. Требуется ручное вмешательство  {str(ER)}')
        time.sleep(60 * 60)


if __name__ == '__main__':
    main()
