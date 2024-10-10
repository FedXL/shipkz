import logging
import os
from dotenv import load_dotenv
from telebot import types
import telebot
from app_bot.management.bot_text_utils import create_web_message_text
from legacy.models import WebUsers


load_dotenv()
bot_token = os.getenv("BOT_TOKEN")
bot_logger = logging.getLogger('bot_logger')
bot_logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
bot_logger.addHandler(console_handler)


def get_keyboard_message_start():
    buttons = [
        types.InlineKeyboardButton(text="🗃", callback_data="message_menu"),
        types.InlineKeyboardButton(text="↕️️", callback_data="fast_answers_choice")]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


class TelegramBot:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token)

    def send_message(self, chat_id, text, reply_markup=None):
        try:
            message = self.bot.send_message(chat_id, text, reply_markup=reply_markup, parse_mode='HTML')
            return message
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")
            return None

    def delete_message(self, chat_id, message_id):
        try:
            message=self.bot.delete_message(chat_id, message_id)
            return message
        except Exception as e:
            print(f"Ошибка при удалении сообщения: {e}")
            return None

    def update_message(self, chat_id, message_id, text):
        try:
            message=self.bot.edit_message_text(chat_id, message_id, text)
            return message
        except Exception as e:
            print(f"Ошибка при обновлении сообщения: {e}")
            return None


sync_bot = TelegramBot(bot_token)


def web_open_meeting_message_in_bot(web_user:WebUsers):
    """WEB создает текст сообщения,
    вытаскивает, старый номер сообщения
    пытается его удалить
    отсылает новое сообщение
    РАБОТАЕТ ТОЛЬКО С SHORT STORY
    """
    text_to_send=create_web_message_text(web_user)
    chat_id = web_user.get_chat_id()
    old_message_id = web_user.last_message_telegramm_id

    if old_message_id:
        try:
            result=sync_bot.delete_message(chat_id, old_message_id)
            bot_logger.info(f'old message deleted {result}')
        except Exception as e:
            bot_logger.error(f'cant to delete message {e}')
    message =  sync_bot.send_message(chat_id=chat_id, text=text_to_send,reply_markup=get_keyboard_message_start())
    if message:
        web_user.last_message_telegramm_id=message.message_id
        web_user.save()
        bot_logger.info(f'new message sent {message}')




