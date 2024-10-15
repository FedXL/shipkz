from legacy.models import WebUsers, Orders
from legacy.serializers import OrdersSerializerPre, OrderFullSerializer


def get_orders_by_username_pre(username, pre=False):
    web_user = WebUsers.objects.filter(web_username=username).first()
    orders = Orders.objects.filter(web_user=web_user).order_by('-id')
    orders_list = [order for order in orders if not hasattr(order, 'ori')]
    serializer = OrdersSerializerPre(orders_list, many=True)
    return serializer.data

def get_orders_by_username_full(username):
    orders = Orders.objects.filter(web_user__web_username=username).order_by('-id')
    orders_list = [order for order in orders if hasattr(order, 'ori')]
    serializer = OrderFullSerializer(orders_list, many=True)
    return serializer.data


