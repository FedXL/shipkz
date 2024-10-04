import aiohttp.web
import aiohttp.web_ws
import aiohttp_jinja2
import jinja2
from aiohttp import web
from module_7.config.config_app import STATIC_PATH, STATIC_MAIN, START_HOST, SOCKET_ENDPOINT, START_PORT, ALLOWED_IP
from module_7.handlers.access_handler import access_token_handler
from module_7.handlers.api_handler import handle_webhook, exchange_hook
from module_7.handlers.socket_handler import websocket_handler
from logs.logs import my_logger
from module_7.handlers.socket_menu_handler import menu_websocket
from module_7.utils.utils3 import check_redis_connection, check_sistem


async def index(request):
    context = {'title': 'Пишем первое приложение на aiohttp',
               'socket_endpoint': SOCKET_ENDPOINT}
    return aiohttp_jinja2.render_template('index.html', request, context=context)


async def ip_filter_middleware(app, handler):
    allowed_ip = [ALLOWED_IP]

    async def middleware(request):
        client_ip = request.remote
        if client_ip not in allowed_ip:
            return web.Response(text="Access Denied", status=403)
        response = await handler(request)
        return response

    return middleware


app = aiohttp.web.Application()
app['debug'] = True
loader = jinja2.FileSystemLoader('templates')
aiohttp_jinja2.setup(app, loader=loader)
app.router.add_get('/ws/', websocket_handler)
app.router.add_get('/ws2/', menu_websocket)
app.router.add_get('/', index)
app.add_routes([web.static('/static', path=STATIC_PATH)])
app.add_routes([web.static('/static_main', path=STATIC_MAIN)])
app.router.add_post('/api/webhook/', handle_webhook)
app.router.add_get('/api/webhook/', handle_webhook)
app.router.add_get('/api/free-zone/exchange/', exchange_hook)
app.router.add_post('/api/access/', access_token_handler)

for resource in app.router.resources():
    if isinstance(resource, web.StaticResource):
        print("Static files path:", resource.get_info())
        break


def main():
    my_logger.info('Старт приложения в режиме TEST MODE')
    check_redis_connection()
    check_sistem()
    aiohttp.web.run_app(app, host=START_HOST, port=START_PORT)
