import asyncio
import json
import aiohttp
import aioredis
import async_timeout
from aiohttp import web
from base.good_db_handlers import get_web_user_id_by_name, get_all_unread_message_count_by_web_user
from module_7.base.db_handlers import associate_user_with_support_socket, remove_socket_from_db_support
from module_7.base.redis_handlers import save_socket_to_redis_support, delete_socket_from_redis_support, \
    get_user_id_by_socket_id_support, get_socket_id_by_user_id_support
from module_7.handlers.pydentic_models import SupportLoad
from logs.logs import my_logger
from module_7.utils.token import check_token
from module_7.utils.utils3 import connect_to_redis_pubsub_menu

"""Сокет хендлер для управления ак минимум меню"""
STOPWORD = "STOP"


async def redis_menu_reader(channel: aioredis.client.PubSub, ws):
    my_logger.debug(f'Start redis listener with socket: {str(id(ws))}')
    while True:
        try:
            async with async_timeout.timeout(1):
                message = await channel.get_message(ignore_subscribe_messages=True)
                if message is not None:
                    print('[info] We hava a message from Manager Side')
                    try:
                        recieved_data = eval(message.get('data'))
                        data = json.loads(recieved_data)
                        support = SupportLoad(**data)
                        socket_id = await get_socket_id_by_user_id_support(support.userID)
                        if (int(id(ws))) == socket_id:
                            await ws.send_str(support.model_dump_json())
                            my_logger.debug(f"sending to socket {socket_id} message = {support.event}")
                        elif message["data"].decode() == STOPWORD:
                            print("(Reader) STOP")
                            break
                    except Exception as ER:
                        my_logger.error(f'Cant to send message to socket: {ER}')
                await asyncio.sleep(0.5)
        except asyncio.TimeoutError:
            pass


class CloseSocketException(Exception):
    def __init__(self, message="Close socket"):
        self.message = message
        super().__init__(self.message)


async def menu_websocket(request):
    """another socket to separate messager logic and others logic such as change menu logic"""
    print('[INFO] start websocket support ')
    place = 'beginning'
    ws = aiohttp.web.WebSocketResponse(max_msg_size=10194304)
    await ws.prepare(request)
    socket_id = int(id(ws))
    my_logger.debug(f'[INFO] new socket open: {socket_id}')
    pubsub = await connect_to_redis_pubsub_menu()
    task = asyncio.create_task(redis_menu_reader(pubsub, ws))

    try:
        async for msg in ws:
            place = 'preparing'
            if msg.type == aiohttp.WSMsgType.ERROR:
                my_logger.error(f'[ERROR] Ошибка веб-сокета:  {msg}')
                raise CloseSocketException(f'Socket mistake [MSG]: {msg}')
            elif msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data == 'close':
                    raise CloseSocketException('msg data = close Bye Bye menu socket')
                else:
                    data_dict = msg.json()
                    event = data_dict.get('event')
                    my_logger.debug(event)
                if not event:
                    data = {'result': 'Invalid data. No event in data'}
                    await ws.send_json(data)
                    raise CloseSocketException('Invalid data No event id data_dict Bye Bye socket')
                place = event
                match event:
                    case 'onconnect':
                        my_logger.debug("START EVENT on connect")
                        place = 'onconnect 1'
                        decrypted_token = check_token(data_dict.get('token'))
                        username = decrypted_token.get('username')
                        user_id = decrypted_token.get('user_id')
                        user_id = int(user_id)
                        place = 'onconnect 2'
                        web_user_id = await get_web_user_id_by_name(username=username)
                        if not web_user_id:
                            raise CloseSocketException('Unregistered user in registered user branch (cant to get '
                                                       'user_id by get_web_user_id_by_name Bye Bye socket')
                        place = 'onconnect 3'
                        await associate_user_with_support_socket(user_id=web_user_id, socket_id=socket_id)
                        data = {'event': 'authorization', 'result': 'success'}
                        await ws.send_json(data)
                        await save_socket_to_redis_support(socket_id=socket_id, user_id=web_user_id)
                    case 'getUnreadMessageCount':
                        my_logger.debug("START EVENT ReadMessagesInfo ")
                        id_user = await get_user_id_by_socket_id_support(socket_id)
                        count = await get_all_unread_message_count_by_web_user(id_user)
                        data = {"event": "UnreadMessageCount",
                                "details": {"count": count}}
                        await ws.send_json(data)
    except CloseSocketException as er:
        my_logger.warning(f'[CLOSE SOCKET (support)] because {er}')
    except Exception as ER:
        my_logger.error(f'[CLOSE SOCKET (support)] Unexpected error in socket handler. Place : {place}. Error:  {ER}')
    finally:
        my_logger.debug(f'[CLOSE SOCKET (support)]: killing redis {task},delete socket {socket_id} from DB')
        task.cancel()
        id_user = await get_user_id_by_socket_id_support(socket_id)
        await delete_socket_from_redis_support(socket_id=socket_id, user_id=id_user)
        await remove_socket_from_db_support(socket_id)
        await ws.close()
