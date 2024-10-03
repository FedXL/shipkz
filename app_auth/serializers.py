from rest_framework import serializers

class UnregRegistrationSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=500, required=False, allow_blank=True, allow_null=True)
    ip = serializers.CharField(max_length=255, required=False, allow_blank=True)
