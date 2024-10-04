import datetime
import re
from enum import Enum
from functools import reduce
from typing import Tuple, List, Dict, Set
from sqlalchemy import update, select, desc, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from base.models import Message, Photo, Document, ParceTask, User, Order, OrderStatus, OrderStatusInfo, WebUser, \
    WebMessage, WebPhoto, WebDoc, Exchange, WebUserModel, WebUserMetaData, EmailTask, EmailTaskStatus
from logs.bot_logger import bot_logger
from logs.logs import my_logger
from utils.config import async_engine_bot
from utils.texts import HEADER_TEXT


async def add_parce_task(order_id, login, psw, task_type):
    async with AsyncSession(async_engine_bot) as session:
        async with session.begin():
            task = ParceTask(order_id=order_id, login=login, password=psw, type=task_type)
            session.add(task)
            await session.commit()
            bot_logger.debug('success')


async def get_sberbank_exchange():
    async with AsyncSession(async_engine_bot) as session:
        async with session.begin():
            stmt = select(Exchange.valuta, Exchange.price, Exchange.data).where(Exchange.valuta.in_(['sber_usd',
                                                                                                     'sber_euro',
                                                                                                     'usd', 'eur']))
            result = await session.execute(stmt)
            values = result.fetchall()
            exchange_data = {row.valuta: {"price": row.price, "data": row.data} for row in values}
            return exchange_data


async def update_sberbank_exchange(data):
    today = data['DATA']
    usd = data['USD']['buy']
    eur = data['EUR']['buy']
    async with AsyncSession(async_engine_bot) as session:
        async with session.begin():
            stmt = update(Exchange).values(price=usd, data=today).where(Exchange.valuta == 'sber_usd')
            await session.execute(stmt)
            stmt = update(Exchange).values(price=eur, data=today).where(Exchange.valuta == 'sber_euro')
            await session.execute(stmt)


async def add_photo_to_db_(session: AsyncSession, user_id_: int, photo_id: str, prefix: str,
                           is_answer: bool, message_id: int = None):
    print('[START ADD PHOTO TO DB bot]')
    if message_id:
        new_message = Message(is_answer=is_answer,
                              storage_id=user_id_,
                              message_id=message_id,
                              time=datetime.datetime.now())
    else:
        new_message = Message(is_answer=is_answer, storage_id=user_id_)
    print('[PHOTO] ', new_message)
    session.add(new_message)
    await session.flush()
    message_id_in_db: int = new_message.id
    session.add(Photo(file_id=photo_id, message_id=message_id_in_db))
    text = prefix + str(message_id_in_db)
    print('[TEXT of photo]')
    await session.execute(update(Message).where(Message.id == message_id_in_db).values(message_body=text))
    await session.flush()
    return text


async def add_document_to_db_(session: AsyncSession,
                              prefix: str,
                              is_answer: bool,
                              user_id: int,
                              document_id: str,
                              message_id: int = None
                              ):
    time = datetime.datetime.now()
    my_logger.debug('start')
    if message_id:
        new_message = Message(is_answer=is_answer,
                              storage_id=user_id,
                              message_id=message_id,
                              time=datetime.datetime.now())
    else:
        new_message = Message(is_answer=is_answer, storage_id=user_id)
    session.add(new_message)
    await session.flush()
    message_id_in_db: int = new_message.id
    new_doc = Document(document_id=document_id, message_id=message_id_in_db)
    session.add(new_doc)
    text = prefix + str(message_id_in_db)
    await session.execute(update(Message).where(Message.id == message_id_in_db).values(message_body=text))
    await session.flush()
    return text


async def extract_order_status_info_by_order_id(session, order_id: int):
    try:
        order_id = int(order_id)
    except Exception:
        return False, 'Invalid order id'
    stmt = select(Order).where(Order.id == order_id)
    result = await session.execute(stmt)
    order = result.scalar_one_or_none()
    if not order:
        return False, 'No such order in DB'
    order_dict = order.to_dict()
    stmt = select(OrderStatusInfo).where(OrderStatusInfo.order_id == order_id)
    result = await session.execute(stmt)
    order_status_info = result.scalar_one_or_none()
    if not order_status_info:
        return False, 'No order_status_info in DB'
    else:
        order_status_info_dict = order_status_info.to_dict()
        result_dict = {**order_dict, **order_status_info_dict}
        print('[STATUS RESULT DICT]', result_dict)
    return result_dict, "success"


