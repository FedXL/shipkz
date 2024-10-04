import asyncio
import datetime
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from base.good_db_handlers import get_all_teleusers
from base.models import Message
from create_bot import bot
from aiogram.types import ParseMode
from handlers.spamer.spam_logs import spam_logger
from utils.config import engine, async_engine_bot
from utils.texts import make_no_discount_text, make_discount_text, make_friday_text, make_friday_mistakes, \
    make_crypto_text


async def send_discount(user, text):
    await bot.get_session()
    result = await bot.send_message(user, text, parse_mode=ParseMode.HTML)
    session = await bot.get_session()
    await session.close()
    print(result)
    return result


async def send_crypto_main():
    users = await get_all_teleusers()
    photo_id = "AgACAgIAAxkBAAED8DBm369Dwo4OZeQbOlArOa4wcCC4PwACcuoxG4J2-EoisQ4D1slbZgEAAwIAA3gAAzYE"
    caption_text = make_crypto_text()
    error_count = 0
    success_count = 0
    await bot.get_session()
    for user in users:
        await asyncio.sleep(0.1)
        try:
            result = await bot.send_photo(user, photo=photo_id, caption=caption_text, parse_mode=ParseMode.HTML)

            async with AsyncSession(async_engine_bot) as session:
                async with session.begin():
                    stmt = insert(Message).values(message_body=caption_text,
                                                  is_answer=True,
                                                  storage_id=user,
                                                  message_id=result.message_id)
                    await session.execute(stmt)
            spam_logger.info(f'success: {result}')
            success_count += 1
        except Exception as er:
            print(f'fail {er}')
            spam_logger.warning(f"fail: {er} ")
            error_count += 1
    session = await bot.get_session()
    await session.close()
    spam_logger.info(f'end of spacing successfully send : {success_count} unsuccessful send: {error_count}')






async def main_crypto_starter():
    try:
        await send_crypto_main()
    except Exception as e:
        spam_logger.exception(f"Error occurred: {e}")
    pass



def safe_message(session: Session(), data):
    print('start')
    message_id = data.message_id
    user_id = data.chat.id
    text = data.text
    time = datetime.datetime.now()
    stmt = insert(Message).values(message_body=text,
                                  is_answer=True,
                                  storage_id=user_id,
                                  time=time,
                                  message_id=message_id)
    session.execute(stmt)
    session.commit()

