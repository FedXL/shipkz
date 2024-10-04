import json

import redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)
redis_client.pubsub()


def send_redis_mess_to_web(message):
    channel = 'news'
    data = str(message)
    redis_client.publish(channel, data)


def send_message_to_support(message:json):
    """Не помню зачем, но оно надо для управления меню"""
    channel = 'menu'
    message = json.dumps(message)
    redis_client.publish(channel, message)

