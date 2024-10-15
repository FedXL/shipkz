import datetime
import json
from rest_framework import serializers
from legacy.models import Orders, OrderStatusInfo

status_attr_dict = {
    'PAID': 'paid',
    'ARRIVED_AT_FORWARDER_WAREHOUSE': 'arrived_to_forward',
    'SENT_TO_HOST_COUNTRY': 'got_track',
    'ARRIVED_IN_HOST_COUNTRY': f'arrived_to_host_country',
    'RECEIVED_IN_HOST_COUNTRY': 'received_in_host_country',
    'SENT_TO_RUSSIA': 'send_to_ru',
    'GET_BY_CLIENT': 'success'
}


class OrdersSerializerPre(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    days_in_way = serializers.SerializerMethodField()


    class Meta:
        model = Orders
        fields = '__all__'
        depth = 1

    def get_date(self, obj):
        return obj.time.strftime("%d %b %Y, %H:%M")

    def get_items(self, obj):

        body_data = json.loads(obj.body)
        items_data = body_data.get('items', {})

        # Формируем список с данными для каждого item
        items = []
        for key, item in items_data.items():
            items.append({
                'item_position': key,
                'item_link': item.get('url'),
                'item_count': item.get('amount'),
                'item_comment': item.get('comment')
            })
        return items

    def get_days_in_way(self, obj):
        date_now = datetime.datetime.now()
        time_left = date_now-obj.time
        days_left = time_left.days
        return days_left






def parse_status(status,host_country,time) -> str:


    if host_country == "KYRGYZSTAN":
         country = "Кыргызстан"
    elif host_country == "KAZAKHSTAN":
         country = "Казахстан"
    else:
        country = 'не указано'
    text_dict={'PAID': 'Заказ выкуплен в магазине',
    'ARRIVED_AT_FORWARDER_WAREHOUSE': 'Заказ поступил на склад форвардера',
    'SENT_TO_HOST_COUNTRY': f'Заказ отправлен в {country}',
    'ARRIVED_IN_HOST_COUNTRY': f'Заказ прибыл на территорию {country}',
    'RECEIVED_IN_HOST_COUNTRY': 'Заказ получен в {country}',
    'SENT_TO_RUSSIA': 'Заказ отправлен в Россию',
    'GET_BY_CLIENT': 'Заказ получен клиентом'
    }

    result = text_dict.get(status,'Ошибочка сообщите нам пожалуйста')
    result +=" " + time.strftime("%d %b %Y")
    return result



class OrderStatusInfoSerializer(serializers.ModelSerializer):
    progress_bar = serializers.SerializerMethodField()
    status_text = serializers.SerializerMethodField()
    class Meta:
        model = OrderStatusInfo
        fields = '__all__'

    def get_progress_bar(self, obj):
        if obj.is_forward:
            host_country = "Казахстан" if obj.host_country == "KAZAKHSTAN" else "Кыргызстан"
            progress_points = [
                {"point_data":obj.paid,"point_text":'Заказ выкуплен в магазине'},
                {"point_data":obj.arrived_to_forward,"point_text":'Заказ поступил на склад форвардера'},
                {"point_data":obj.got_track,"point_text": f"Заказ отправлен в {host_country}"},
                {"point_data":obj.received_in_host_country,"point_text":f"Заказ получен в {host_country}"},
                {"point_data":obj.send_to_ru,"point_text":f"Заказ отправлен в Россию"}
            ]
        else:
            progress_points= [
                {"point_data":obj.paid,"point_text":'Заказ выкуплен в магазине'},
                {"point_data":obj.got_track,"point_text":'Заказ отправлен'},
                {"point_data":obj.arrived_to_host_country,"point_text":'Заказ прибыл в страну назначения'},
                {"point_data":obj.received_in_host_country,"point_text":'Заказ получен в стране назначения'},
                {"point_data":obj.send_to_ru,"point_text":'Заказ отправлен в Россию'}
            ]

        return progress_points

    def get_status_text(self,obj):
        status = obj.order.status
        attribute = status_attr_dict.get(status)
        point_time = getattr(obj, attribute)
        country= obj.host_country
        text = parse_status(status=status,
                            host_country=country,
                            time=point_time)

        # if obj.cdek:
        #     text += f' СДЕК {obj.cdek}'
        # elif obj.got_track:
        #     if obj.is_forward:
        #         text += " Доставка Форвардером"
        #     else:
        #         if obj.post_service:
        #             text += f' ТРЕК {obj.trek} Почтовая служба {obj.post_service}'
        return text

class OrderFullSerializer(OrdersSerializerPre):
    order_status_info = OrderStatusInfoSerializer(source='ori')
    start_time = serializers.SerializerMethodField()

    def get_start_time(self,obj):
        return obj.time.strftime("%d %b %Y")


