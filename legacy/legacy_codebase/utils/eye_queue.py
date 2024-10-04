"""Обновление  автоматически.
    Этот модуль содержит функции для реализации функционала оповещения о просмотре пользовательем WEB чата.
Идея заключается в том что при отправлении из веб чатом сообщения isReadMessage в сокет.
Будет стартовать функция, которая запустит принудительное обновление сообщения для общения.
    А для того что бы исключить ситуацию когда пользователь одновременно прочитает 20 сообщений и прервать 19 лишних
обновлений, создана очередь по типу стек в редисе."""

import asyncio
from logs.logs import my_logger
from module_7.bot.bot_handlers import update_meeting_message_web
from module_7.utils.utils3 import connect_to_redis
from utils.config import REDIS_QUEUE_SET, REDIS_QUEUE_LIST


async def add_element(redis, web_user_id):
    set_name = REDIS_QUEUE_SET
    list_name = REDIS_QUEUE_LIST
    """
    Добавляет элемент в множество и, если элемент уникален, добавляет его в список.
    """
    is_added = await redis.sadd(set_name, web_user_id)
    if is_added:
        my_logger.debug(f'add {web_user_id}')
        await redis.rpush(list_name, web_user_id)
    else:
        my_logger.debug(f'already got element for user {web_user_id}')


async def remove_last_element_and_cleanup(redis):
    """
    Удаляет последний элемент из списка и, если список был не пуст, удаляет этот элемент из множества.
    """
    set_name = REDIS_QUEUE_SET
    list_name = REDIS_QUEUE_LIST
    element = await redis.lpop(list_name)
    if element:
        print(f'remove {element}')
        await redis.srem(set_name, element)
        element = element.decode('utf-8')
        return element
    else:
        return


async def main_loop_eye_checker():
    """foo for check redis . If in redis got eye task, trying to reload meeting message"""
    redis = await connect_to_redis()
    while True:
        print('[EYE]')
        web_user_id = await remove_last_element_and_cleanup(redis)
        if web_user_id:
            try:
                web_user_id = int(web_user_id)
                my_logger.debug(f'try to reload message for WEB USER {web_user_id}')
                await update_meeting_message_web(web_user_id)
            except Exception as er:
                my_logger.debug(f'Cant to update meeting message Error: {er}')
        await asyncio.sleep(3)



