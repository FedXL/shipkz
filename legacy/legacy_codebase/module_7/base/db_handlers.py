import hashlib
import json
from enum import Enum
from typing import Tuple, Any

from sqlalchemy import select, desc, delete, update, join
from sqlalchemy.dialects.postgresql import insert

from sqlalchemy.ext.asyncio import AsyncSession
import datetime
from sqlalchemy.orm import selectinload
from module_7.base.engines import async_engine
from base.models import WebUser, Jwt, WebSocket, WebMessage, WebPhoto, Message, Photo, RootUser, Order, OrderStatusInfo, \
    User, OrderStatus, WebDoc, WebSocketSupport, WebUserMetaData

from module_7.handlers.pydentic_models import MessageType, HistoryDetails
from logs.logs import my_logger
from module_7.utils.create_web_order_parcer import OrderReg, OrderNotReg
from utils.config import SUPER_WEB_USER, async_engine_bot, WEB_USER_META_FIELDS


class PackageStatus(Enum):
    init = "PAID"
    arrived_to_forward = "ARRIVED_AT_FORWARDER_WAREHOUSE"
    got_track = "SENT_TO_HOST_COUNTRY"
    arrived_to_KZ = "ARRIVED_IN_HOST_COUNTRY"
    received_in_KZ = "RECEIVED_IN_HOST_COUNTRY"
    send_to_RU = "SENT_TO_RUSSIA"
    success = "GET_BY_CLIENT"

    """
- заказ выкуплен в магазине
- заказ отправлен в казахстан /заказ в пути
- заказ получен для отравки в рф
- заказ отправлен в рф
- заказ получен клиентом
    """
    """
- заказ выкуплен в магазине
- заказ поступил на склад форвардера
- заказ отправлен в казахстан (получен трек)  / заказ в пути
- заказ поступил на территорию казахстана
- заказ получен для последующей отправки
- заказ отправлен в рф
- закз получен клиентом
    """


async def change_order_status_in_db(status: str | None, order_id: int):
    """изменить ордер статус в ордере и собрать информацю по заказу. Основная задача просто подтвердить функцию"""
    if status not in [member.value for member in PackageStatus.__members__.values()]:
        return False, "Invalid status"
    async with AsyncSession(async_engine) as session:
        async with session.begin():
            order = await session.get(Order, order_id)
            if order:
                try:
                    order.status = status
                    await session.flush()
                    data = {'details': order.status,
                            'order_id': order.id,
                            'result': 'success'}
                    await session.commit()
                    return data, 'Success'
                except Exception as er:
                    return False, str(er.args)
            else:
                return False, f'Cant to find order with that id {order_id}'


async def add_order_status_info_db(order_id: int, data: dict) -> Tuple[bool, str] | Tuple[bool, None]:
    async with AsyncSession(async_engine) as session:
        async with session.begin():
            stmt = select(OrderStatusInfo).where(OrderStatusInfo.order_id == order_id)
            result = await session.execute(stmt)
            order_info = result.scalar()
            print('ORDER DATA', data)
            try:
                if order_info:
                    stmt = update(OrderStatusInfo).where(OrderStatusInfo.order_id == order_id)
                    stmt = stmt.values(**data)
                    print('UPDATE STATUS INFO', stmt)
                    await session.execute(stmt)
                    result = True, 'successful update'
                else:
                    new_order_info = OrderStatusInfo(order_id=order_id, **data)
                    print('CREATE STATUS INFO', new_order_info)
                    session.add(new_order_info)
                    await session.commit()
                    result = True, 'successful create'
            except Exception as ER:
                print(f'ERROR in add item info {ER}')
                result = False, f"ADD info to item ERROR: {ER.args}"
            finally:
                return result


