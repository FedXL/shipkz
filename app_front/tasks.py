from typing import Tuple
from celery import shared_task
from app_bot.management.bot_core import sync_bot
from app_bot.management.bot_text_utils import create_web_message_text
from app_front.management.email.email_sender import send_email
from legacy.models import WebUsersMeta, Orders, WebUsers


def create_unregister_web_order(data,web_user_id,user_ip) ->Tuple[Orders,WebUsers]:
    """data = form data from unregistered order form fields {url, price, count, comment, email, phone}"""

    url = data.get('url')
    price = data.get('price')
    count = data.get('count')
    comment = data.get('comment')
    email = data.get('email')
    phone = data.get('phone')



    web_user = WebUsers.objects.get(user_id=web_user_id)
    user_email, created_email = WebUsersMeta.objects.update_or_create(
        web_user=web_user,
        field='email',
        defaults={'value': email}
    )

    user_phone, created_phone = WebUsersMeta.objects.update_or_create(
        web_user=web_user,
        field='phone',
        defaults={'value': phone}
    )

    order = Orders.objects.create(
        type='WEB_ORDER',
        body=data,
        user_ip=user_ip,
        web_user=web_user
    )
    return order, web_user

@shared_task
def unregister_web_task_way(data:dict,
                            web_user_id:str,
                            user_ip:str):
    email = data.get('email')
    order, web_user = create_unregister_web_order(data,web_user_id,user_ip)
    # send_order_notification_email(to_mail=email, form_data=data, order_number=order.id)
    sync_bot.send_message(chat_id=716336613, text='Ваш заказ принят в обработку, ожидайте звонка менеджера')
    text=create_web_message_text(web_user)



@shared_task
def send_email_task(header, body, to_mail):
    send_email(header, body, to_mail)

