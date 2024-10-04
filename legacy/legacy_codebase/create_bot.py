from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from aiogram.dispatcher import Dispatcher
from utils.config import API_TOKEN, supported_bot
from sqlalchemy import create_engine
from utils.config import user, host, port, database, password

engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}', echo=False)
storage = MemoryStorage()
bot = Bot(API_TOKEN)
dp = Dispatcher(bot=bot, storage=storage)
dp.debug = False
bot_for_support = Bot(supported_bot)
