import datetime
from typing import Set, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from base.good_db_handlers import extract_users_by_orders, extract_order_status_info_by_order_id
from handlers.chat.sender import send_notification_text_to_web_user, send_notification_text_to_tele_user
from logs.logs import my_logger
from module_7.bot.bot_handlers import update_meeting_message_telegram, update_meeting_message_web
from utils.config import async_engine_bot, BUYER_STATUSES
from utils.utils_lite import quot_replacer
from aiogram.types import Message as AioMessage
from aiogram.types import User as AioUser
from aiogram.types import Chat as AioChat


def create_aiogram_message(user_id, chat_id, text):
    user = AioUser(id=123456789, is_bot=False, first_name="Test User")
    chat = AioChat(id=123456789, type="private")
    message = AioMessage(message_id=1,
                         from_user=user,
                         date=0,
                         chat=chat,
                         text=text)
    return message


async def send_messages_to_users(data: dict, text, session, prefix_to_text=False):
    """send one text message to users by orders"""

    safe_text = quot_replacer(text)
    time = datetime.datetime.now()
    tele_orders = data.get('tele_users')
    web_orders = data.get('web_users')
    tele_orders_id = {order.user_id for order in tele_orders} if tele_orders else None
    web_orders_id = {order.user_id for order in web_orders} if web_orders else None
    report = dict()

    if web_orders_id:
        for user in web_orders_id:
            try:
                await send_notification_text_to_web_user(session_chat=session,
                                                         manager='Askar',
                                                         user_id=user,
                                                         text=safe_text
                                                         )
                status = 'success'
                details = {'type': 'web'}
            except Exception as er:
                status = 'error'
                details = {"details": str(er)}
            finally:
                report[user] = {'result': status, 'details': details}
    if tele_orders_id:
        if prefix_to_text:
            text = f'[{prefix_to_text}] \n' + text
        for user in tele_orders_id:
            try:
                response = await send_notification_text_to_tele_user(session=session,
                                                                     user_id=user,
                                                                     text=safe_text,
                                                                     time=time)
                status = 'success'
                details = {'type': 'telegram', 'message_id': response.message_id}
            except Exception as er:
                status = 'error'
                details = {"details": str(er)}
            finally:
                report[user] = {'result': status, 'details': details}
    report['text'] = text
    data['report'] = report
    return data


"""
EXAMPLE OF ORDER:
{   'id': 2568,
    'web_user': 1,
    'time': '2024-02-25 13:47',
     'body': '{"country":"Japan","items":{"1":{"url":"https://www.bike-components.de/de/Specialized/Tarmac-SL7-Expert-Carbon-Rennrad-Modell-2023-p91412/?v=134767-satin-carbon-white","amount":2,"comment":"test"}},"username":"admin","phone_number":"8999 999 99 99","cdek_adress":"Где то непонятно где"}',
     'order_type': 'WEB_ORDER',
     'status': 'PAID',
     'order_id': 2568,
     'is_forwarder_way': True,
     'relative_price': '33 доллар',
     'shop': 'ebay.com',
     'store_order_number': '',
     'trek': '012313123123ad',
     'cdek': None,
     'shopped': '2024-02-28 05:58',
     'post_service': 'dhl express',
     'host_country': 'KAZAKHSTAN',
     'arrived_to_forwarder': '2024-02-27 06:21',
     'send_to_host_country': '2024-02-27 06:29',
     'arrived_to_host_country': '2024-02-27 06:29',
     'received_in_host_country': None,
     'send_to_ru': None,
     'received_by_client': None}
     
{'id': 2449,
    'telegram_user': 716336613,
    'time': '2024-02-04 12:29',
    'body': '[\'\'shop:  <code>bike inn</code>\'\', \'\'<a href="yandex.ru">ссылка 1</a> :  работай пожалуйста\'\']',
    'order_type': 'KAZ_ORDER_LINKS', 'status': 'PAID', 'order_id': 2449, 'is_forwarder_way': True,
    'relative_price': '33 доллар',
    'shop': 'ebay.com',
    'store_order_number': '',
    'trek': None, 'cdek': None,
    'shopped': '2024-02-28 05:58',
    'post_service': None,
    'host_country': 'KAZAKHSTAN',
    'arrived_to_forwarder': None,
    'send_to_host_country': None,
    'arrived_to_host_country': None,
    'received_in_host_country': None,
    'send_to_ru': None,
    'received_by_client': None }
"""


