import asyncio
import html
import json
import datetime
from typing import Tuple
import aiogram.utils.markdown as md
from aiogram.types import Message, ParseMode
from base.good_db_handlers import collect_web_meta_by_id
from create_bot import bot
from handlers.chat.reload_media import init_conversation
from module_7.base.db_handlers import is_kazakhstan_chat, save_message_id_to_user, download_history, get_message_id, get_name_from_db
from module_7.bot.menu import get_keyboard_message_start
from module_7.bot.texts import make_mask_to_web_messages, make_message_text
from logs.logs import my_logger
from sheets.add_orders import add_last_string
from utils.config import kazakhstan_chat, tradeinn_chat, alerts, orders_chat_storage
from utils.texts import make_message_text_w


async def check_user_chat(user_id: int) -> int:
    result = await is_kazakhstan_chat(user_id)
    if result:
        chat = kazakhstan_chat
    else:
        chat = tradeinn_chat
    return chat


async def get_telegram_photo_or_document_id(file_path) -> Tuple[str, str]:
    """Send to telegram channel and get telegram id"""
    my_logger.debug(f'start filepath {file_path}')
    if '/documents/' in file_path:
        title = "/" + 'doc' + "_"
        response = await bot.send_document(chat_id=kazakhstan_chat, document=open(file_path, 'rb'))
        await asyncio.sleep(2)
        document_id = response.document.file_id
        result_id = document_id
    elif '/images/' in file_path:
        title = "/" + 'photo' + "_"
        response = await bot.send_photo(chat_id=kazakhstan_chat, photo=open(file_path, 'rb'))
        await asyncio.sleep(2)
        photo_id = response.photo[-1].file_id
        result_id = photo_id
    else:
        raise AssertionError('in get_telegram_photo_id Unexpected type of file')
    await bot.delete_message(response.chat.id, response.message_id)
    return result_id, title


async def update_meeting_message_web(user_id):
    history, username = await download_history(user_id=user_id,
                                               is_for_meeting_message=True,
                                               with_name_mode=True)
    print('[INFO-O-O]', username)
    my_logger.debug(f"start create message with {username}")
    history = history[:5]
    history_prep = [(mes.is_answer, mes.text, mes.is_read) for mes in history]

    mask = await make_mask_to_web_messages(user_id=user_id, user_name=username)
    text = make_message_text_w(history_prep)
    text_to_send = md.text(mask, *text, sep='\n')
    chat = await check_user_chat(user_id=user_id)
    old_message_id = await get_message_id(user_id)
    if old_message_id:
        try:
            await bot.delete_message(chat, old_message_id)
        except:
            my_logger.debug('cant to delete message')
    message: Message = await bot.send_message(chat, text_to_send, parse_mode=ParseMode.HTML,
                                              reply_markup=get_keyboard_message_start())
    if message:
        await save_message_id_to_user(message.message_id, user_id)


async def update_meeting_message_telegram(user_id):
    await init_conversation(regexp_command=user_id, message=False, is_integers=True)


async def send_meeting_message_to_bot(user_id, user_name, full_history=False):
    """WEB создает текст сообщения,
    вытаскивает, старый номер сообщения
    пытается его удалить
    отсылает новое сообщение
    """
    my_logger.debug(f'start user_id = {user_id} username={user_name} and isFullHistory={full_history}')
    history = await download_history(user_id=user_id, is_for_meeting_message=True)
    print('[AMASSING DEBUG 1]')
    if not full_history:
        print('[AMASSING DEBUG 2]')
        history = history[:5]
        history_prep = [(mes.is_answer, mes.text,) for mes in history]
        mask = await make_mask_to_web_messages(user_id=user_id, user_name=user_name)
        text = make_message_text(history_prep)
        text_to_send = md.text(mask, *text, sep='\n')
        print(text_to_send)
        chat = await check_user_chat(user_id=user_id)
        print('[AMASSING DEBUG 3]')
    else:
        return

    try:
        print('[AMASSING DEBUG 4]')
        old_message_id = await get_message_id(user_id)
        if old_message_id:
            try:
                await bot.delete_message(chat, old_message_id)
            except:
                print('not')
        message: Message = await bot.send_message(chat, text_to_send, parse_mode=ParseMode.HTML,
                                                  reply_markup=get_keyboard_message_start())
        if message:
            await save_message_id_to_user(message.message_id, user_id)
    except Exception as ER:
        my_logger.error(f'sending message or saving to db error {ER}')


