import asyncio
import base64
import html
import io
import logging
import datetime
import os
from typing import Tuple
from aiogram import Dispatcher
from aiogram.dispatcher.filters import Regexp
from aiogram.types import ParseMode, CallbackQuery, PhotoSize, Document
from aiogram.utils import markdown
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from base.base_connectors import insert_to_base, get_messages_from_base_last_5, get_from_base, get_target_message
from base.base_handlers_bot import add_photo_to_bd, add_doc_to_bd, check_is_kazakhstan
from base.good_db_handlers import add_photo_to_db_, get_messages_from_base_last_5_g, add_document_to_db_, \
    save_text_message_to_db, get_messages_from_web_db, save_photo_message_to_web_db, save_document_message_to_web_db, \
    get_all_unread_message_count_by_web_user, add_email_task
from base.models import Message, User, WebUser
from base.redis_handlers import send_redis_mess_to_web, send_message_to_support
from create_bot import bot
import aiogram.utils.markdown as md
from handlers.admin.fast_answers import get_keyboard_answers_list
from logs.logs import my_logger
from module_7.base.db_handlers import download_history
from module_7.handlers.pydentic_models import SupportDetails, SupportLoad, MessageDetails
from sheets.add_orders import add_last_string
from utils.config import kazakhstan_chat, MANAGER, tradeinn_chat, alerts, async_engine_bot, SUPER_WEB_USER
from utils.errors import TelegramHandlerError
from utils.texts import get_id_from_text, make_message_text, make_message_text_full, make_mask_to_messages, thank_u, \
    get_mask_from_message, find_the_way, get_mask_from_web_message, make_message_text_w, TheWay, preparing_message_list, \
    make_message_text_full_w
from aiogram import types
from utils.utils_lite import quot_replacer, disappear_message_message_is_send, create_new_message_change, generate_salt, \
    get_mime_extension, image_or_document