async def send_to_buyer_instructions(data: Set[Tuple[int, str]],orders) -> dict:
    for item in data:
        buyer = item[0]
        text = item[1] + "  " + f"Номера заказов: {str(orders)}."
    async with AsyncSession(async_engine_bot) as session:
        async with session.begin():
            try:
                message = await send_notification_text_to_tele_user(session=session,
                                                                user_id=buyer,
                                                                text=text,
                                                                time=datetime.datetime.now())
                report = {'message_id': message.message_id, 'result': 'success', 'send_to': message.chat.id}
            except Exception as ER:
                my_logger.warning(f'Error in sending message to buyer {buyer} because:', ER.args)
                report = {'result': 'error', 'details': str(ER)}

    return report


async def send_one_notification_by_order(order: int, status: str):
    async with AsyncSession(async_engine_bot) as session:
        async with session.begin():
            order_and_status_dict, comment = await extract_order_status_info_by_order_id(session=session,
                                                                                         order_id=order)
            if not order_and_status_dict:
                return False, comment
            user_text, buyer_info = await text_status_generator(data=order_and_status_dict,
                                                                status=status)
            if not user_text:
                return False, 'Error in text'
            report, comment = await send_notification_to_user(data=order_and_status_dict,
                                                              user_text=user_text,
                                                              session=session)
            if not report:
                return False, comment
            report['buyer_info'] = buyer_info
    return report, False


async def send_notification_to_user(data,
                                    user_text,
                                    session) -> tuple[dict, str]:
    """send notification to users by orders"""
    time = datetime.datetime.now()
    user_text = quot_replacer(user_text)
    error = data.get('error')
    if error:
        return False, 'Error in data'
    try:
        if data.get('web_user'):
            user = 'web user'
            user_id = data.get('web_user')
            await send_notification_text_to_web_user(session_chat=session,
                                                     manager='Askar',
                                                     user_id=user_id,
                                                     text=user_text)
            status = 'success'
            details = {'type': 'web'}
        elif data.get('telegram_user'):
            user = 'telegram user'
            user_id = data.get('telegram_user')
            response = await send_notification_text_to_tele_user(session=session,
                                                                 user_id=user_id,
                                                                 text=user_text,
                                                                 time=time)
            status = 'success'
            details = {'type': 'telegram', 'message_id': response.message_id}
    except Exception as er:
        my_logger.warning(f'CANT to SEND notification  to {user} {user_id} because:', er.args)
        status = 'error'
        details = str(er)
    finally:
        report = {'user': user_id, 'result': status, 'details': details, 'text': user_text}
    await session.flush()
    return report, False


async def open_chats_by_orders(orders: list):
    async with AsyncSession(async_engine_bot) as session:
        async with session.begin():
            orders_dict, comment = await extract_users_by_orders(session=session, orders_list=orders)
            web_users = orders_dict.get('web_users')
            tele_users = orders_dict.get('tele_users')

            if tele_users:
                tele_users_id = set()
                for user in tele_users:
                    tele_id = user.user_id
                    tele_users_id.add(tele_id)
                for user in tele_users_id:
                    await update_meeting_message_telegram(user)

            if web_users:
                web_users_id = set()
                for user in web_users:
                    web_id = user.user_id
                    web_users_id.add(web_id)
                for user in web_users_id:
                    await update_meeting_message_web(user)


async def send_messages_by_orders(orders: list, text: str):
    """same as sender"""
    async with AsyncSession(async_engine_bot) as session:
        async with session.begin():
            print('PHASE 1')
            orders_dict, comment = await extract_users_by_orders(session=session, orders_list=orders)
            print(orders_dict, comment)
            if not orders_dict:
                return False, comment
            print('PHASE 2')
            print(orders_dict, comment)
            report_and_orders = await send_messages_to_users(data=orders_dict, text=text, session=session)
    return report_and_orders, False


