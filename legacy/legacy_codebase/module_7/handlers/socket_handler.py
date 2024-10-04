import asyncio
import base64
import datetime
import mimetypes
import re
from typing import Tuple
import aiohttp
import aioredis
import async_timeout
import magic
from aiohttp import web
from sqlalchemy.ext.asyncio import AsyncSession
from base.good_db_handlers import get_web_user_id_by_name, add_document_to_db_, save_document_message_to_web_db, \
    add_photo_to_db_, save_photo_message_to_web_db, get_web_username_by_user_id, have_read_the_message
from handlers.chat.sender import download_photo_or_document_to_server
from module_7.base.db_handlers import associate_user_with_socket, \
    download_history, \
    remove_socket_from_db
from module_7.base.redis_handlers import save_socket_user_mapping, delete_socket_user_mapping, get_user_id_by_socket_id, \
    get_socket_id_by_user_id
from module_7.bot.bot_handlers import get_telegram_photo_or_document_id, send_meeting_message_to_bot
from module_7.handlers.event_handlers import message_event_handler
from module_7.handlers.pydentic_models import MessageLoad, HistoryLoad
from logs.logs import my_logger
from module_7.utils.token import check_token
from module_7.utils.utils3 import connect_to_redis_pubsub
from utils.config import SUPER_WEB_USER, async_engine_bot
from utils.eye_queue import add_element


"""Сокет хендлер для управления мессанджером"""

STOPWORD = "STOP"


async def redis_reader(channel: aioredis.client.PubSub, ws):
    my_logger.debug(f'Start redis listener with socket: {str(id(ws))}')
    while True:
        try:
            async with async_timeout.timeout(1):
                message = await channel.get_message(ignore_subscribe_messages=True)
                if message is not None:
                    print('[info] We hava a message from Manager Side')
                    try:
                        recieved_data = eval(message.get('data'))
                        recieved_mes = MessageLoad(**recieved_data)
                        text = recieved_mes.details.text
                        text = text.split(':', 1)[1]
                        recieved_mes.details.text = text
                        socket_id = await get_socket_id_by_user_id(recieved_mes.details.user_id)
                        if (int(id(ws))) == socket_id:
                            await ws.send_str(recieved_mes.model_dump_json())
                            my_logger.debug(f"sending to socket {socket_id} message = {recieved_mes.details.text}")
                        elif message["data"].decode() == STOPWORD:
                            break

                    except Exception as ER:
                        my_logger.error(f'problem in sending message to web user section: {ER}')

                await asyncio.sleep(0.5)
        except asyncio.TimeoutError:
            pass


class CloseSocketException(Exception):
    def __init__(self, message="Close socket"):
        self.message = message
        super().__init__(self.message)