async def replace_user(data: dict) -> Tuple[bool, str]:
    async with AsyncSession(async_engine) as session:
        async with session.begin():
            try:
                user_type = data.get('is_webuser')
                user_id = data.get('user_id')
                try:
                    order_id = int(data.get('order_id'))
                except ValueError:
                    return False, f'Invalid order id : {order_id}'

                if not user_type or not user_id or not order_id:
                    return False, f"Some fields user : {user_id}, order: {order_id} , is_webuser :{user_type} is invalid"
                stmt = select(Order).where(Order.id == order_id)
                result = await session.execute(stmt)
                order = result.scalar()
                if not order:
                    return False, f'Cant to find order in system with that id: {order_id}'
                if order.user_ip is not None:
                    return False, (f"This order have anonymous structure and cannot to be changed. Plz use not "
                                   f"anonymous web form")

                match user_type:
                    case "web_user":
                        try:
                            webuser_id = int(user_id)
                            stmt = select(webuser_id).where(WebUser.user_id == webuser_id)
                        except ValueError:
                            stmt = select(WebUser).where(WebUser.web_username == user_id)
                        result = await session.execute(stmt)
                        webuser = result.scalar()
                        if not webuser:
                            return False, f'Cant to find webuser in system with that id: {webuser}'
                        if order.client is not None:
                            return False, (f"This order was created with telegram bot. Plz create order with web site "
                                           f"to add web user")
                        stmt = update(Order).where(Order.id == order_id).values(web_user=webuser.user_id, user_ip=None,
                                                                                client=None)
                    case "telegram_user":
                        try:
                            telegram_id = int(user_id)
                        except ValueError:
                            return False, f"Bad user_id. it should to be 8-11 numbers {user_id} "
                        stmt = select(User).where(User.user_id == telegram_id)
                        result = await session.execute(stmt)
                        telegram_user = result.scalar()
                        if not telegram_user:
                            return False, f"Cant to find telegram user with that telegram_id {user_id}"
                        if order.web_user:
                            return False, f'Cant to add web user to to order from telegram bot'

                        stmt = update(Order).where(Order.id == order.id).values(web_user=None, user_ip=None,
                                                                                client=telegram_user.user_id)
                await session.execute(stmt)
                return True, 'successfully'
            except Exception as er:
                return False, f"Unexpected error {er}"


async def create_order_web(web_order_data: OrderReg | OrderNotReg, user: dict):
    order = Order(type='WEB_ORDER',
                  body=web_order_data.model_dump_json())
    if user.get('user_id') == 0:
        my_logger.debug(f"start unregistered user branch")
        order.user_ip = web_order_data.user_ip
        web_user = web_order_data.username
        if web_user:
            order_id, web_user_id = await save_order_web(order=order, web_user=web_user)
        else:
            my_logger.error("cant to find webusername in incoming data")
            raise AssertionError
    else:
        my_logger.info(f"start registered user branch")
        web_user = user.get('username')
        order_id, web_user_id = await save_order_web(order=order, web_user=web_user)
    if order_id:
        return order_id, web_user, web_user_id
    else:
        my_logger.error('cant to save order and get order id')
        raise AssertionError


def format_current_datetime(current_datetime):
    formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M')
    return formatted_datetime


async def get_orders_by_username(username: str, variant='paid'):
    async with AsyncSession(async_engine) as session:
        async with session.begin():
            stmt = select(WebUser.user_id).where(WebUser.web_username == username)
            query = await session.execute(stmt)
            web_user_id = query.scalar_one_or_none()
            if not web_user_id:
                return False, f"Cant to find user with {username}"
            stmt = (select(Order, OrderStatusInfo)
                    .select_from(join(Order, OrderStatusInfo, Order.id == OrderStatusInfo.order_id, isouter=True))
                    .where(Order.web_user == web_user_id)
                    .order_by(desc(Order.id)))
            result_all = await session.execute(stmt)
            rows = result_all.fetchall()
            orders_list = []
            match variant:
                case "paid":
                    for row in rows:
                        _order = row[0]
                        _order_dict = _order.to_dict()
                        sring = _order.body
                        _order_dict['body'] = json.loads(sring)
                        _status = row[1]
                        if _status:
                            _status_dict = _status.to_dict()
                            result_dict = {**_order_dict, 'order_status_info': {**_status_dict}}
                            status_check = make_text_for_status(result_dict)
                            result_dict['order_status_info']['progres_bar'] = status_check
                            if result_dict['order_status_info']['host_country'] == 'KAZAKHSTAN':
                                result_dict['order_status_info']['host_country'] = 'Казахстан'
                            elif result_dict['order_status_info']['host_country'] == 'KYRGYZSTAN':
                                result_dict['order_status_info']['host_country'] = 'Кыргызстан'
                                orders_list.append(result_dict)
                            orders_list.append(result_dict)
                        else:
                            continue
                case 'not_yet':
                    for row in rows:
                        _order = row[0]
                        _order_dict = _order.to_dict()
                        sring = _order.body
                        _order_dict['body'] = json.loads(sring)
                        _status = row[1]
                        if _status:
                            continue
                        else:
                            result_dict = {**_order_dict}
                            orders_list.append(result_dict)

    return orders_list


