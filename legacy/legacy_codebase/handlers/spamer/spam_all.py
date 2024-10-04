import asyncio
from aiogram.types import ParseMode
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from base.models import Message, User
from create_bot import bot
from handlers.spamer.spam_logs import spam_logger
from utils.config import async_engine_bot
from utils.texts import spammer_text_poshlina, spammer_text_poshlina2


async def get_all_user():
    async with AsyncSession(async_engine_bot) as session:
        async with session.begin():
            stmt = select(User)
            result = await session.execute(stmt)
            users = result.scalars()
            clients = [user.user_id for user in users]
    return clients


async def lets_spam_starts(clients):
    text = spammer_text_poshlina2()
    success_count = 0
    fail_count = 0
    total = 1
    async with AsyncSession(async_engine_bot) as session:
        async with session.begin():
            for client in clients:
                print(f'{total} send to {client}')
                try:
                    result = await bot.send_message(client, text, parse_mode=ParseMode.MARKDOWN)
                    spam_logger.info(str(result))
                    await asyncio.sleep(0.3)
                    stmt = insert(Message).values(message_body=text,
                                                  is_answer=True,
                                                  storage_id=client,
                                                  message_id=result.message_id)
                    await session.execute(stmt)
                    spam_logger.info(f'success with client {client}')
                    success_count += 1
                except Exception as er:
                    spam_logger.info(f'fail with client {client}')
                    fail_count += 1
                    print(er)
                total += 1
    print({'success': success_count, 'fails': fail_count, 'total': total})
    return


async def asymain():
    clients = await get_all_user()
    print(clients)
    print('[Длинна]', len(clients))
    await lets_spam_starts(clients)


def spammer_task_21_02_2024():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asymain())
    loop.close()

def spammer_task_08_04_2024():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asymain())
    loop.close()


async def try_to_send_fedor():
    await bot.send_message(chat_id=716336613,text=spammer_text_poshlina2(), parse_mode=ParseMode.MARKDOWN)