def get_keyboard_message_start():
    buttons = [
        types.InlineKeyboardButton(text="🗃", callback_data="message_menu"),
        types.InlineKeyboardButton(text="↕️️", callback_data="fast_answers_choice"),
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


def get_keyboard_fast_answer_menu():
    buttons = [
        types.InlineKeyboardButton(text="Ответы 🗣", callback_data="fast_answers_list"),
        types.InlineKeyboardButton(text="Карты 💳️", callback_data="fast_cards_list"),
        types.InlineKeyboardButton(text="🔼", callback_data="fast_back")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


def get_keyboard_menu_mess():
    buttons = [
        types.InlineKeyboardButton(text="✅ Завершено", callback_data='is_answered'),
        types.InlineKeyboardButton(text="🆘 Внимание", callback_data='is_not_answered'),
        types.InlineKeyboardButton(text="⚽️ Перекинуть", callback_data='change_channel'),
        types.InlineKeyboardButton(text="Full History", callback_data='full_history')
    ]
    keyword = types.InlineKeyboardMarkup(row_width=2)
    keyword.add(*buttons). \
        add(types.InlineKeyboardButton(text="↕️", callback_data="long_history")). \
        add(types.InlineKeyboardButton("🔼", callback_data="fast_back"))
    return keyword


async def change_message(message: types.Message, new_text: str):
    chat_id = message.chat.id
    message_id = message.message_id
    await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=new_text)


async def read_message(chat_id: int, message_id: int):
    message = await bot.get_message(chat_id=chat_id, message_id=message_id)
    text = message.text
    print(text)


async def send_to_googlesheets(manager, user_id_, text_to_sheets):
    try:
        await add_last_string([(str(datetime.datetime.now()), manager, user_id_, text_to_sheets,)],
                              'messages_storage')
    except Exception as ER:
        print(f"[ERROR] google sheets error in chat admins part : {ER}")


async def send_photo_to_tele_user(message: types.Message,
                                  user_id: int,
                                  manager: str,
                                  is_answer: bool,
                                  session: AsyncSession) -> Tuple:
    photo_id = message.photo[-1].file_id
    text_to_sheets = "photo: " + photo_id
    manager_message = await bot.send_photo(user_id, photo_id)
    message_id = manager_message.message_id
    prefix = f"🔸 [{manager}]: /photo_"

    await add_photo_to_db_(session=session,
                           user_id_=user_id,
                           message_id=message_id,
                           photo_id=photo_id,
                           prefix=prefix,
                           is_answer=is_answer)
    return text_to_sheets


async def send_doc_to_tele_user(message: types.Message, manager: str, is_answer: bool, user_id: int,
                                session: AsyncSession):
    document_id = message.document.file_id
    prefix = f"🔸 [{manager}]: /doc_"
    text_to_sheets = "doc: " + document_id
    manager_message = await bot.send_document(user_id, document_id)
    message_id = manager_message.message_id
    await add_document_to_db_(session=session,
                              prefix=prefix,
                              user_id=user_id,
                              is_answer=is_answer,
                              message_id=message_id,
                              document_id=document_id, )
    return text_to_sheets


async def send_caption_to_tele_user(message: types.Message, user_id: int, session: AsyncSession,
                                    is_answer: bool, manager: str):
    manager_message = await bot.send_message(user_id, message.caption)
    message_id = manager_message.message_id
    safe_caption = quot_replacer(message.caption)
    time = datetime.datetime.now()
    caption_message = Message(message_body=safe_caption,
                              is_answer=is_answer,
                              storage_id=user_id,
                              message_id=message_id,
                              time=time)
    session.add(caption_message)


async def send_text_to_tele_user(message: types.Message, user_id: int, session: AsyncSession, is_answer: bool,
                                 manager: str):
    text_to_send = message.text
    text_to_sheets = text_to_send
    text_to_send = f"🔸 [{manager}]: " + text_to_send
    safe_text = quot_replacer(text_to_send)
    manager_message = await bot.send_message(user_id, text_to_send)
    manager_message_id = manager_message.message_id
    time = datetime.datetime.now()
    new_message = Message(message_body=safe_text,
                          is_answer=is_answer,
                          storage_id=user_id,
                          message_id=manager_message_id,
                          time=time)
    session.add(new_message)
    await session.flush()
    return text_to_sheets


async def from_manager_to_bot_way(message, user_id):
    user_id_ = int(user_id)
    target_id_message = message.reply_to_message.message_id
    manager = MANAGER.get(message.from_user.id)
    print('[WAY]', manager)

    async with AsyncSession(async_engine_bot) as session:
        async with session.begin():
            args = {'session': session, 'user_id': user_id_, 'manager': manager,
                    'is_answer': True, 'message': message}
            print(args)
            if message.caption:
                await send_caption_to_tele_user(**args)
            if message.content_type == 'photo':
                print('[INFO] photo branch ')
                text_to_sheets = await send_photo_to_tele_user(**args)
            elif message.content_type == 'document':
                print("[INFO] document branch ")
                text_to_sheets = await send_doc_to_tele_user(**args)
            elif message.content_type == 'text':
                print('[INFO] start text branch')
                text_to_sheets = await send_text_to_tele_user(**args)

            text_after_reply = await get_messages_from_base_last_5_g(user_id_, session)
            text2 = make_message_text(text_after_reply)
            text1 = get_mask_from_message(message.reply_to_message.text)
            response = await bot.send_message(message.chat.id,
                                              text=md.text(*text1, *text2, sep="\n"),
                                              parse_mode=ParseMode.HTML,
                                              reply_markup=get_keyboard_message_start())

            await bot.delete_message(message.chat.id, message.message_id)
            await bot.delete_message(message.chat.id, target_id_message)
            await session.commit()

    async with AsyncSession(async_engine_bot) as session:
        async with session.begin():
            stmt = update(User).values(message_id=response.message_id).where(User.user_id == user_id_)
            print(stmt.values)
            await session.execute(stmt)
            await session.commit()
    await send_to_googlesheets(manager, user_id_, text_to_sheets)


async def send_photo_to_web_user(session_bot: AsyncSession, session_chat: AsyncSession,
                                 manager: str,
                                 user_id: int,
                                 is_answer: bool,
                                 message: types.Message):
    photo_id = message.photo[-1].file_id
    text_to_sheets = "photo: " + photo_id
    prefix = f"{manager}: /photo_"

    command = await add_photo_to_db_(session=session_bot,
                                     user_id_=SUPER_WEB_USER,
                                     photo_id=photo_id,
                                     prefix=prefix,
                                     is_answer=is_answer)

    photo_path, mimi_type = await download_photo_or_document_to_server(incoming_file=photo_id, user_id=user_id,
                                                                       command=command)
    message_id = await save_photo_message_to_web_db(photo_path=photo_path, photo_command=command, user_id=user_id,
                                                    is_answer=is_answer, session=session_chat)

    now = datetime.datetime.now()
    # with open(photo_path, 'rb') as f:
    # file_content = f.read()
    # file_base64 = base64.b64encode(file_content).decode('utf-8')
    text = manager + ":" + photo_path  # manager+ : это костыль без чего то тоам + : работать не будет.
    # file = file_base64
    formatted_datetime = now.strftime("%B %d, %H:%M")
    data = {
        "event": "message",
        "name": manager,
        "details": {"message_id": message_id,
                    "is_answer": True,
                    "user_id": user_id,
                    "message_type": 'fastPhoto',
                    "time": formatted_datetime,
                    # "file": file,
                    # "mimi_type": mimi_type,
                    "user_name": manager,
                    "text": text,
                    "is_read": False
                    }
    }
    send_redis_mess_to_web(message=data)
    return data


async def send_doc_to_web_user(session_bot: AsyncSession, session_chat: AsyncSession,
                               manager: str,
                               user_id: int,
                               is_answer: bool,
                               message: types.Message):
    document_id = message.document.file_id
    prefix = f"{manager}: /doc_"
    text_to_sheets = "doc: " + document_id
    print('send_doc_to_web_user', document_id, prefix, text_to_sheets, sep=" | ")
    command = await add_document_to_db_(session=session_bot,
                                        prefix=prefix,
                                        is_answer=is_answer,
                                        user_id=SUPER_WEB_USER,
                                        document_id=document_id)
    document_path, mimi_type = await download_photo_or_document_to_server(incoming_file=document_id, user_id=user_id,
                                                                          command=command)
    message_id = await save_document_message_to_web_db(document_path=document_path, doc_command=command,
                                                       user_id=user_id,
                                                       is_answer=is_answer,
                                                       session=session_chat)

    now = datetime.datetime.now()
    # FIXME Это костыль без него сообщения не передать  надо ":"
    text = manager + ":" + document_path
    formatted_datetime = now.strftime("%B %d, %H:%M")

    data = {
        "event": "message",
        "name": manager,
        "details": {"message_id": message_id,
                    "is_answer": True,
                    "user_id": user_id,
                    "message_type": 'document',
                    "time": formatted_datetime,
                    "text": text,
                    "user_name": manager,
                    "is_read": False}
    }
    send_redis_mess_to_web(message=data)
    return data


async def send_text_to_web_user(session_chat: AsyncSession, session_bot: AsyncSession,
                                manager: str,
                                user_id: int,
                                is_answer: bool,
                                message: types.Message):
    text = f"{manager}: {message.text}"
    message_id = await save_text_message_to_db(session=session_chat, is_answer=True, text=text, user_web_id=user_id)
    await session_chat.commit()
    now = datetime.datetime.now()
    formatted_datetime = now.strftime("%B %d, %H:%M")

    data = {
        'event': 'message',
        'name': manager,
        'details': {'message_id': message_id,
                    'is_answer': True,
                    'user_id': user_id,
                    'message_type': 'text',
                    'time': formatted_datetime,
                    'text': text,
                    'user_name': manager,
                    'is_read': False}
    }

    send_redis_mess_to_web(message=data)

    try:
        count = await get_all_unread_message_count_by_web_user(user_id, session_chat)
        count_details = SupportDetails(count=count)
        count_message = SupportLoad(event='UnreadMessageCount',
                                    userID=user_id,
                                    userName=manager,
                                    details=count_details)
        send_message_to_support(count_message.model_dump_json())
    except Exception as ER:
        my_logger.error(f'problem in sending unread count to menu/etc {ER}')
    return data


async def send_notification_text_to_tele_user(session,
                                              user_id: int,
                                              text: str,
                                              time: datetime):

    manager_message = await bot.send_message(user_id, text, parse_mode=ParseMode.HTML)
    new_message = Message(message_body=text,
                          is_answer=True,
                          storage_id=user_id,
                          message_id=manager_message.message_id,
                          time=time)
    session.add(new_message)

    return manager_message


async def send_notification_text_to_web_user(session_chat: AsyncSession,
                                             manager: str,
                                             user_id: int,
                                             text: str):
    text = f"{manager}: {text}"
    message_id = await save_text_message_to_db(session=session_chat, is_answer=True, text=text, user_web_id=user_id)
    now = datetime.datetime.now()
    formatted_datetime = now.strftime("%B %d, %H:%M")
    data = {
        'event': 'message',
        'name': manager,
        'details': {'message_id': message_id,
                    'is_answer': True,
                    'user_id': user_id,
                    'message_type': 'text',
                    'time': formatted_datetime,
                    'text': text,
                    'user_name': manager,
                    'is_read': False}
    }
    send_redis_mess_to_web(message=data)
    try:
        count = await get_all_unread_message_count_by_web_user(user_id, session_chat)
        count_details = SupportDetails(count=count)
        count_message = SupportLoad(event='UnreadMessageCount',
                                    userID=user_id,
                                    userName=manager,
                                    details=count_details)
        send_message_to_support(count_message.model_dump_json())
    except Exception as ER:
        my_logger.error(f'problem in sending unread count to menu/etc {ER}')


async def download_photo_or_document_to_server(command: str | None,
                                               incoming_file: PhotoSize | Document | str,
                                               user_id) -> Tuple[str, str]:
    """ return document path and meme"""
    if command:
        command = command.replace('/', '').split(" ")[1]
        file = await bot.get_file(incoming_file)
        file_url = file.file_path
        downloaded_file = await bot.download_file(file_url)
        extension, mimi = get_mime_extension(downloaded_file)
        if "doc" in command:
            directory_prefix = "documents"
        elif "photo" in command:
            directory_prefix = "images"
        else:
            raise AssertionError("Unknown command", command)
    else:
        file_content = base64.b64decode(incoming_file)
        downloaded_file = io.BytesIO(file_content)
        extension, mimi = get_mime_extension(downloaded_file)
        directory_prefix = image_or_document(extension=extension)

    static_path = os.path.abspath('/my_static')
    salt = generate_salt()
    filename = f'{command}_{salt}{extension}'
    directory_path = os.path.join(directory_prefix, str(user_id))
    file_dir_to_create = os.path.join(static_path, directory_path)
    os.makedirs(file_dir_to_create, exist_ok=True)
    full_path = os.path.join(static_path, directory_path, filename)
    with open(full_path, 'wb') as f:
        f.write(downloaded_file.read())
    return full_path, mimi


async def send_caption_to_web_user(session_chat: AsyncSession, session_bot: AsyncSession,
                                   manager: str,
                                   user_id: int,
                                   is_answer: bool,
                                   message: types.Message):
    text = f"{manager}: {message.caption}"
    message_id = await save_text_message_to_db(session=session_chat, is_answer=True, text=text, user_web_id=user_id)
    now = datetime.datetime.now()
    formatted_datetime = now.strftime("%B %d, %H:%M")
    data = {
        'event': 'message',
        'name': manager,
        'details': {'message_id': message_id,
                    'is_answer': True,
                    'user_id': user_id,
                    'message_type': 'text',
                    'time': formatted_datetime,
                    'text': text,
                    'user_name': manager,
                    'is_read': False}
    }
    send_redis_mess_to_web(message=data)
    return data


async def from_manager_to_web_way(message, user_id):
    user_id_ = int(user_id)
    target_id_message = message.reply_to_message.message_id
    manager = MANAGER.get(message.from_user.id)
    async with AsyncSession(async_engine_bot) as session_bot:
        async with session_bot.begin():
            args = {'session_bot': session_bot,
                    'session_chat': session_bot,
                    'user_id': user_id_,
                    'manager': manager,
                    'is_answer': True,
                    'message': message}

        if message.content_type == 'photo':
            print('[INFO] photo branch ')
            message_dict = await send_photo_to_web_user(**args)
        elif message.content_type == 'document':
            print("[INFO] document branch ")
            print(message)
            message_dict = await send_doc_to_web_user(**args)
        elif message.content_type == 'text':
            print('[INFO] start text branch')
            message_dict = await send_text_to_web_user(**args)

        if message_dict:
            try:
                details = message_dict.get('details')
                message_id = details.get('message_id')
                await add_email_task(message_id)
            except Exception as ER:
                my_logger.error(f'problem in creating email task {ER}')
        if message.caption:
            caption_dict = await send_caption_to_web_user(**args)



        text_after_reply = await get_messages_from_web_db(user_id_, session_bot)
        text2 = make_message_text_w(text_after_reply)
        text1 = get_mask_from_web_message(message.reply_to_message.text, user_id)
        response = await bot.send_message(message.chat.id, text=md.text(*text1, *text2, sep="\n"),
                                          parse_mode=ParseMode.HTML,
                                          reply_markup=get_keyboard_message_start())

        await bot.delete_message(message.chat.id, message.message_id)
        await bot.delete_message(message.chat.id, target_id_message)

        stmt = update(WebUser).values(last_message_telegramm_id=response.message_id).where(WebUser.user_id == user_id_)
        await session_bot.execute(stmt)
        await session_bot.commit()



async def catch_messaging(message: types.Message):
    error_send_to = message.chat.id
    """Основная функция для отправления сообщений"""
    try:
        message.text = html.escape(message.text)
    except Exception as er:
        print(er)
    try:
        info = 'check way:'
        if message.chat.type in ['group', 'channel', 'supergroup'] and message.reply_to_message:
            way = find_the_way(message)
            if way.way == 'Telegram way':
                info = 'From managers, telegram way'
                await from_manager_to_bot_way(message=message, user_id=way.id)
            elif way.way == 'Web way':
                info = 'From managers, web way'
                await from_manager_to_web_way(message=message, user_id=way.id)
        # -----------------------------------------------------------------user part--------------------------------
        # ------------------------------------user part-------------------------------------------------------------
        elif message.chat.type in ['private']:
            error_send_to = alerts
            info = 'from user'
            answer = check_is_kazakhstan(message.from_user.id)
            if answer == True:
                chat_switch = kazakhstan_chat
            else:
                chat_switch = tradeinn_chat

            if chat_switch == tradeinn_chat:
                await bot.send_message(alerts,
                                       f"From {message.from_user.first_name} | {message.from_user.id} | Message")
            info = 'from user , create user'
            user_id = message.from_user.id
            user_name = message.from_user.first_name
            text_to_send = message.text
            safe_text = quot_replacer(text_to_send)
            value1 = f"INSERT INTO users (user_id, user_name, message_id) VALUES ({user_id},'{user_name}', NULL);"
            insert_to_base(value1)

            if message.caption:
                safe_caption = quot_replacer(message.caption)
                value2 = f"INSERT INTO messages (message_body,is_answer,storage_id,message_id) VALUES ('{safe_caption}',{False}, {user_id},{message.message_id});"
                insert_to_base(value2)

            if message.content_type == "photo":
                photo_telegram_id = message.photo[-1].file_id
                add_photo_to_bd(photo_telegram_id, user_id, message.message_id)
                text_to_sheets = "photo: " + photo_telegram_id

            elif message.content_type == 'document':
                doc_id = message.document.file_id
                add_doc_to_bd(doc_id, user_id, message.message_id)
                text_to_sheets = "doc: " + doc_id

            elif message.content_type == 'text':
                message_id = message.message_id
                value2 = f"INSERT INTO messages (message_body, is_answer, storage_id,message_id) VALUES ('{safe_text}', {False}, {user_id},{message_id});"
                insert_to_base(value2)
                text_to_sheets = safe_text

            # ФОРМИРУЕМ ТЕКСТ ДЛЯ ОТПРАВКИ СООБЩЕНИЯ:
            info = 'from user, create text for sending'
            message_list = get_messages_from_base_last_5(user_id)

            text = make_message_text(message_list)

            text_info = make_mask_to_messages(message, user_id)



            logging.info("[INFO] SEND FROM USER TO CHAT")
            # ОТПРАВЛЯЕМ СООБЩЕНИЕ В ГРУППУ
            print('TEXTS', text, text_info, sep='\n')
            response = await bot.send_message(chat_switch, md.text(
                text_info,
                md.text(*text, sep="\n"),
                sep="\n"),
                                              parse_mode=ParseMode.HTML,
                                              reply_markup=get_keyboard_message_start())
            await disappear_message_message_is_send(message)
            # СОХРАНЯЕМ ID отправленного сообщения ОНО НАМ ПОНАДОБИТСЯ ЧТО БЫ ПОТОМ БЫЛО ПОНЯТНО КАКОЕ СООБЩЕНИЕ УДАЛЯТЬ
            target_id = response.message_id

            # ВЫТАСКИВАЕМ СТАРЫЙ АЙДИ сообщения в группе ДЛЯ УНИЧТОЖЕНИЯ
            info = 'from user , killing old message'
            target = get_target_message(user_id)
            target = target[0][0]
            # УДАЛЯЕМ ПРОШЛОЕ СООБЩЕНИЕ И ОБНОВЛЯЕМ АЙДИ В БАЗЕ.
            if target:
                try:
                    await bot.delete_message(chat_switch, target)
                except Exception as er:
                    print(f"[INFO] cant to kill message, {er}")
            value = f"UPDATE users SET message_id = {target_id} WHERE user_id = {user_id}"
            insert_to_base(value)
            try:
                info = 'from user add to google sheets'
                await add_last_string(
                    [(str(datetime.datetime.now()), 'from user', message.from_user.id, text_to_sheets)],
                    'messages_storage')
            except Exception as ER:
                print(f"[ERROR] google sheets error in chat admins part : {ER}")
    except Exception as er:
        await bot.send_message(error_send_to, f"Unexpected error from catch messaging. In {info}. Error text : {er}")


async def open_long_history(callback_query: CallbackQuery):
    text_to_get_id = callback_query.message.text
    new_message = types.Message(reply_to_message=types.Message(text=callback_query.message.text))
    way: TheWay = find_the_way(new_message)
    print('The fucking way',way)
    if way.way == 'Telegram way':
        print('telegram way LONG HISTORY')
        user_id = way.id
        value = f"""SELECT is_answer,
                    TO_CHAR(time + INTERVAL '3 hours', '[dd-MM HH24:mi]') AS formatted_datetime,
                    message_body FROM messages WHERE storage_id={user_id} ORDER BY id DESC;"""
        text = get_from_base(value)
        text1 = get_mask_from_message(text_to_get_id)
        text2 = make_message_text_full(text)
        new_keyboard = types.InlineKeyboardMarkup(row_width=1)
        new_keyboard.add(types.InlineKeyboardButton("🔼", callback_data='fast_back_and_reload'))
    elif way.way == 'Web way':
        print('start web way LONG HISTORY')
        place = '1'
        user_id = int(way.id)
        pace = '2'
        history = await download_history(user_id=user_id, is_for_meeting_message=True)
        history_list = preparing_message_list(history)
        text2 = make_message_text_full_w(history_list)
        text1 = get_mask_from_web_message(text_to_get_id, user_id)
        new_keyboard = types.InlineKeyboardMarkup(row_width=1)
        new_keyboard.add(types.InlineKeyboardButton("🔼", callback_data='fast_back_and_reload'))
    else:
        raise TelegramHandlerError(chat_id=callback_query.message.chat.id,
                                   message="Не могу определить User ID из текста сообщения. Функция find_the_way "
                                           "вернула None")
    save_text = md.text(*text1, *text2, sep="\n")
    save_text = html.escape(save_text)
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=save_text,
        parse_mode=ParseMode.HTML
    )

    await bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=new_keyboard)


