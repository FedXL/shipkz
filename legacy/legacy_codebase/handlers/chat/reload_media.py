import asyncio
from typing import Union

from aiogram import types, Dispatcher
from aiogram.dispatcher import filters
from aiogram.types import ParseMode, Message, ChatType, User
import aiogram.utils.markdown as md
from base.base_connectors import get_from_base, get_messages_from_base_last_5, insert_to_base
from base.good_db_handlers import get_web_user_info
from create_bot import bot
from handlers.chat.sender import get_keyboard_message_start
from module_7.base.db_handlers import download_history
from utils.texts import make_message_text, make_mask_to_messages, make_message_text_w, \
    make_mask_to_messages_w, preparing_for_message_5list
from utils.config import ADMINS, kazakhstan_chat
from utils.utils_lite import disappear_message


async def photo_reloader(message: types.Message, regexp_command):
    print('[INFO] photo reloader start')
    message_id = regexp_command.group(1)
    await bot.delete_message(message.chat.id, message.message_id)
    try:
        value = f"SELECT file_id FROM photos WHERE message_id = {message_id};"
        photo = get_from_base(value)[0][0]
        photo_message = await bot.send_photo(message.chat.id, photo)
    except Exception as ER:
        print(f'[ERROR] photo_reloader: {ER}')
        photo_message = await bot.send_message(message.chat.id, 'Фотография не найдена')
    await disappear_message(photo_message)


async def document_reloader(message: types.Message, regexp_command):
    print('[INFO] document reloader start')
    message_id = regexp_command.group(1)
    await bot.delete_message(message.chat.id, message.message_id)
    try:
        value = f"SELECT document_id FROM documents WHERE message_id = {message_id};"
        document = get_from_base(value)[0][0]
        document_message = await bot.send_document(message.chat.id, document)
    except Exception as ER:
        print(f'[ERROR] document_reloader: {ER}')
        document_message = await bot.send_message(message.chat.id, 'Документ не найден')
    await disappear_message(document_message)


async def disappear_message_abstract(message: types.Message):
    await asyncio.sleep(5)
    await bot.delete_message(message.chat.id, message.message_id)


async def init_conversation(message: Union[types.Message, bool], regexp_command, is_integers=False):
    if is_integers:
        print('[telegram way] from int')
        chat_id = kazakhstan_chat
        user_id = regexp_command
    else:
        print('[telegram way] from message')
        user_id = regexp_command.group(1)
        chat_id = message.chat.id

    insert_get_info = f"SELECT user_name, user_second_name, tele_username, message_id FROM users WHERE user_id = {user_id};"
    user_info = get_from_base(insert_get_info)

    if not user_info:
        await bot.send_message(chat_id, f"Такого пользователя {user_id} нет в базе данных")
        return
    else:
        user_info = user_info[0]
    try:
        info = 'in message list'
        message_list = get_messages_from_base_last_5(user_id)
        info = 'in make_message_text'
        text = make_message_text(message_list)
        info = 'in new_message create'
        new_message = Message(chat_id=chat_id, chat=ChatType())
        new_message.from_user = User(alias='from', base=User)
        new_message.from_user.first_name = user_info[0]
        new_message.from_user.last_name = user_info[1]
        new_message.from_user.username = user_info[2]
        target_to_delete = user_info[3]
        info = ' in make_mask to messages'
        text_info = make_mask_to_messages(new_message, user_id)
        info = ' in bot.send_message()'
        response = await bot.send_message(chat_id,
                                          md.text(text_info,
                                                  md.text(*text, sep="\n"),
                                                  sep="\n"),
                                          parse_mode=ParseMode.HTML,
                                          reply_markup=get_keyboard_message_start()
                                          )
        target_id = response.message_id
        stmt2 = f"UPDATE users SET message_id = {target_id} WHERE user_id = {user_id}"
        insert_to_base(stmt2)
    except Exception as er:
        await bot.send_message(chat_id, f"Unexpected Error {info} : {er}")
        print('[INFO message]')
        return
    try:
        await bot.delete_message(chat_id=chat_id, message_id=int(target_to_delete))
    except Exception as er:
        print('cant to delete')


async def init_conversation_web(message: types.Message, regexp_command):
    print('[web way]')
    info = None
    user_id = regexp_command.group(1)
    user = await get_web_user_info(user_id)

    if not user:
        await bot.send_message(message.chat.id, f"Такого пользователя {user_id} нет в базе данных")
        return
    try:
        user_id = int(user_id)
        info = 'in message list'
        info = 'in make_message_text'
        history = await download_history(user_id=user_id, is_for_meeting_message=True, is_short_history=True)
        for hist in history:
            print(hist)
        history_list = preparing_for_message_5list(history)
        text = make_message_text_w(history_list)
        info = 'in new_message create'
        new_message = Message(chat_id=message.chat.id, chat=ChatType())
        new_message.from_user = User(alias='from', base=User)
        new_message.from_user.first_name = None
        new_message.from_user.last_name = None
        new_message.from_user.username = user.web_username
        info = ' in make_mask to messages'
        text_info = make_mask_to_messages_w(new_message, user_id)
        info = 'in sending message'
        await bot.send_message(message.chat.id, md.text(
            text_info,
            md.text(*text, sep="\n"),
            sep="\n"),
                               parse_mode=ParseMode.HTML,
                               reply_markup=get_keyboard_message_start())

    except Exception as er:
        await bot.send_message(message.chat.id, f"Unexpected Error {info} : {er}")


async def init_links(message: types.Message, regexp_command):
    user_id = regexp_command.group(1)
    print("INFO order init links message", user_id)
    insert_get_info = f"SELECT user_name,user_second_name,tele_username FROM users WHERE user_id = {user_id};"
    user_info = get_from_base(insert_get_info)
    print(message.from_user.id)
    if message.from_user.id not in ADMINS:
        await message.answer("Нет доступа к операции")
        return
    if not user_info:
        await bot.send_message(message.chat.id, f"Такого пользователя {user_id} нет в базе данных")
        return
    else:
        user_info = user_info[0]
    first_name = user_info[0]
    last_name = user_info[1]
    username = user_info[2]
    text = md.text(
        md.text(first_name),
        md.text(last_name),
        md.text(f"@{username}"),
        md.text(md.hlink(f"#ID_{user_id}", f"tg://user?id={user_id}")),
        sep="\n"
    )
    links_message = await bot.send_message(message.chat.id, text, parse_mode=ParseMode.HTML)
    await disappear_message(links_message)


def register_reload_media(dp: Dispatcher):
    dp.register_message_handler(photo_reloader, filters.RegexpCommandsFilter(regexp_commands=['photo_([0-9]*)']))
    dp.register_message_handler(document_reloader, filters.RegexpCommandsFilter(regexp_commands=['doc_([0-9]*)']))
    dp.register_message_handler(init_conversation_web, filters.RegexpCommandsFilter(regexp_commands=['wtalk_([0-9]*)']))
    dp.register_message_handler(init_conversation, filters.RegexpCommandsFilter(regexp_commands=['talk_([0-9]*)']))
    dp.register_message_handler(init_links, filters.RegexpCommandsFilter(regexp_commands=['link_([0-9]*)']))
