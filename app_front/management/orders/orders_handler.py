from legacy.models import WebUsers, Orders
from legacy.serializers import OrdersSerializer


def get_orders_by_username(username, pre=False):
    web_user = WebUsers.objects.filter(web_username=username).first()
    orders = Orders.objects.filter(web_user=web_user).order_by('-id')

    if pre:
        orders_list = [order for order in orders if not hasattr(order, 'ori')]
    else:
        orders_list = [order for order in orders if hasattr(order, 'ori')]

    serializer = OrdersSerializer(orders_list, many=True)
    return serializer.data