async def comeback_from_history(callback_query: CallbackQuery):
    text_to_get_id = callback_query.message.text
    new_message = types.Message(reply_to_message=types.Message(text=callback_query.message.text))
    way: TheWay = find_the_way(new_message)
    print(way)
    if way.way == 'Telegram way':
        user_id = get_id_from_text(text_to_get_id)
        text1 = get_mask_from_message(text_to_get_id)
        text = get_messages_from_base_last_5(user_id)
        text2 = make_message_text(text)
    elif way.way == 'Web way':
        print('start web way')
        user_id = int(way.id)
        history = await download_history(user_id=user_id, is_for_meeting_message=True, is_short_history=True)
        history_list = preparing_message_list(history)
        print(history_list)
        text2 = make_message_text_full_w(history_list)
        text1 = get_mask_from_web_message(text_to_get_id, user_id)

    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=md.text(*text1, *text2, sep="\n"),
        parse_mode=ParseMode.HTML
    )

    await bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=get_keyboard_menu_mess())


async def open_fast_answers(callback_query: CallbackQuery):
    print("[INFO] start open fast answers")
    match callback_query.data:
        case "fast_answers_choice":
            new_keyboard = get_keyboard_fast_answer_menu()
        case "message_menu":
            new_keyboard = get_keyboard_menu_mess()
        case 'fast_answers_list':
            print('[INFO] open_fast_answers: answer_list_branch')
            user_id = callback_query.from_user.id
            type_keyboard = "answer"
            new_keyboard = get_keyboard_answers_list(type_keyboard, user_id)
        case 'fast_cards_list':
            print('[INFO] open_fast_answers: card_list_branch')
            user_id = callback_query.from_user.id
            type_keyboard = 'card'
            new_keyboard = get_keyboard_answers_list(type_keyboard, user_id)
    await bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=new_keyboard)
    await bot.answer_callback_query(callback_query.id, " ")


