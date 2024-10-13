from legacy.models import WebUsers, Orders
from legacy.serializers import OrdersSerializer


def get_orders_by_username(username):
    web_user = WebUsers.objects.filter(web_username=username).first()
    orders = Orders.objects.filter(web_user=web_user).order_by('-id')
    orders_list = []
    for order in orders:
        if hasattr(order, 'ori'):
            orders_list.append(order)
    serializer = OrdersSerializer(orders_list, many=True)
    serialized_data = serializer.data
    return serialized_data
