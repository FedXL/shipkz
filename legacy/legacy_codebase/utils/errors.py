import asyncio
from create_bot import bot


class TelegramHandlerError(Exception):
    """Класс пользовательской ошибки"""

    def __init__(self, chat_id, message="Произошла пользовательская ошибка"):
        self.message = message
        self.chat_id = chat_id
        super().__init__(self.message)
        self.send_message_to_telegram()

    async def send_message_to_telegram(self):
        """Отправка сообщения через телеграм-бота"""
        await bot.send_message(chat_id=self.chat_id, text=self.message)


async def send_message_from_bot(chat_id, message):
    await bot.send_message(chat_id=chat_id, text=message)


def send_message_from_bot_synch(chat_id, message):
    print('start')
    asyncio.run(send_message_from_bot(chat_id, message))
