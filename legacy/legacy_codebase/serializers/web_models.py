from ipaddress import IPv4Address, IPv6Address
from pydantic import BaseModel

"""
examples:
user(unregistered) -> {'user_id': 0,
        'username': False,
        'current_time': 1697099084,
        'exp': 1697099094}

<-order (unregistered)->
    {'country': 'Japan',
    'url': 'http://yandex.ru',
    'amount': '1',
    'price': '5000 евро',
    'comment': '1213123123123123123',
    'email': 'mabuteec@gmail.com',
    'phone': '8 888 888 88 88',
    'user_name': None,
    'user_ip': '2a0d:b201:1016:75c3:6c2b:d3da:a24:a941'}

"""


class GetWebUser(BaseModel):
    user_id: int
    username: str | bool


class GetWebOrder(BaseModel):
    country: str
    url: str
    price: str
    comment: str = None
    email: str
    phone: str
    user_name: str | None = None
    user_ip: IPv4Address | IPv6Address
