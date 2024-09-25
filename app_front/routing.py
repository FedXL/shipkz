from django.urls import path
from app_front import consumers

websocket_urlpatterns = [
    path('ws/messenger/', consumers.MessangerConsumer.as_asgi()),
]