def make_text_for_status(data):
    """
- заказ выкуплен в магазине
- заказ отправлен в казахстан (получен трек)  / заказ в пути
- заказ поступил на территорию казахстана
- заказ получен для последующей отправки
- заказ отправлен в рф
- заказ получен клиентом

"""

    order_status_info = data.get('order_status_info')
    is_forwarder = order_status_info.get('is_forwarder_way')
    check_list_1 = [
        'arrived_to_forwarder',
        'send_to_host_country',
        'received_in_host_country',
        'send_to_ru'
    ]

    check_list_2 = [
        'send_to_host_country',
        'arrived_to_host_country',
        'received_in_host_country',
        'send_to_ru'
    ]
    if is_forwarder:
        check_list = check_list_1
    else:
        check_list = check_list_2

    result = {}
    count = 2
    for check in check_list:
        data = order_status_info.get(check)
        if data:
            result[count] = True
        else:
            result[count] = False
        count += 1
    return result


async def save_order_web(order: Order, web_user: str) -> bool | tuple[int, Any]:
    my_logger.debug("start save order web")
    async with AsyncSession(async_engine) as session:
        async with session.begin():
            my_logger.debug(f"web_user: {web_user}")
            stmt = select(WebUser).where(WebUser.web_username == web_user)
            user = await session.execute(stmt)
            web_user_obj = user.scalars().one_or_none()
            if web_user_obj:
                web_user_id = web_user_obj.user_id
                print('[WEB USER id найдись]', web_user_id)
            else:
                my_logger.error(f'Нет такого веб пользователя с именем {web_user}')
                return False
            order.web_user = web_user_id
            my_logger.debug(f"try to save order{vars(order)}")
            session.add(order)
            await session.flush()
            print('GO NEXT')
            order_id = order.id
            order_status = OrderStatus(status=True,
                                       order_id=order_id)
            session.add(order_status)
            await session.flush()
            print('GO NEXT NEXT')
            web_message = WebMessage(is_answer=False, user=web_user_id)
            message_body = "/order_" + str(order_id)
            web_message.message_body = message_body
            web_message.message_type = 'order'
            session.add(web_message)
            await session.commit()
            my_logger.info(f'success created order{order_id, web_user_id, web_user}')
            return order_id, web_user_id


async def add_photo_to_db_bot(
        photo_id: str,
        is_answer: bool,
        user_id: int = SUPER_WEB_USER,
        message_id: int = None):
    my_logger.debug('start')
    prefix = '/photo_'
    try:
        async with AsyncSession(async_engine_bot) as session:
            async with session.begin():
                if message_id:
                    new_message = Message(is_answer=is_answer, storage_id=user_id, message_id=message_id)
                else:
                    new_message = Message(is_answer=is_answer, storage_id=user_id)

                session.add(new_message)
                await session.flush()
                message_id_in_db: int = new_message.id
                session.add(Photo(file_id=photo_id, message_id=message_id_in_db))

                photo_command = prefix + str(message_id_in_db)
                await session.execute(
                    update(Message).where(Message.id == message_id_in_db).values(message_body=photo_command))
                await session.commit()
                my_logger.debug(f'finish {photo_command}')
                return photo_command

    except Exception as Error:
        my_logger.debug(f'all is bad {Error}')


async def update_text_in_message_in_web_db(web_message_id: int, text: str):
    async with AsyncSession(async_engine) as session:
        async with session.begin():
            stmt = update(WebMessage).where(WebMessage.id == web_message_id).values(message_body=text)
            await session.execute(stmt)
            await session.commit()


async def save_photo_message_to_web_db(
        is_answer: bool,
        user_id: int,
        message_type: str,
        text: str,
        message_id: int | None = None,
        extension: str = None,
        time=None,
        bot_command=None, ):
    async with AsyncSession(async_engine) as session:
        async with session.begin():
            new_message = WebMessage(message_body=bot_command,
                                     is_answer=is_answer,
                                     user=user_id,
                                     message_type=message_type)
            session.add(new_message)
            await session.flush()
            message_id = new_message.id
            photo = WebPhoto(photo_path=text,
                             message_id=message_id)
            session.add(photo)
            await session.flush()
            return message_id


