import json
from channels.generic.websocket import AsyncWebsocketConsumer

class MessangerConsumer(AsyncWebsocketConsumer):
    """консъюмер для обработки вебсокетов"""
    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({
            'message': 'Connected successfully!'
        }))

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        # Логика обработки входящих сообщений
        await self.send(text_data=json.dumps({
            'message': 'You sent' + text_data}))