async def come_back(callback_query: CallbackQuery):
    new_keyboard = get_keyboard_message_start()
    await bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=new_keyboard)
    await bot.answer_callback_query(callback_query.id, " ")


async def ban(callback_query: CallbackQuery):
    await callback_query.answer("Пока не работает")


async def send_fast_answer_to_user(callback_query: CallbackQuery):
    id = callback_query.data.split("_")[1]

    value = f"SELECT body FROM fast_answers WHERE id = {id};"
    text = get_from_base(value)[0][0]
    manager = MANAGER.get(callback_query.from_user.id)
    text = f"🔸 [{manager}]: " + text
    target_message_id = callback_query.message.message_id
    message_text = callback_query.message.text
    user_id = get_id_from_text(message_text)
    value = f"UPDATE users SET message_id = {target_message_id} WHERE user_id = {user_id};"  # обновляем айди сообщения в базе
    insert_to_base(value)
    value = f"INSERT INTO messages (message_body,is_answer,storage_id) VALUES ('{text}',{True},{user_id});"
    insert_to_base(value)
    await bot.send_message(user_id, text)
    text1 = get_mask_from_message(message_text)
    text0 = get_messages_from_base_last_5(user_id)
    text2 = make_message_text(text0)

    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=md.text(*text1, *text2, sep="\n"),
        parse_mode=ParseMode.HTML,
        reply_markup=get_keyboard_message_start()
    )
    print(target_message_id, message_text, sep="\n")
    await callback_query.answer("успешно")