async def extract_users_by_orders(session, orders_list: list) -> Tuple:
    """:return report | False , False | comment"""
    rubbish = []
    valid_orders = []
    for order in orders_list:
        try:
            order_id = int(order)
            valid_orders.append(order_id)
        except Exception:
            rubbish.append(order)
    stmt = select(Order).where(Order.id.in_(valid_orders))
    print(stmt)
    try:
        result = await session.execute(stmt)
        orders = result.scalars()
        if not orders:
            return False, 'NO orders in DB'
        report = {}
        full_report = {}
        web_users = []
        tele_users = []
        for order in orders:
            if order.client:
                report[order.id] = {'order_type': 'telegram', 'user': order.client}
                tele_users.append(order.client)
            elif order.web_user:
                report[order.id] = {'order_type': 'web', 'user': order.web_user}
                web_users.append(order.web_user)
        if rubbish:
            for item in rubbish:
                report[item] = {'error': 'format of order'}

        if len(web_users) > 0:
            stmt = select(WebUser).where(WebUser.user_id.in_(web_users))
            result = await session.execute(stmt)
            web_users_models = result.scalars()
            full_report['web_users'] = web_users_models

        if len(tele_users) > 0:
            stmt = select(User).where(User.user_id.in_(tele_users))
            result = await session.execute(stmt)
            tele_users_models = result.scalars()
            full_report['tele_users'] = tele_users_models
        full_report['orders'] = report
    except Exception as er:
        my_logger.error(f'We have a problem {er}')
        return False, 'Error in extrac users'
    return full_report, False


async def have_read_the_message(target_id):
    assert isinstance(target_id, int)
    async with AsyncSession(async_engine_bot) as session:
        async with session.begin():
            stmt = update(WebMessage).where(WebMessage.id == target_id).values(is_read=True)
            print(f"read now {target_id}")
            await session.execute(stmt)


async def get_all_unread_message_count_by_web_user(web_user_id, session=None):
    assert isinstance(web_user_id, int)
    if session:
        stmt = select(func.count()).filter(WebMessage.user == web_user_id, WebMessage.is_read == False)
        result = await session.execute(stmt)
        count = result.scalar()
        return count
    else:
        async with AsyncSession(async_engine_bot) as session:
            async with session.begin():
                stmt = select(func.count()).filter(WebMessage.user == web_user_id, WebMessage.is_read == False)
                result = await session.execute(stmt)
                count = result.scalar()
                return count


async def save_text_message_to_db(text: str, user_web_id: int, is_answer: bool,
                                  session: AsyncSession, message_type='text') -> int:
    my_logger.debug('start ')
    message = WebMessage(message_body=text,
                         is_answer=is_answer,
                         user=user_web_id,
                         message_type=message_type)
    session.add(message)
    my_logger.debug(message)
    await session.flush()
    id = message.id
    my_logger.debug(f'end with success message id {id}')
    return id


async def get_messages_from_base_last_5_g(user_id: int, session: AsyncSession):
    stmt = select(Message.is_answer, Message.message_body).where(Message.storage_id == user_id).order_by(
        desc(Message.id)).limit(5)
    result = await session.execute(stmt)
    rows = result.fetchall()
    return rows


async def get_all_teleusers():
    async with AsyncSession(async_engine_bot) as session:
        stmt = select(User.user_id).order_by(desc(User.user_id))
        result = await session.execute(stmt)
        users = result.scalars().all()
        return users


async def get_messages_from_web_db(user_id: int, session: AsyncSession):
    stmt = select(WebMessage.is_answer, WebMessage.message_body, WebMessage.is_read).where(
        WebMessage.user == user_id).order_by(
        desc(WebMessage.id)).limit(5)
    result = await session.execute(stmt)
    rows = result.fetchall()
    return rows


async def get_web_user_id_by_name(username: str) -> int:
    async with AsyncSession(async_engine_bot) as session:
        async with session.begin():
            stmt = select(WebUser.user_id).where(WebUser.web_username == username)
            result_proxy = await session.execute(stmt)
            result = result_proxy.scalar()
            return result


async def get_web_username_by_user_id(user_id: int) -> str:
    async with AsyncSession(async_engine_bot) as session:
        async with session.begin():
            user_id = int(user_id)
            stmt = select(WebUser.web_username).where(WebUser.user_id == user_id)
            result_proxy = await session.execute(stmt)
            result = result_proxy.scalar()
            return result


