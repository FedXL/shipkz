import asyncio
import mimetypes
import secrets
import string
from datetime import datetime
from typing import BinaryIO, Tuple
import magic
from aiogram import types
from aiogram.types import CallbackQuery, User, ChatType, Message
from base.base_connectors import insert_to_base
from create_bot import bot
from module_7.handlers.pydentic_models import MessageLoad
from utils.config import MANAGER, SUPPORT_IMAGE_EXTENSION, SUPPORT_DOCUMENTS_EXTENSION


def ShopValid(text: str) -> bool:
    try:
        new_text = int(text)
        return False
    except ValueError:
        pass
    if len(text) > 150:
        return False
    return True


def create_counter():
    i = 0

    def func():
        nonlocal i
        i += 1
        return i

    return func


def is_number(str):
    try:
        float(str)
        return True
    except ValueError:
        return False


def quot_replacer(text):
    try:
        text = text.replace("'", "''")
    except Exception as ER:
        print(ER)
    return text


def create_new_message_order(query: CallbackQuery, texts, order_id):
    texts = texts + f" /order_{order_id}"
    new_message = Message(chat_id=query.message.chat.id, text=texts, chat=ChatType())
    new_message.chat.type = 'private'
    new_message.from_user = User(alias='from', base=User)
    new_message.from_user.id = query.from_user.id
    new_message.from_user.first_name = query.from_user.first_name
    new_message.from_user.last_name = query.from_user.last_name
    new_message.from_user.username = query.from_user.username
    new_message.message_id = 000000
    new_message.chat.id = False
    return new_message


def create_new_message_change(query: CallbackQuery, user_id, query_set: list):
    manager = MANAGER.get(query.from_user.id)
    texts = f"🥾⚽️🧍 от {manager}"
    new_message = Message(chat_id=query.message.chat.id, text=texts, chat=ChatType())
    new_message.chat.type = 'private'
    new_message.from_user = User(alias='from', base=User)
    new_message.from_user.id = user_id
    new_message.from_user.first_name = query_set[0]
    new_message.from_user.last_name = query_set[1]
    new_message.from_user.username = query_set[2]
    new_message.chat.id = False
    new_message.message_id = 000000
    return new_message


async def disappear_message_message_is_send(message: types.Message):
    # Send the message
    if message.chat.id:
        sent_message = await bot.send_message(message.chat.id, '🔸Ваше сообщение отправлено🔸')
        # Delete the message after 5 seconds
        await asyncio.sleep(4)
        await bot.delete_message(message.chat.id, sent_message.message_id)


async def disappear_message_thanks_is_send(message: types.Message, send_to: str):
    if message.chat.id:
        send_message = await bot.send_message(message.chat.id, f'🙏🙏 отправлено , {send_to}')
        await asyncio.sleep(4)
        await bot.delete_message(message.chat.id, send_message.message_id)


def add_managers():
    from utils.config import MANAGER
    for user_id, short_name in MANAGER.items():
        stmt = f"INSERT INTO managers (short_name, user_id) VALUES ('{short_name}',{user_id});"
        insert_to_base(stmt)


async def disappear_message(message: types.Message, timer=5 * 60):
    await asyncio.sleep(timer)
    try:
        await message.delete()
    except:
        return


def generate_salt(length=25):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def update_time_to_custom_format(details_instance: MessageLoad):
    current_time = datetime.fromisoformat(details_instance.details.time)
    new_time_format = current_time.strftime("%B %d, %H:%M")
    details_instance.details.time = new_time_format


def get_mime_extension(file_content: BinaryIO) -> Tuple[str, str]:
    m = magic.Magic(mime=True)
    mimi = m.from_buffer(file_content.getvalue())
    mimetypes.init()
    extension = mimetypes.guess_extension(mimi)
    print('[FILE EXTENSION MIMI]', extension, mimi)
    return extension, mimi


def image_or_document(extension: str) -> str | bool:
    if extension in SUPPORT_IMAGE_EXTENSION:
        print('IT is the IMAGE')
        it_is = 'images'
    elif extension in SUPPORT_DOCUMENTS_EXTENSION:
        it_is = 'documents'
        print('IT is the Document')
    else:
        raise AssertionError(f'IM NOT SUPPORT {extension} sorry. [check support image extension and support documents '
                             f'extension in utils/config]')
    return it_is