async def is_answered(query: CallbackQuery):
    """метит основное сообщение зеленой меткой и сохраняет ответ в бд но не шлет пользователю."""
    # ИЗ этого текста вытаскивается id
    user_id_ = get_id_from_text(query.message.text)
    value1 = f"UPDATE users SET message_id = {query.message.message_id} WHERE user_id = {user_id_};"
    manager = MANAGER.get(query.from_user.id)
    if query.data == 'is_answered':
        text_to_send = "Завершено"
        is_answer = True
    elif query.data == 'is_not_answered':
        text_to_send = "Требует внимания"
        is_answer = False
    elif query.data == 'thanks':
        text_to_send = "🙏🙏🙏"
        is_answer = True
    else:
        print("[ERROR] querry data в is_answered пришла странная is_answered | is_not_answered", query.data)
    text_to_send = f"🔸 [{manager}]: " + text_to_send
    safe_text = quot_replacer(text_to_send)
    value2 = f"INSERT INTO messages (message_body,is_answer,storage_id) VALUES ('{safe_text}',{is_answer},{user_id_});"
    insert_to_base(value1 + value2)
    print('[INFO]', 'Bot send message to', user_id_, "text: ", text_to_send)
    text_after_reply = get_messages_from_base_last_5(user_id_)
    text2 = make_message_text(text_after_reply)
    text1 = get_mask_from_message(query.message.text)
    logging.info("[INFO] SEND FROM USER TO CHAT")
    chat_id = query.message.chat.id

    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=query.message.message_id,
        text=md.text(*text1, *text2, sep="\n"),
        parse_mode=ParseMode.HTML,
        reply_markup=get_keyboard_message_start()
    )


