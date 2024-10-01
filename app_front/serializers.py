from rest_framework import serializers


class ItemSerializer(serializers.Serializer):
    url = serializers.URLField()
    amount = serializers.IntegerField()
    comment = serializers.CharField()

class OrderRegSerializer(serializers.Serializer):
    country = serializers.CharField()
    items = serializers.DictField(child=ItemSerializer())
    username = serializers.CharField(allow_null=True, required=False)
    phone_number = serializers.CharField(allow_null=True, required=False)
    cdek_adress = serializers.CharField(allow_null=True, required=False)

class OrderNotRegSerializer(serializers.Serializer):
    country = serializers.CharField()
    url = serializers.URLField()
    price = serializers.CharField()
    comment = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField()
    username = serializers.CharField()
    user_ip = serializers.CharField()


