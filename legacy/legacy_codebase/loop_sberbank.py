import asyncio
from utils.sberbank import periodic_task, update_exchange_data


def main_sberbank():
    print('[START sberbank!]')
    loop = asyncio.get_event_loop()
    loop.create_task(periodic_task(7200, update_exchange_data))
    loop.run_forever()


if __name__ == "__main__":
    main_sberbank()