async def change_channel(query: CallbackQuery):
    user_id = get_id_from_text(query.message.text)
    print(f"[INFO] [start] change_channel  {user_id}")
    value = f"SELECT user_name, user_second_name,tele_username,is_kazakhstan FROM users WHERE user_id={user_id};"
    query_set = get_from_base(value)[0]
    before_answer = query_set[3]
    print('answer before', before_answer)
    if before_answer:
        answer = False
    else:
        answer = True
    print('answer after', answer)
    value = f"UPDATE users SET  is_kazakhstan = '{answer}' WHERE user_id = {user_id};"
    insert_to_base(value)
    new_message = create_new_message_change(query, user_id, query_set)
    await catch_messaging(new_message)
    await query.answer(query_set)
    await query.message.delete()
    before_chat = f"Error: before {before_answer}"
    after_chat = f"Error : after {answer}"

    if before_answer:
        before_chat = "KAZAKHSTAN"
    elif before_answer == False:
        before_chat = "TRADEINN"
    elif before_answer is None:
        before_chat = "TRADEINN"

    if answer:
        after_chat = "KAZAKHSTAN"
    elif answer == False:
        after_chat = "TRADEINN"

    await bot.send_message(query.message.chat.id, md.text(
        md.text("Администратор:", query.from_user.first_name),
        md.text("🥾⚽️ пользователя: ", user_id),
        md.text("Который раньше находился в чате :", before_chat),
        md.text("В чат: ", after_chat),
        sep="\n"
    ))