async def create_meeting_message_from_web(bytes_string):
    try:
        string = bytes_string.decode('utf-8').replace("'", '"')
        my_data = json.loads(string)
        user_id = my_data.get('user_id')
        user_name = await get_name_from_db(user_id)
        history = await download_history(user_id)
        history = history[:5]
        history_prep = [(mes.get('is_answer'), mes.get('body'),) for mes in history]
        mask = await make_mask_to_web_messages(user_id, user_name)
        text = make_message_text(history_prep)
        text_to_send = md.text(mask, *text, sep='\n')
        chat = await check_user_chat(user_id)
    except Exception as ER:
        my_logger.error(f"preparing text error {ER}")
        return
    try:
        old_message_id = await get_message_id(user_id)
        if old_message_id:
            try:
                await bot.delete_message(chat, old_message_id)
            except:
                print('not')
        message: Message = await bot.send_message(chat, text_to_send, parse_mode=ParseMode.HTML,
                                                  reply_markup=get_keyboard_message_start())
        if message:
            await save_message_id_to_user(message.message_id, user_id)
    except Exception as ER:
        my_logger.error(f'sending message or saving to db error {ER}')


async def send_order_alert_bot(user,
                               web_user_id,
                               order,
                               order_details,
                               is_reload=False):
    print(order_details, user)
    order_details = order_details.model_dump()
    if is_reload:
        chat_id = kazakhstan_chat
    else:
        chat_id = orders_chat_storage
    try:
        details = [md.text(f"#{order}"), md.text(f"Type: WEB_ORDER")]
        place = 'here one'
        if user:
            place = 'we have a user'
            details.append(md.text("User WEB: ", user))
            items = order_details.get('items')
            count = 1
            for key, value in items.items():
                quantity = value.get('amount')
                comment = value.get('comment')
                quantity = str(quantity) + " шт."
                url = html.escape(value.get('url'))
                row = f'<a href="{url}">item-{count}</a>'
                details.append(md.text(row, quantity, comment, sep=' '))
                count += 1
            place = 'added md.text(row);'
            user_meta = await collect_web_meta_by_id(web_user_id)
            details.append(md.text(" "))
            details.append(md.text('[USER META]'))
            if user_meta:
                for row in user_meta:
                    key, value = row.popitem()
                    details.append(md.text(key, value, sep=" "))
        else:
            if not user:
                user = "Unregistered User"
                details.append(md.text("User WEB: ", user))
            for key, value in order_details.items():
                details.append(md.text(f"{key}:", f"<code>{value}</code>", sep=" "))
        text = md.text(*details, sep="\n")
    except Exception as er:
        print(f'UNEXPECTED ERROR in preparing text {er} ')
        return
    try:
        print('[TRY TO SEND BOT')
        result = await bot.send_message(chat_id, text=text, parse_mode=ParseMode.HTML,
                                        disable_web_page_preview=True)
        print('SUCCESS send to bot', result)
    except Exception as er:
        print(f'[ERROR] expected error in bot send alert {er}')

    if is_reload:
        return
    try:
        print('[TRY TO SEND TO SHEETS]', order, user, str(datetime.date.today()), str(text))
        result = await add_last_string([(order, user, str(datetime.date.today()), "WEB_ORDER", str(text))], 'Dashboard')
        print('[SUCCESS SEND TO SHEETS]', result)
    except Exception as er:
        print(f"[ERROR] problem with sending to sheets {er}")
