import asyncio
from typing import List, Dict
from pydantic import BaseModel
from logs.logs import my_logger


class Item(BaseModel):
    url: str
    amount: int
    comment: str


class OrderReg(BaseModel):
    """order for registered web users"""
    country: str
    items: Dict[int, Item]
    username: str | None = None
    phone_number: str | None = None
    cdek_adress: str | None = None


class OrderNotReg(BaseModel):
    country: str
    url: str
    price: str
    comment: str
    email: str
    phone: str
    username: str
    user_ip: str


async def parce_web_order(data) -> OrderReg | OrderNotReg | bool:
    my_logger.info(f'incoming data to parce: {data}')
    country_key = 'radio-1'
    url_key = 'url-1'
    number_key = 'number-1'
    comment_key = 'text-1'
    is_unregister_user = data.get('unregister_user')
    country_type = data.get(country_key)
    unregistered_username_key = 'text-3'
    try:
        if not is_unregister_user:
            products = {}
            counter = 1
            while True:
                if data.get(url_key) is not None:
                    product = Item(url=data.get(url_key),
                                   amount=data.get(number_key),
                                   comment=data.get(comment_key))
                    products[counter] = product.model_dump()
                else:
                    break
                if counter != 1:
                    counter += 1
                    url_key = url_key[:-2] + "-" + str(counter)
                    number_key = number_key[:-2] + "-" + str(counter)
                    comment_key = comment_key[:-2] + "-" + str(counter)
                else:
                    counter += 1
                    url_key += "-" + str(counter)
                    number_key += "-" + str(counter)
                    comment_key += "-" + str(counter)
            registered_order = OrderReg(country=country_type,
                                        items=products,
                                        username=data.get('hidden-1'),
                                        phone_number=data.get('phone_number'),
                                        cdek_adress=data.get('cdek_adress')
                                        )
            my_logger.info(f"[success parsing model]: {registered_order.model_dump()}")
            return registered_order
        else:
            price_key = 'text-2'
            comment_key = 'textarea-1'
            email_key = 'email-1'
            phone_key = 'phone-1'
            ip_key = 'user_ip'
            unregistered_order = OrderNotReg(
                country=country_type,
                url=data.get(url_key),
                amount=data.get(number_key),
                price=data.get(price_key),
                comment=data.get(comment_key),
                email=data.get(email_key),
                phone=data.get(phone_key),
                username=data.get(unregistered_username_key),
                user_ip=data.get(ip_key),
            )
            return unregistered_order
    except Exception as Er:
        my_logger.error(f'cant to parce data {Er}')
        return False


async def registerparcer():
    data = {'radio-1': 'europe',
            'url-1': 'http://yandex.ru',
            'number-1': '1',
            'text-1': 'sss',
            'group-1-copies': {'1het2n3su00d5efcaf79825': 2},
            'hidden-1': 'admin',
            'hidden-2': '',
            'hidden-3': '',
            'referer_url': '',
            'forminator_nonce': 'a82632ee72',
            '_wp_http_referer': '//',
            'form_id': '1114',
            'page_id': '1115',
            'form_type': 'default',
            'current_url': 'https://shipkz.ru/-/',
            'render_id': '0', 'action': 'forminator_submit_form_custom-forms',
            'url-1-2': 'http://google.com', 'number-1-2': '1',
            'text-1-2': 'www',
            'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImFkbWluIiwiY3VycmVudF90aW1lIjoxNjk5NjM1NTA5LCJleHAiOjE2OTk2MzU1MTl9.FJrJPTwHB0o42RqcJN_F65eUPol7Ncxl4EWsox28zl8',
            'event': 'create_order',
            'cdek_adress': 'Алматы , Акжар 60',
            'unregister_user': False,
            'user_name': '',
            'phone_number': '87058210643'}
    result = await parce_web_order(data)
    print(result)


async def unregisterparcer():
    data = {'radio-1': 'europe',
            'url-1': 'http://yandex.ru',
            'text-2': '5000 евро',
            'number-1': '1',
            'textarea-1': 'test',
            'email-1': 'fedorkuruts@gmail.com',
            'phone-1': '87058210643',
            'text-3': 'UNREG_CZpOAJY8Or1VHiNEN2Vs',
            'referer_url': '',
            'forminator_nonce': 'cebc15809d',
            '_wp_http_referer': '/kz/',
            'form_id': '1104',
            'page_id': '121',
            'form_type': 'default',
            'current_url': 'https://shipkz.ru/',
            'render_id': '0',
            'action': 'forminator_submit_form_custom-forms',
            'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjowLCJ1c2VybmFtZSI6ZmFsc2UsImN1cnJlbnRfdGltZSI6MTcwMTcwMDg2NCwiZXhwIjoxNzAxNzAwODg0fQ.KhbJ6BZz1XQqZ5tCysqtswM6251BlYweUFAfzr36xQM',
            'event': 'create_order',
            'unregister_user': True,
            'user_ip': '176.64.21.224'}
    result = await parce_web_order(data)
    print(result)