async def thanks_message(query: CallbackQuery):
    await is_answered(query)
    user_id = get_id_from_text(query.message.text)
    await query.answer("Успешно")
    await bot.send_message(user_id, thank_u())


async def extract_full_history(query: CallbackQuery):
    await query.answer("Full History")
    way = find_the_way(query.message.text, text_mode=True)
    if way.way == 'Telegram way':
        print("TELEGRAM WAY LONG HISTORY")
        user_id = way.id
        stmt = f"""SELECT
                id,
                TO_CHAR(time + INTERVAL '3 hours', 'dd-MM-YY HH24:mi') AS formatted_datetime,
                message_body 
                FROM messages
                WHERE storage_id = {user_id}
                ORDER BY id DESC;"""
        queryset = get_from_base(stmt)
        string = f"Клиент: {user_id} \n"
        for line in queryset:
            line_str = list(map(str, line))
            string += " ".join(line_str) + '\n'
        file = io.BytesIO(string.encode('utf-8'))
        file.name = f'history.txt'
        document_message = await bot.send_document(chat_id=query.message.chat.id, document=file,
                                                   caption=markdown.text("История"))
        file.close()
    elif way.way == 'Web way':
        print('WEB WAY LONG HISTORY')
        user_id = int(way.id)
        history, username = await download_history(user_id=user_id, is_for_meeting_message=False, with_name_mode=True)
        string = f"Клиент: {username} \n"
        string += f"Web ID: {user_id} \n"
        string += f"История сообщений, всего {len(history)} \n"
        for line in history:
            pymod: MessageDetails = line
            string += (f"{pymod.message_id} | {pymod.time} |"
                       f" {pymod.text} | {pymod.is_answer} | {pymod.is_read} | {pymod.message_type} \n")
        file = io.BytesIO(string.encode('utf-8'))
        file.name = f'history.txt'
        document_message = await bot.send_document(chat_id=query.message.chat.id, document=file,
                                                   caption=markdown.text("Web История"))
    try:
        await asyncio.sleep(5 * 60)
        await document_message.delete()
    except:
        return


def register_handlers_warning(dp: Dispatcher):
    dp.register_callback_query_handler(come_back, lambda c: c.data == 'fast_back')
    dp.register_callback_query_handler(open_fast_answers, lambda c: c.data in (
        'fast_answers_choice', 'fast_cards_list', 'fast_answers_list', 'message_menu'))
    dp.register_callback_query_handler(comeback_from_history, lambda c: c.data == 'fast_back_and_reload')
    dp.register_callback_query_handler(open_long_history, lambda c: c.data == 'long_history')
    dp.register_callback_query_handler(extract_full_history, lambda c: c.data == 'full_history')
    dp.register_callback_query_handler(is_answered, lambda c: c.data in ('is_answered', 'is_not_answered'))
    dp.register_callback_query_handler(ban, lambda c: c.data == 'ban')
    dp.register_message_handler(catch_messaging, content_types=['text', 'photo', 'document'], )
    dp.register_callback_query_handler(send_fast_answer_to_user, Regexp('answer_([0-9]*)|card_([0-9]*)'))
    dp.register_callback_query_handler(thanks_message, lambda c: c.data == 'thanks')
    dp.register_callback_query_handler(change_channel, lambda c: c.data == 'change_channel')
