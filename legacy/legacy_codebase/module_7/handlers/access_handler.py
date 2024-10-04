import json
import string
import random
from aiohttp import web
from pydantic import BaseModel
from base.good_db_handlers import get_web_user_id_by_name
from create_bot import bot
from logs.logs import my_logger
from module_7.base.db_handlers import create_user_from_wp
from module_7.config.config_app import sharable_secret_long
from module_7.utils.token import check_token, create_token, create_access_token
from utils.config import ADMIN


class accessIncome(BaseModel):
    token: str
    event: str
    long_token: str = None


def generate_random_name(length=20):
    random_name = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    return random_name


async def create_long_token_handler(decrypted_token: dict):
    ip = decrypted_token.get('username')
    new_username = 'UNREG_' + generate_random_name()
    long_token = create_token(username=new_username, ip=ip, secret=sharable_secret_long)
    await create_user_from_wp(new_username)
    return long_token


async def access_token_handler(request):
    place = None
    try:
        place = 'authorization'
        data = await request.read()
        opendata = data.decode('utf-8')
        data_dict = json.loads(opendata)
        income = accessIncome(**data_dict)

        decrypted_token = check_token(income.token)
        if not decrypted_token:
            my_logger.info(request)
            return web.json_response(data={'result': 'Invalid Token'}, status=403)

        event = income.event
        place = event
        match event:
            case "get_long_token":
                my_logger.debug('[GET LONG TOKEN BRANCH]')
                long_token = await create_long_token_handler(decrypted_token=decrypted_token)
                data_return = {'long_token': long_token, 'result': 'success'}
                return web.json_response(data_return, status=200)
            case "get_access_token":
                my_logger.debug('[GET ACCESS TOKEN BRANCH]')
                if not income.long_token:
                    my_logger.debug('Invalid Request. long token is null')
                    return web.json_response(status=403, data={'result': 'invalid_request'})
                decrypted_long_token, comment = check_token(token=income.long_token,
                                                            secret=sharable_secret_long,
                                                            is_comment=True)
                if not decrypted_long_token:
                    my_logger.error(f'invalid long token')
                    return web.json_response(status=403, data={'result': 'invalid_long_token'})
                unregistered_username = decrypted_long_token.get('username')
                user_id = await get_web_user_id_by_name(unregistered_username)
                if user_id:
                    access_token = create_access_token(username=unregistered_username)
                    data_return = {'access_token': access_token,
                                   'result': 'success',
                                   'user_name': unregistered_username}
                    my_logger.debug(f'Access allowed user: {unregistered_username}')
                    return web.json_response(data_return, status=200)
                else:
                    my_logger.warning(
                        f'Cant to find user_id While token is valid looks like secret key was stolen. Plz '
                        f'change secret keys')
                    await bot.send_message(ADMIN,
                                           f"[WARNING] got long key {income.long_token} with {decrypted_token} . "
                                           f"Token is valid but user was not created. Change secret key or check "
                                           f"database")
                    return web.json_response(data={'result': 'Invalid Long Token'})
    except Exception as ER:
        my_logger.error(f"Unexpected Error in {place} Details: {ER}")
        return web.json_response(status=500, data={'result': 'Server Error'})