async def websocket_handler(request):
    print('[INFO] start websocket handler')
    place = None
    ws = aiohttp.web.WebSocketResponse(max_msg_size=10194304)
    await ws.prepare(request)
    socket_id = int(id(ws))
    my_logger.debug(f'[INFO] new socket open: {socket_id}')
    pubsub, redis = await connect_to_redis_pubsub()
    task = asyncio.create_task(redis_reader(pubsub, ws))

    try:
        async for msg in ws:
            place = 'preparing'
            if msg.type == aiohttp.WSMsgType.ERROR:
                my_logger.error(f'[ERROR] Ошибка веб-сокета:  {msg}')
                raise CloseSocketException(f'Socket mistake [MSG]: {msg}')
            elif msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data == 'close':
                    raise CloseSocketException('msg data = close Bye Bye socket')
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
                        place = 'onconnect 1'
                        decrypted_token = check_token(data_dict.get('token'))
                        my_logger.debug(f'socket : on connect : {decrypted_token}')
                        username = decrypted_token.get('username')
                        user_id = decrypted_token.get('user_id')
                        user_id = int(user_id)
                        place = 'onconnect 2'
                        web_user_id = await get_web_user_id_by_name(username=username)
                        if not web_user_id:
                            raise CloseSocketException('Unregistered user in registered user branch (cant to get '
                                                       'user_id by get_web_user_id_by_name Bye Bye socket')
                        place = 'onconnect 3'
                        await associate_user_with_socket(user_id=web_user_id, socket_id=socket_id)
                        data = {'event': 'authorization', 'result': 'success'}
                        await ws.send_json(data)
                        await save_socket_user_mapping(socket_id=socket_id,
                                                       user_id=web_user_id)
                    case 'download_history':
                        my_logger.debug('[checker branch] start download history')
                        id_user = await get_user_id_by_socket_id(socket_id=socket_id)
                        history = await download_history(user_id=id_user)
                        print('history was good downloaded', str(history)[:100])
                        data = HistoryLoad(event='download_history', data=history)
                        await ws.send_json(data.model_dump())
                        my_logger.debug('the history was successfully send')
                    case 'message':
                        my_logger.debug('start event : message  from  message branch')
                        message_load = MessageLoad(**data_dict)
                        print('[MESSAGE SENDING INFO]', message_load)
                        message_load.details.user_id = await get_user_id_by_socket_id(socket_id=socket_id)
                        await message_event_handler(data=message_load, ws=ws)
                    case 'uploadStatic':
                        my_logger.debug('start event : uploadStatic')
                        details = data_dict.get('details')
                        file_web = details.get('file_string')
                        user_id = await get_user_id_by_socket_id(socket_id=socket_id)
                        file_path, mimi = await download_photo_or_document_to_server(user_id=user_id, command=None,
                                                      incoming_file=file_web)
                        print(f'[RESULT] {file_path},{mimi}')
                        telegram_id, prefix = await get_telegram_photo_or_document_id(file_path=file_path)
                        print(f'[TELEGRAM RESULT]', telegram_id, prefix)
                        if prefix == '/doc_':
                            print('[DOCUMENTS BRANCH INCOMING]')
                            message_type = 'document'
                            async with AsyncSession(async_engine_bot) as session:
                                async with session.begin():
                                    command = await add_document_to_db_(session=session,
                                                                        prefix=prefix,
                                                                        is_answer=False,
                                                                        user_id=SUPER_WEB_USER,
                                                                        document_id=telegram_id)

                                    message_id = await save_document_message_to_web_db(document_path=file_path,
                                                                                       doc_command=command,
                                                                                       user_id=user_id,
                                                                                       is_answer=False,
                                                                                       session=session)
                                    await session.commit()
                            web_username = await get_web_username_by_user_id(user_id=user_id)
                            print(f'[START TO SEND MESSAGE TO BOT] with {user_id} {web_username} {command}')
                            await send_meeting_message_to_bot(user_id=user_id, user_name=web_username)
                        elif prefix == '/photo_':
                            message_type = "fastPhoto"
                            print('[PHOTO BRANCH INCOMING]')
                            async with AsyncSession(async_engine_bot) as session:
                                async with session.begin():
                                    print('PHOTO')
                                    command = await add_photo_to_db_(session=session,
                                                                     prefix=prefix,
                                                                     is_answer=False,
                                                                     user_id_=SUPER_WEB_USER,
                                                                     photo_id=telegram_id)

                                    message_id = await save_photo_message_to_web_db(photo_path=file_path,
                                                                                    photo_command=command,
                                                                                    user_id=user_id,
                                                                                    session=session,
                                                                                    is_answer=False)
                                    await session.commit()
                            web_username = await get_web_username_by_user_id(user_id=user_id)
                            print(f'[START TO SEND MESSAGE TO BOT] with {user_id} {web_username} {command}')
                            await send_meeting_message_to_bot(user_id=user_id, user_name=web_username)
                        else:
                            print("UNEXPECTED  PREFIX")
                            raise CloseSocketException
                        now = datetime.datetime.now()
                        formatted_datetime = now.strftime("%B %d, %H:%M")
                        data = {
                            "event": "message",
                            "name": web_username,
                            "details": {"message_id": message_id,
                                        "is_answer": False,
                                        "user_id": user_id,
                                        "message_type": message_type,
                                        "time": formatted_datetime,
                                        "user_name": web_username,
                                        "text": file_path
                                        }
                        }
                        await ws.send_json(data=data)
                        await ws.send_json(data={"event": "openAddButton"})
                    case 'downloadStatic':
                        my_logger.debug("start event : downloadStatic")
                        file_path = data_dict.get('path')
                        document_or_photo = is_document_or_photo(file_path)
                        targetID = data_dict.get('targetID')
                        id_user = await get_user_id_by_socket_id(socket_id=socket_id)
                        check_url, comment = path_access(id_user, file_path)
                        if check_url:
                            file64, mimi = await get_file(file_path)
                            data = {
                                "event": "fileDownload",
                                "details": {
                                    "message_type": "data_upload",
                                    "document_or_photo": document_or_photo,
                                    "targetID": targetID,
                                    "file": file64,
                                    "mimi_type": mimi,
                                }
                            }
                        else:
                            data = {"event": "serverError", "comment": comment}
                        await ws.send_json(data)
                    case 'isReadMessage':
                        my_logger.debug('start event : is ReadMessage')
                        message_id = data_dict.get('targetID')
                        user_id = await get_user_id_by_socket_id(socket_id=socket_id)
                        await add_element(redis, user_id)
                        if message_id:
                            match = re.search(r'\d+', message_id)
                            if match:
                                id_digits = int(match.group())  # Преобразуем в целое число
                                print("Айди цифры:", id_digits)
                                await have_read_the_message(id_digits)
                            else:
                                print("Цифры не найдены")
    except CloseSocketException as er:
        my_logger.warning(f'[CLOSE SOCKET] becouse {er}')
    except Exception as ER:
        my_logger.error(f'[CLOSE SOCKET couse] Unexpected error in socket handler. Place : {place}. Error:  {ER}')
    finally:
        my_logger.debug(f'[close socket]: killing redis {task},delete socket {socket_id} from DB')
        task.cancel()
        id_user = await get_user_id_by_socket_id(socket_id)
        await delete_socket_user_mapping(socket_id=socket_id, user_id=id_user)
        await remove_socket_from_db(socket_id)
        await ws.close()
    return ws


