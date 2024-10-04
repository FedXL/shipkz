import platform
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine

TOKEN_ASKAR_BOT_HANDLER = '5810775244:AAFAa_MHBQjYydxa-EKK_WkfOonlfZ-NY0Q'
TOKEN_ASKAR = '5928544625:AAFvaSoDkBoS-C_x5TgaHxiBRd5QrGS_Qc8'
TOKEN_FED_TEST = '5736118437:AAECz8GV1yR_iQ3e2JqGzKgYc6sE6ROykKo'
TOKEN_BOT_HANDLER = "6021912534:AAEB5Pb7o38eAUmiOgVJSFApJu03BIjFzos"
NAME = "@Ship_KZ"

REDIS_QUEUE_SET = 'my_queue_set'
REDIS_QUEUE_LIST = 'my_queue_list'
current_os = platform.system()

if current_os == 'Windows':
    TEST_MODE = True
elif current_os == 'Linux':
    TEST_MODE = False
else:
    TEST_MODE = False

ADMIN = 716336613
ADMINS = [5549912130, 716336613, 1192158442]

# ГРУППА В КОТОРУЮ ПИШЕТ БОТ ИЛИ ЧЕЛОВЕК.
ShipKZ_ORDERS = -1001808930707
ShipKZ_CATCH_KAZAKHSTAN = -1001877924443
ShipKZ_CATCH_TRADINN = -1001665027798
ShipKZ_alerts = -1001949406384
ShipKZ_main_channel = -1001607267548

test_orders = -1001935862887
test_group = -1001560268568
test_chanel = -1001719436442
test_group_tradinn = -801351162
text_channel_support = -1001936578982

MANAGER = {
    716336613: "Fed",
    5549912130: "Askar",
    1192158442: "Askar",
    1087968824: "Fed",
    5906993162: "Anon",
    810809351: "Alex",
    55036742: "Andrey",
    350946841: "Igor",
    6215812561: "Marat"
}

MANAGER_TRADEINN = {
    810809351: "Alex",
    55036742: "Andrey",
    350946841: "Igor",
    6215812561: "Marat"
}

psws = {
    810809351: "aoiwjdoaawda13123wdawd",
    55036742: "aoiwdi323r3jgr43053mksd",
    350946841: "jg94j94j203k0kacm-4343",
    6215812561: "pl,epfo22r2krok24ro35"}

db_user = "postgres"
db_host = "localhost"
db_port = "5432"
db_password = "root"
db_name = "anal"


db_server_user = "postgres"
db_server_host = "localhost"
db_sever_port = "5432"
db_server_password = "12345"
db_server_name = "test_db"

love_is = -1001914850118

if TEST_MODE:
    orders_chat_storage = test_orders
    kazakhstan_chat = test_group
    tradeinn_chat = test_group_tradinn
    API_TOKEN = TOKEN_FED_TEST
    user = db_user
    host = db_host
    port = db_port
    password = db_password
    database = db_name
    alerts = test_orders
    flask_host = '0.0.0.0'
    flask_port = '5000'
    supported_channel = text_channel_support
    supported_bot = TOKEN_BOT_HANDLER
    REDIS_URL = "redis://localhost"
    REDIS_PUBSUB_ROOM = 'news'
    SUPER_WEB_USER = 9999999999
    CHROME_DRIVER_PATH = ".\\chromedriver\chromedriver-win32\chromedriver.exe"
    STATIC_FILES_PATH = ""
else:
    STATIC_FILES_PATH = '/my_static'
    orders_chat_storage = ShipKZ_ORDERS
    kazakhstan_chat = ShipKZ_CATCH_KAZAKHSTAN
    tradeinn_chat = ShipKZ_CATCH_TRADINN
    API_TOKEN = TOKEN_ASKAR
    user = db_server_user
    host = db_server_host
    port = db_sever_port
    password = db_server_password
    database = db_server_name
    alerts = ShipKZ_alerts
    flask_host = '127.0.0.1'
    flask_port = '6969'
    supported_channel = ShipKZ_main_channel
    supported_bot = TOKEN_ASKAR_BOT_HANDLER
    REDIS_URL = "redis://localhost"
    REDIS_PUBSUB_ROOM = 'news'
    SUPER_WEB_USER = 9999999999
    CHROME_DRIVER_PATH = "/root/chromedriver/chromedriver-linux64/chromedriver"

SUPPORT_IMAGE_EXTENSION = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.svg', '.webp']
SUPPORT_DOCUMENTS_EXTENSION = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.rtf', '.txt', '.odt',
                               '.ods', '.odp', '.log']

engine_app = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}', echo=False)
engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}', echo=False)
async_engine_bot = create_async_engine(f'postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}', echo=False)
print(f'postgresql://{user}:{password}@{host}:{port}/{database}')
WEB_USER_META_FIELDS = meta_data = ['ID',
                                    'username',
                                    'user_email',
                                    'user_registered',
                                    'first_name',
                                    'last_name',
                                    'description',
                                    'phone_number',
                                    'cdek_adress',
                                    'full_name',
                                    'telegram']

PATH_TO_CHROMEDRIVER = '/root/chromedriver/chromedriver'
BUYER_STATUSES = ['SENT_TO_HOST_COUNTRY', 'ARRIVED_IN_HOST_COUNTRY', 'RECEIVED_IN_HOST_COUNTRY']