async def create_user(name):
    my_logger.debug(f'start foo with name: {name}')
    async with AsyncSession(async_engine) as session:
        async with session.begin():
            created_time = datetime.datetime.now()
            user = WebUser(user_name=name,
                           is_kazakhstan=True,
                           last_online=created_time)
            session.add(user)
            await session.flush()
            user_id = user.user_id
            await session.commit()
    return user_id


async def create_user_WEB(username):
    my_logger.debug(f'start foo with name: {username}')
    async with AsyncSession(async_engine) as session:
        async with session.begin():
            created_time = datetime.datetime.now()
            user = WebUser(web_username=username,
                           is_kazakhstan=True,
                           last_online=created_time)
            session.add(user)
            await session.flush()
            user_id = user.user_id
            await session.commit()
    return user_id


async def create_user_ROOT(user_id):
    my_logger.debug(f'start foo with name: {user_id}')
    async with AsyncSession(async_engine) as session:
        async with session.begin():
            user = RootUser(web_user=user_id)
            session.add(user)
            await session.flush()
            id = user.id
            await session.commit()
    return id


async def create_user_from_wp(username):
    """:return (user_id, root_id)"""
    user_id = await create_user_WEB(username)
    root_id = await create_user_ROOT(user_id)
    return user_id, root_id


async def create_user_from_wp_with_meta(data_dict: dict):
    """:return Tuple ( root_user_id, web_user_id)"""
    username = data_dict.get('username')
    if not username:
        my_logger.error('no username in data dict')
        raise ValueError("Username is required")
    my_logger.debug(f'start foo with name: {username}')
    async with AsyncSession(async_engine) as session:
        async with session.begin():
            created_time = datetime.datetime.now()
            web_user = WebUser(web_username=username, is_kazakhstan=True, last_online=created_time)
            session.add(web_user)
            await session.flush()
            user_id = web_user.user_id
            root_user = RootUser(web_user=user_id)
            session.add(root_user)
            await session.flush()
            root_id = root_user.id
            try:
                for field in WEB_USER_META_FIELDS:
                    meta_data = WebUserMetaData(field=field, value=str(data_dict.get(field)), web_user=user_id)
                    session.add(meta_data)
                await session.flush()
            except Exception as ER:
                my_logger.error(f'не удалось сохранить метаданные пользователя {ER}')
            await session.commit()
            return user_id, root_id


async def update_user_wp_meta(data_dict: dict):
    """:return Tuple ( root_user_id, web_user_id)"""
    username = data_dict.get('username')

    if not username:
        my_logger.error('no username in data dict')
        raise ValueError("Username is required")
    my_logger.debug(f'start foo with name: {username}')
    async with AsyncSession(async_engine) as session:
        async with session.begin():
            stmt = select(WebUser).where(WebUser.web_username == username)
            result = await session.execute(stmt)
            user_record = result.fetchone()
            user_id = user_record.WebUser.user_id if user_record else None
            if user_id:
                for field in WEB_USER_META_FIELDS:
                    value = str(data_dict.get(field))
                    if value is not None:
                        stmt = (
                            insert(WebUserMetaData)
                            .values(web_user=user_id, field=field, value=value)
                            .on_conflict_do_update(
                                constraint='uq_field_web_user',
                                set_={
                                    'value': value,
                                    'field': field,
                                    'web_user': user_id
                                }
                            )
                        )
                        await session.execute(stmt)
                await session.commit()
                my_logger.debug(f'Metadata for user {username} updated successfully.')
                return True
            else:
                my_logger.error(f'User {username} not found.')
                return False


async def associate_user_with_token(user_id, token):
    my_logger.debug('start')
    token_hash = hashlib.sha256(token.split('.')[2].encode()).hexdigest()
    async with AsyncSession(async_engine) as session:
        async with session.begin():
            jwt_token = Jwt(user_id=user_id,
                            jwt_hash=token_hash)
            session.add(jwt_token)
            await session.flush()
            if jwt_token.id:
                my_logger.debug(f'success token_id: {jwt_token.id}')
                await session.commit()
            else:
                my_logger.error(f'fail')