async def get_web_user_info(user_id: int) -> WebUserModel:
    async with AsyncSession(async_engine_bot) as session:
        async with session.begin():
            user_id = int(user_id)
            stmt = select(WebUser).where(WebUser.user_id == user_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            user = user.to_model()
            return user


async def delete_orders_by_webusername(username: str, order_id: int) -> Tuple[bool, str]:
    try:
        async with AsyncSession(async_engine_bot) as session:
            async with session.begin():
                stmt = select(WebUser).where(WebUser.web_username == username)
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()
                if user:
                    print('find_user SUCCESS')
                    user_id = user.user_id
                else:
                    return False, f'[WARNING] SECURITY ERROR:  Cant to find user in (delete_orders_by_webusername) {username}'
                stmt = select(Order).where(Order.web_user == user_id)
                result = await session.execute(stmt)
                orders = result.scalars().all()
                if orders:
                    print('find orders SUCCESS')
                else:
                    return False, f'[WARNING] SECURITY ERROR:  Cant to find orders in (delete_orders_by_webusername) {username}'
                for order in orders:
                    print('iter order')
                    if order.id == order_id:
                        target = order
                        print(f'find order with id {order_id}')
                        break
                    target = None
                if target:
                    stmt = delete(OrderStatus).where(OrderStatus.order_id == target.id)
                    stmt2 = delete(OrderStatusInfo).where(OrderStatusInfo.order_id == target.id)
                    try:
                        await session.execute(stmt)
                        await session.execute(stmt2)
                        await session.delete(target)
                        return True, f'Success deleted order {order_id}'
                    except Exception as error:
                        return False, f"Error in db {error}"
                else:
                    return False, (f'[WARNING] SECURITY ERROR: That webserver: {username} '
                                   f'Trying to delete order from another user and token was valid')
    except Exception as ER:
        print('Unexpected Error in delete_orders_by_webusername', ER)
        return False, 'unexpected ERROR'


async def save_photo_message_to_web_db(photo_path: str, photo_command, user_id: int, is_answer: bool,
                                       session: AsyncSession):
    new_message = WebMessage(message_body=photo_command,
                             is_answer=is_answer,
                             user=user_id,
                             message_type='photo')
    session.add(new_message)
    await session.flush()
    message_id = new_message.id
    photo = WebPhoto(photo_path=photo_path,
                     message_id=message_id)
    session.add(photo)
    await session.flush()
    photo_id = photo.id
    return message_id


async def save_document_message_to_web_db(document_path: str,
                                          doc_command,
                                          user_id: int,
                                          is_answer: bool,
                                          session: AsyncSession):
    new_message = WebMessage(message_body=doc_command,
                             is_answer=is_answer,
                             user=user_id,
                             message_type='document')

    session.add(new_message)
    await session.flush()
    message_id = new_message.id

    document = WebDoc(doc_path=document_path,
                      message_id=message_id)

    session.add(document)
    await session.flush()
    document = document.id
    return message_id


async def add_user_to_base_good(user_id, user_first_name, user_second_name, username, is_kazakhstan=True):
    bot_logger.debug(f'try to save user with {user_id}')
    async with AsyncSession(async_engine_bot) as session:
        async with session.begin():
            user = await session.get(User, user_id)
            if user:
                bot_logger.debug(f'user is already in database: {user_id}')
                income = is_kazakhstan
                in_db = user.is_kazakhstan
                if income == in_db:
                    return
                else:
                    stmt = update(User).where(User.user_id == user_id).values(is_kazakhstan=is_kazakhstan)
                    await session.execute(stmt)
                    return

            user = User(user_id=user_id,
                        user_name=user_first_name,
                        user_second_name=user_second_name,
                        tele_username=username,
                        is_kazakhstan=is_kazakhstan)
            try:
                session.add(user)
                await session.commit()
                bot_logger.debug(f'successfully add new user {user_id}')
            except Exception as er:
                bot_logger.error(f"error when try to save new user {er}")


class OrderType(Enum):
    tradeinn = "TRADEINN"
    kaz_links = 'KAZ_ORDER_LINKS'
    kaz_cabinet = "KAZ_ORDER_CABINET"
    web_order = "WEB_ORDER"


async def create_order_bot(client: int,
                           order_type: OrderType,
                           order_body: str):
    async with AsyncSession(async_engine_bot) as session:
        async with session.begin():
            new_order = Order(client=client, body=order_body, type=order_type)
            session.add(new_order)
            await session.flush()
            bot_logger.debug(f'new order {new_order}')
            order_status = OrderStatus(order_id=new_order.id, status=True)
            session.add(order_status)
            await session.flush()
            id = new_order.id
            if order_type in [OrderType.kaz_cabinet, OrderType.kaz_links]:
                order_status_info = OrderStatusInfo(order_id=new_order.id, status=True)
                session.add(order_status_info)
                await session.flush()
    return id


async def get_country_by_orders_id(orders: list) -> Set | None:
    async with AsyncSession(async_engine_bot) as session:
        async with session.begin():
            print('Start Good DB')

            stmt = select(OrderStatusInfo).where(OrderStatusInfo.order_id.in_(orders))
            print(orders, stmt)
            result = await session.execute(stmt)
            counties = []
            print(result)
            if result:
                order_status_info = result.scalars()
                for status in order_status_info:
                    if status.host_country:
                        counties.append(status.host_country)
            else:
                return None
            print('STOP good db')
            return set(counties)


async def get_order_info_by_id(order_id):
    if not order_id:
        return False, 'No order id'
    try:
        order_id = int(order_id)
    except:
        return False, f'Invalid order id {order_id}'
    async with AsyncSession(async_engine_bot) as session:
        async with session.begin():
            stmt = select(Order).where(Order.id == order_id)
            result = await session.execute(stmt)
            order = result.scalar_one_or_none()
            if not order:
                return False, f'Cant to find order with that id ; {order_id}'
            order_dict = order.to_dict()
            stmt = select(OrderStatusInfo).where(OrderStatusInfo.order_id == order_id)
            result = await session.execute(stmt)
            order_status_info = result.scalar_one_or_none()
            if not order_status_info:
                result_dict = order_dict
            else:
                order_status_info_dict = order_status_info.to_dict()
                result_dict = {**order_dict, **order_status_info_dict}
            return result_dict, "success"


async def collect_web_meta_by_id(web_user_id) -> List[Dict]:
    print('start collect meta')
    """ Для сбора метаданных """
    async with AsyncSession(async_engine_bot) as session:
        async with session.begin():
            try:
                web_user_id = int(web_user_id)
                stmt = select(WebUserMetaData).where(WebUserMetaData.web_user == web_user_id)
                result = await session.execute(stmt)
            except Exception as er:
                my_logger.error(f'I cant to execute meta data {er}')
                return False
            if not result:
                return False
            try:
                fields = result.scalars()
                meta_fields = [web_meta.to_dict() for web_meta in fields]
            except Exception as er:
                my_logger.error(f'cant to make meta fields list: {er}')
                return False
            return meta_fields


async def extract_web_meta_by_id(web_user_id, session) -> List[Dict]:
    """ Для сбора метаданных """
    try:
        web_user_id = int(web_user_id)
        stmt = select(WebUserMetaData).where(WebUserMetaData.web_user == web_user_id)
        result = await session.execute(stmt)
    except Exception as er:
        my_logger.error(f'I cant to execute meta data {er}')
        return False
    if not result:
        return False
    try:
        fields = result.scalars()
        meta_fields = [web_meta.to_dict() for web_meta in fields]
        meta_dict = reduce(lambda x, y: {**x, **y}, meta_fields)
    except Exception as er:
        my_logger.error(f'cant to make meta fields list: {er}')
        return False
    return meta_dict


async def extract_web_user_by_id(web_user_id, session) -> List[Dict]:
    try:
        web_user_id = int(web_user_id)
        stmt = select(WebUser).where(WebUser.user_id == web_user_id)
        result = await session.execute(stmt)
        user = result.scalar()
        model = user.to_dict()
        return model
    except Exception as er:
        my_logger.error(f'I cant to execute web user data {er}')
        return {'result': f'I cant to execute web user data {er}'}


async def extract_telegram_user_by_id(session, telegram_id):
    stmt = select(User).where(User.user_id == telegram_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        return {'cant find user with telegram id': telegram_id}
    user_dict = user.to_dict()
    return user_dict


async def extract_orders_by_user_id(session, client_id, is_web):
    if is_web:
        my_logger.debug('web_way')
        stmt = select(Order.id).where(Order.web_user == client_id)
    else:
        stmt = select(Order.id).where(Order.client == client_id)
    result = await session.execute(stmt)
    if not result:
        return {'orders': 'no orders'}
    my_logger.debug('step 1')
    orders = result.fetchall()
    my_logger.debug('step 2')
    order_ids = [str(order) for order, in orders]
    my_logger.debug('step 3')
    try:
        order_ids_str = ', '.join(order_ids)
        orders_dict = {'orders': order_ids_str}
    except Exception:
        return {'orders': 'no orders'}
    return orders_dict


def extract_digits(input_string):
    return ''.join(re.findall(r'\d+', input_string))


async def collect_user_data_by_user_id(user_id):
    async with AsyncSession(async_engine_bot) as session:
        async with session.begin():
            if 'w' in user_id or "W" in user_id:
                my_logger.debug('web user way')
                web_user = extract_digits(user_id)
                web_user = int(web_user)
                print('step-1')
                web_user_dict = await extract_web_user_by_id(web_user_id=web_user, session=session)
                print('step-2')
                meta_dict = await extract_web_meta_by_id(web_user_id=web_user, session=session)
                print('step-3')
                orders = await extract_orders_by_user_id(client_id=web_user, session=session, is_web=True)
                print('step-4')
                result = {**web_user_dict, **meta_dict, **orders}
            else:
                my_logger.debug('telegram way')
                try:
                    user_id = int(user_id)
                except Exception:
                    my_logger.error("we have exception of user_id")
                    return {'result': f'Invalid user id {user_id}'}
                print('step-1')
                user_info = await extract_telegram_user_by_id(session=session, telegram_id=user_id)
                print(user_info)
                print('step-2')
                orders = await extract_orders_by_user_id(client_id=user_id, session=session, is_web=False)
                print(orders)
                result = {**user_info, **orders}
                print(result)
            return result


async def collect_user_data_by_order_id(order_id):
    async with AsyncSession(async_engine_bot) as session:
        async with session.begin():
            stmt = select(Order).where(Order.id == order_id)
            result = await session.execute(stmt)
            order = result.scalar_one_or_none()
            if not order:
                return {'result': 'No such order in DB'}
            if order.client:
                my_logger.debug('EXTRACT TELEGRAM USER')
                result = await extract_telegram_user_by_id(session=session, telegram_id=order.client)
            elif order.web_user:
                my_logger.debug('EXTRACT WEB USER')
                web_user_dict = await extract_web_user_by_id(web_user_id=order.web_user, session=session)
                meta_dict = await extract_web_meta_by_id(web_user_id=order.web_user, session=session)
                result = {**meta_dict, **web_user_dict}
    return result


async def add_email_task(web_message_id: int) -> bool:
    """функция для добавления задачи на рассылку почты"""
    async with AsyncSession(async_engine_bot) as session:
        async with session.begin():
            my_logger.info(f'Start dd email ask web_message_id: {web_message_id}')
            try:
                id2 = int(web_message_id)
                message = await session.get(WebMessage, ident=id2)
                if not message:
                    return False
            except Exception as ER:
                print(ER)
                return False
            print('try to get user')

            print(message.user)
            user_id = message.user
            stmt = select(EmailTask).where(
                (EmailTask.web_user == user_id) & (EmailTask.status == EmailTaskStatus.AWAIT))
            result = await session.execute(stmt)
            task = result.scalar_one_or_none()
            if task:
                task.status = EmailTaskStatus.CANCELED
                await session.flush()
            data = datetime.datetime.now() + datetime.timedelta(hours=1)
            header = HEADER_TEXT
            text = message.message_body
            new_task = EmailTask(web_user=user_id,
                                 text=text,
                                 header=header,
                                 status=EmailTaskStatus.AWAIT,
                                 execute_time=data)
            session.add(new_task)
            await session.flush()
            return True


def get_email_by_user_id(user_id, session):
    stmt = select(WebUserMetaData).where(
        (WebUserMetaData.web_user == user_id) & (WebUserMetaData.field == 'user_email'))
    result = session.execute(stmt)
    meta = result.scalar_one_or_none()
    if meta:
        email = meta.value
        return email
    else:
        return False


def check_was_last_message_read(user_id, session):
    """only for WEB users"""
    stmt = (
        select(WebMessage)
        .where(WebMessage.user == user_id)
        .order_by(WebMessage.id.desc())
        .limit(1)
    )
    result = session.execute(stmt)
    last_message = result.scalar_one_or_none()
    if last_message:
        return last_message.is_read
    return False