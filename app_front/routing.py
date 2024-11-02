from django.urls import path
from app_front import consumers

websocket_urlpatterns = [
    path('ws/support/', consumers.SupportConsumer.as_asgi()),  # URL для подключения к WebSocket

]