async def get_user_by_token(token: str) -> int:
    """webchat"""
    my_logger.debug('start')
    token_hash = hashlib.sha256(token.split('.')[2].encode()).hexdigest()
    try:
        async with AsyncSession(async_engine) as session:
            async with session.begin():
                stmt = select(Jwt.user_id).where(Jwt.jwt_hash == token_hash)
                result = await session.execute(stmt)
                user_id = result.scalar()
                return user_id
    except Exception as ER:
        my_logger.error(f'Cannot to get user by token {ER}')


async def associate_user_with_socket(user_id, socket_id):
    my_logger.debug(f'start with user {user_id} socket {socket_id}')
    try:
        socket_id = int(socket_id)
        user_id = int(user_id)
        async with AsyncSession(async_engine) as session:
            async with session.begin():
                websocket = WebSocket(socket_id=socket_id, user_id=user_id)
                session.add(websocket)
                await session.commit()
        my_logger.debug(f'socket saved {socket_id} with {user_id}')
    except Exception as ER:
        my_logger.error(f'[SOCKET ASSOCIATE ERROR] :  {ER}')


async def associate_user_with_support_socket(user_id, socket_id):
    my_logger.debug(f'start with user {user_id} socket {socket_id}')
    try:
        socket_id = int(socket_id)
        user_id = int(user_id)
        async with AsyncSession(async_engine) as session:
            async with session.begin():
                websocket = WebSocketSupport(socket_id=socket_id, user_id=user_id)
                session.add(websocket)
                await session.commit()
        my_logger.debug(f'socket saved {socket_id} with {user_id}')
    except Exception as ER:
        my_logger.error(f'[SOCKET ASSOCIATE ERROR] :  {ER}')


async def download_history(user_id: int,
                           is_for_meeting_message=False,
                           is_short_history=False,
                           with_name_mode=False) -> list[HistoryDetails]:
    """Честно пытался разобраться с relationships, но ни фига не понял. Как у двух моделей
    строить понятно, а как у трех моделей связанных внешними ключами photo-fk->message-fk->user
    как построить relationship отношение photo<-message->user не понимаю хоть убей"""
    assert isinstance(user_id, int), f'user_id in is not int type = {type(user_id)}, {user_id}'
    assert isinstance(is_for_meeting_message, bool), 'is_for_meeting_message is not bool'
    my_logger.debug(
        f'start download history with user id {user_id}, is it for meeting message?  {is_for_meeting_message}')
    async with AsyncSession(async_engine) as session:
        async with session.begin():
            if is_for_meeting_message:
                if is_short_history:
                    stmt = select(WebMessage).where(WebMessage.user == user_id).order_by(desc(WebMessage.time)).options(
                        selectinload(WebMessage.user_relationship)).limit(5)
                else:
                    stmt = select(WebMessage).where(WebMessage.user == user_id).order_by(desc(WebMessage.time)).options(
                        selectinload(WebMessage.user_relationship))
            else:
                stmt = select(WebMessage).where(WebMessage.user == user_id).order_by(WebMessage.time).options(
                    selectinload(WebMessage.user_relationship))
            print(stmt)

            messages = await session.execute(stmt)
            messages = messages.scalars()
            history = []
            for mess in messages:
                mess_dict = mess.as_dict()
                mess_dict['user_name'] = mess.user_relationship.web_username
                hist = HistoryDetails(**mess_dict)
                if hist.is_answer and not is_for_meeting_message:
                    text_splited = hist.text.split(':', 1)
                    if len(text_splited) > 1:
                        manager_name = text_splited[0]
                        hist.user_name = manager_name
                        hist.text = text_splited[1]
                if not is_for_meeting_message:
                    if hist.message_type == 'photo':
                        stmt = select(WebPhoto.photo_path).where(WebPhoto.message_id == hist.message_id)
                        photo = await session.execute(stmt)
                        photo_path = photo.scalar()
                        hist.text = photo_path
                    elif hist.message_type == 'document':
                        stmt = select(WebDoc.doc_path).where(WebDoc.message_id == hist.message_id)
                        document = await session.execute(stmt)
                        document_path = document.scalar()
                        hist.text = document_path
                else:
                    original_date = hist.time
                    original_date_with_year = "2024, " + original_date
                    parsed_date = datetime.datetime.strptime(original_date_with_year, "%Y, %B %d, %H:%M")
                    formatted_date = parsed_date.strftime("%d-%m %H:%M")
                    hist.time = formatted_date
                history.append(hist)

            stmt_last = select(WebUser).where(WebUser.user_id == user_id)
            print('[HERE HERE]')
            if with_name_mode:
                result = await session.execute(stmt_last)
                web_user = result.scalar()
                if web_user:
                    username = web_user.web_username
    my_logger.debug('extract history success')
    if with_name_mode:
        print('HISTORY USERNAME', username)
        return history, username
    else:
        return history


