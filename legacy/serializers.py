from rest_framework import serializers
from legacy.models import Orders


class OrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orders
        fields = '__all__'
        depth = 1