async def text_status_generator(data: dict, status: str) -> tuple[str, tuple[int, str]]:
    """
    EXAMPLE OF ORDER:
    {   'id': 2568,
        'web_user': 1,
        'time': '2024-02-25 13:47',
         'body': '{"country":"Japan","items":{"1":{"url":"https://www.bike-components.de/de/Specialized/Tarmac-SL7-Expert-Carbon-Rennrad-Modell-2023-p91412/?v=134767-satin-carbon-white","amount":2,"comment":"test"}},"username":"admin","phone_number":"8999 999 99 99","cdek_adress":"Где то непонятно где"}',
         'order_type': 'WEB_ORDER',
         'status': 'PAID',
         'order_id': 2568,
         'is_forwarder_way': True,
         'relative_price': '33 доллар',
         'shop': 'ebay.com',
         'store_order_number': '',
         'trek': '012313123123ad',
         'cdek': None,
         'shopped': '2024-02-28 05:58',
         'post_service': 'dhl express',
         'host_country': 'KAZAKHSTAN',
         'arrived_to_forwarder': '2024-02-27 06:21',
         'send_to_host_country': '2024-02-27 06:29',
         'arrived_to_host_country': '2024-02-27 06:29',
         'received_in_host_country': None,
         'send_to_ru': None,
         'received_by_client': None}
    """
    print('[TEXT GENERATOR]', data)

    host_county = data.get('host_country')
    if host_county == 'KAZAKHSTAN':
        host_county = 'Казахстан'
    elif host_county == 'KYRGYZSTAN':
        host_county = 'Кыргызстан'
    buyer_text = None
    match status:
        case "PAID":
            user_text = f"Ваш заказ выкуплен в магазине. Номер заказа: {data['id']}. Магазин: {data['shop']}."
        case "ARRIVED_AT_FORWARDER_WAREHOUSE":
            user_text = f"Ваш заказ прибыл на склад форвардера. Номер заказа: {data['id']}."
        case "SENT_TO_HOST_COUNTRY":
            user_text = (f"Ваш заказ отправлен в {host_county}. Номер заказа: {data['id']}."
                         f" Трек: {data['trek']}. Почтовый сервис: {data['post_service']}. ")
            buyer_text = (f"Заказ отправлен в {host_county}. Трек: {data['trek']}. "
                          f"Почтовый сервис: {data['post_service']}. Вознаграждение составит: {data['buyer_reward']}.")
        case "ARRIVED_IN_HOST_COUNTRY":
            user_text = f"Ваш заказ прибыл на территорию {host_county}. Номер заказа: {data['id']}."
            buyer_text = (f"Лови посылку. Заказ уже в {host_county}. Трек: {data['trek']}. "
                          f"Почтовый сервис: {data['post_service']}. Вознаграждение составит: {data['buyer_reward']}.")
        case "RECEIVED_IN_HOST_COUNTRY":
            user_text = f"Ваш заказ получен в {host_county}е. Номер заказа: {data['id']}."
            buyer_text = f"Отлично. Особые инструкции:  {data.get('buyer_instructions')}"
        case "SENT_TO_RUSSIA":
            user_text = f"Ваш заказ отправлен в Россию. Номер заказа: {data['id']}. Номер СДЕК: {data['cdek']}."
        case "GET_BY_CLIENT":
            user_text = (f"Мы рады, что вы получили заказ: {data['id']}. Подарите нам видео распаковки"
                         f" посылки, и получите скидку 1000 руб. на следующий заказ. Отзыв можно оставить в чате нашего"
                         f" телеграмм-канала @shipkz_discussing.")
        case _:
            return False, False
    for_buyer_send = (
        data['buyer'], buyer_text)  # костыль конечно. Но хотя бы мы будем знать что все ордера на одного баера записаны
    return user_text, for_buyer_send
