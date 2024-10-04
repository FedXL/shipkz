import asyncio
from aiogram.types import ParseMode
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from base.models import Order, Message
from create_bot import bot
from handlers.spamer.spam_logs import spam_logger
from utils.config import async_engine_bot

PHOTO_ID = 'AgACAgIAAxkBAAEDp-lme8cxSMg2SXjGwBLuQ2ZvsoPJ6AACqtoxGxsR2UuTQ8MuktzEOgEAAwIAA3kAAzUE'

def make_60_text():
    """Ловите летнюю распродажу на tradeinn.com! Скидки до 60%.  Проверьте свой вишлист, на одежду и обувь при распродажах обычно весьма приличные скидки."""
    text = (f"Ловите летнюю распродажу на tradeinn.com\n"
            f"<b>Скидки до 60%.</b>\n"
            f"Проверьте свой вишлист, на одежду и обувь, при распродажах обычно весьма приличные скидки.")
    return text


async def get_users_id() -> set:
    print('[start get_users]')
    async with AsyncSession(async_engine_bot) as session:
        async with session.begin():
            stmt = select(Order).where(Order.type == 'TRADEINN')
            result = await session.execute(stmt)
            result = result.scalars()
            result_list = [order.client for order in result]
            clients = set(result_list)
    return clients


async def send_60_summer():
    users = [716336613]
    photo_id = PHOTO_ID
    caption_text = make_60_text()
    error_count = 0
    success_count = 0
    await bot.get_session()
    for user in users:
        await asyncio.sleep(1)
        try:
            result = await bot.send_photo(user, photo=photo_id, caption=caption_text, parse_mode=ParseMode.HTML)
            iddd = int(result.message_id)
            async with AsyncSession(async_engine_bot) as session:
                async with session.begin():
                    stmt = insert(Message).values(message_body=caption_text,
                                                  is_answer=True,
                                                  storage_id=user,
                                                  message_id=iddd)
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