async def get_name_from_db(user_id: int):
    async with AsyncSession(async_engine) as session:
        async with session.begin():
            stmt = select(WebUser.user_name).where(WebUser.user_id == user_id)
            result = await session.execute(stmt)
            username = result.scalar()
            return username


async def save_message_to_db(message_id: int | None,
                             is_answer: bool,
                             user_id: int | None,
                             message_type: MessageType,
                             text: str | None,
                             token=None,
                             extension=None,
                             time=None,
                             user_name=None,
                             file=None,
                             mimi_type=None,
                             is_read=False):
    """is_answer = false -> from user / is_answer = true -> from manager"""
    my_logger.debug('try to save message')
    try:
        async with AsyncSession(async_engine) as session:
            async with session.begin():
                if is_answer == True:
                    is_read = False
                else:
                    is_read = True

                new_message = WebMessage(message_body=text,
                                         message_type=message_type,
                                         is_answer=is_answer,
                                         user=user_id,
                                         is_read=is_read)
                session.add(new_message)
                await session.flush()
                id = new_message.id
                await session.commit()
                my_logger.debug('message was successfully saved')
                return id

    except Exception as ER:
        my_logger.error(f'Cannot to save message {text} error: {ER}')
        raise ArithmeticError


async def remove_socket_from_db(socket_id: int):
    my_logger.debug(f'start to kill socket: {socket_id} ')
    async with AsyncSession(async_engine) as session:
        async with session.begin():
            stmt = delete(WebSocket).where(WebSocket.socket_id == socket_id)
            await session.execute(stmt)
            await session.commit()
    my_logger.debug(f'{socket_id} socket was successfully killed')


async def remove_socket_from_db_support(socket_id: int):
    """delete socket from WebSocketSupport model database"""
    my_logger.debug(f'start to kill socket: {socket_id} ')
    async with AsyncSession(async_engine) as session:
        async with session.begin():
            stmt = delete(WebSocketSupport).where(WebSocketSupport.socket_id == socket_id)
            await session.execute(stmt)
            await session.commit()
    my_logger.debug(f'{socket_id} socket was successfully killed')


async def refresh_old_token(old_token, new_token):
    async with AsyncSession(async_engine) as session:
        async with session.begin():
            token_hash_old = hashlib.sha256(old_token.split('.')[2].encode()).hexdigest()
            stmt = select(Jwt.user_id).where(Jwt.jwt_hash == token_hash_old)
            user = await session.execute(stmt)
            user_id = user.scalar()
            if user_id:
                stmt_delete = delete(Jwt).where(Jwt.jwt_hash == token_hash_old)
                await session.execute(stmt_delete)
                token_hash_new = hashlib.sha256(new_token.split('.')[2].encode()).hexdigest()
                jwt_token = Jwt(user_id=user_id, jwt_hash=token_hash_new)
                session.add(jwt_token)
                await session.commit()
                return True
            else:
                return False


async def is_kazakhstan_chat(user_id: int):
    async with AsyncSession(async_engine) as session:
        async with session.begin():
            stmt = select(WebUser.is_kazakhstan).where(WebUser.user_id == user_id)
            result = await session.execute(stmt)
            is_kz = result.scalar()
            return is_kz


async def save_message_id_to_user(message_id: int, user_id: int):
    # message_id from telegram message
    my_logger.debug('start')
    async with AsyncSession(async_engine) as session:
        async with session.begin():
            stmt = update(WebUser).where(WebUser.user_id == user_id).values(last_message_telegramm_id=message_id)
            await session.execute(stmt)
            await session.commit()
            my_logger.debug('finish')


async def get_message_id(user_id: int):
    async with AsyncSession(async_engine) as session:
        async with session.begin():
            stmt = select(WebUser.last_message_telegramm_id).where(WebUser.user_id == user_id)
            result = await session.execute(stmt)
            message_id = result.scalar()
            return message_id
