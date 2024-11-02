from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from app_front.management.unregister_authorization.token import check_token


class SupportConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            token = self.scope.get('token')
            if not token:
                await self.close()
                return
            decoded_token = check_token(token=token,
                                        secret=settings.SHARABLE_SECRET,
                                        is_comment=False)
            if not decoded_token:
                await self.close()
                return

            web_user_id = decoded_token.get('user_id')
            channel_group_name = f"web_support_{web_user_id}"
        else:
            web_user_id = user.profile.web_user.user_id
            channel_group_name = f"web_support_{web_user_id}"

        await self.channel_layer.group_add(
            channel_group_name,
            self.channel_name,
        )
        await self.accept()
        await self.send(text_data='{"message": "Вы подключены к поддержке!"}')  # Форматируйте по необходимости

    async def disconnect(self, close_code):
        if hasattr(self, 'channel_group_name'):
            await self.channel_layer.group_discard(self.channel_group_name, self.channel_name)

