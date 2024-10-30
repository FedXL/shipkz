from app_front.management.email.email_sender import my_logger
from legacy.models import WebUsers, Orders
from legacy.serializers import OrdersSerializerPre, OrderFullSerializer


def get_orders_by_username_pre(username, pre=False):
    my_logger.info(f'!username!: {username}')
    orders = Orders.objects.filter(web_user__web_username=username).order_by('-id')
    orders_list = [order for order in orders if not hasattr(order, 'ori')]
    serializer = OrdersSerializerPre(orders_list, many=True)
    return serializer.data

def get_orders_by_username_full(username):
    orders = Orders.objects.filter(web_user__web_username=username).order_by('-id')
    orders_list = [order for order in orders if hasattr(order, 'ori')]
    serializer = OrderFullSerializer(orders_list, many=True)
    return serializer.data


def body_parser(form_set_data):

    """
    ак как у нас старый body это json и кривой надо сделать из нормальноф формы именно ег
    income data 
      {'country': {'country': 'EUROPE'}, 'items': [{'goods_link': '2.ru', 'count': 2, 'comment': '33'}]}
    output data
    "items":{ 
    "1": {"url": "https://thomasfarthing.co.uk... ", "amount": 1, "comment": "Цвет - GREY, размер - 40/31\""},
    "2": {"url": "https://thomasfarthing.co.uk/pr...", "amount": 1, "comment": "Цвет - BROWN, размер - 58cm"}
    }
    """

    refactored_items = {}
    numer =1
    for item in form_set_data:
        url = item.get('goods_link')
        count = item.get('count')
        comment = item.get('comment')
        refactored_items[numer] = {'url': url, 'amount': count, 'comment': comment}
        numer += 1
    return refactored_items
