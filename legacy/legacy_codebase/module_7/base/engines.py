from sqlalchemy.ext.asyncio import create_async_engine
from module_7.config.config_app import DB_URL, DB_TEST
from utils.config import async_engine_bot

async_engine = async_engine_bot

async_test_engine = create_async_engine(DB_TEST, echo=False)




