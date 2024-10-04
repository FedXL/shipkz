import asyncio
from aiogram.types import ParseMode
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from base.models import Order, OrderStatus, Message
from create_bot import bot
from handlers.spamer.spam_logs import spam_logger
from utils.config import async_engine_bot
import aiogram.utils.markdown as md


async def get_users_id():
    print('[start get_users]')
    async with AsyncSession(async_engine_bot) as session:
        async with session.begin():
            stmt = select(OrderStatus).where(OrderStatus.order_price.isnot(None))
            result = await session.execute(stmt)
            statuses = result.scalars()
            order_ids = [status.order_id for status in statuses if status.order_id > 1651]
            print(len(order_ids))
            stmt2 = select(Order).where(Order.id.in_(order_ids)).order_by(Order.id)
            result = await session.execute(stmt2)
            orders = result.scalars()
            clients = [order.client for order in orders]
            clients = set(clients)
    return clients


def spammer_text():
    text = md.text(
        md.text("<b>Конкурс распаковок!</b>"),
        md.text(" "),
        md.text("Главный приз сертификат на 100 евро при заказе через наш сервис и каждый участник получит скидку "
                "1000 руб. на следующий заказ."),
        md.text(' '),
        md.text("Для участия в конкурсе необходимо оставить видео в комментариях к посту."),
        md.text(' '),
        md.text("Конкурс продлится до 28 февраля. В конце бот рандомно определит победителя."),
        md.text(" "),
        md.text("<a href='https://t.me/shipKZ/453'>Конкурс видео распаковок</a>"),
        sep="\n"
    )
    return text


async def lets_spam_starts(clients):
    text = spammer_text()
    success_count = 0
    fail_count = 0
    total = 1
    async with AsyncSession(async_engine_bot) as session:
        async with session.begin():
            for client in clients:
                print(f'{total} send to {client}')
                try:
                    result = await bot.send_message(client, text, parse_mode=ParseMode.HTML)
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
    return {'success': success_count, 'fails': fail_count, 'total': total}


async def main_spammer():
    print('НЕТ Надо новое задание придумывать.')
#     string = OMG
#     string = string.replace('"', '').replace("'","").split('\n')
#
#     bk_clients = []
#     for item in string:
#         try:
#             truitem = int(item)
#             bk_clients.append(truitem)
#         except:
#             continue
#
#     clients = await get_users_id()
#
#     total = {*clients, *bk_clients}
#
#     report = await lets_spam_starts(total)
#     print('report', report)
