import logging
my_logger = logging.getLogger('my_logger')

from django.db import transaction
from legacy.models import Orders, WebUsers






@transaction.atomic
def create_unregistered_order_way(data):
    username = data.get('username')
    web_user = WebUsers.objects.filter(web_username=username)
    order = Orders.objects.create(**data)

# order = Orders(type='WEB_ORDER', body=order_data)
#
#
#     if user.get('user_id') == 0:
#         my_logger.debug("start unregistered user branch")
#         order.user_ip = order_data['user_ip']
#         web_user = order_data['username']
#         if web_user:
#             order.save()
#             web_user_instance = WebUsers.objects.create(username=web_user)
#             return order.id, web_user_instance.username, web_user_instance.id
#         else:
#             my_logger.error("cant to find webusername in incoming data")
#             raise AssertionError
#     else:
#         my_logger.info("start registered user branch")
#         web_user = user.get('username')
#         order.save()
#         web_user_instance = WebUsers.objects.get(username=web_user)
#         return order.id, web_user_instance.username, web_user_instance.id
#