def is_document_or_photo(url):
    if 'documents' in url:
        return 'document'
    elif 'images' in url:
        return 'photo'
    else:
        return False


def path_access(id_user, file_path):
    try:
        match = re.search(r'/(\d+)/', file_path)
        if match:
            number = int(match.group(1))
            user_id = int(id_user)
            if id_user == number:
                return True, " "
            else:
                my_logger.warning('Socket user whants file with another user_id signature, looks hi is cheater')
                return False, "Access Denied u are the cheater"
        else:
            return False, "Invalid path"
    except Exception as error:
        my_logger.error(f'Unexpected Error {error}')
        return False, "Unexpected Error"


async def get_file(place_path: str) -> [Tuple[str, str] | Tuple[bool, str]]:
    try:
        with open(place_path, 'rb') as f:
            file_content = f.read()
            extension, mimi = get_mime_extension_bytes(file_content)
            file_base64 = base64.b64encode(file_content).decode('utf-8')
        return file_base64, mimi
    except FileNotFoundError:
        return False, 'file is not found'
    except Exception as error:
        return False, f'Unexpected error {error}'


def get_mime_extension_bytes(file_content: bytes) -> Tuple[str, str]:
    m = magic.Magic(mime=True)
    mimi = m.from_buffer(file_content)
    mimetypes.init()
    extension = mimetypes.guess_extension(mimi)
    print('[FILE EXTENSION MIMI]', extension, mimi)
    return extension, mimi
