import datetime
import json
from aiohttp import web
from base.good_db_handlers import get_order_info_by_id, get_sberbank_exchange, get_all_unread_message_count_by_web_user, \
    collect_user_data_by_order_id, collect_user_data_by_user_id
from handlers.chat.sender import send_notification_text_to_tele_user
from module_7.base.db_handlers import create_order_web, get_orders_by_username, replace_user, \
    create_user_from_wp_with_meta, update_user_wp_meta
from logs.logs import my_logger
from module_7.bot.bot_handlers import send_order_alert_bot, send_meeting_message_to_bot
from module_7.handlers.change_status.status_handler import change_order_status_handler, \
    collect_country_report_from_orders
from module_7.handlers.crud_handlers.crud_handlers import delete_order_
from module_7.handlers.notifications.notificate_handler import open_chats_by_orders, \
    send_messages_by_orders, send_one_notification_by_order, send_to_buyer_instructions
from module_7.utils.create_web_order_parcer import parce_web_order
from module_7.utils.token import check_token
from sheets.add_orders import add_last_string
from utils.config import BUYER_STATUSES


async def exchange_hook(request):
    if request.method == 'GET':
        values = await get_sberbank_exchange()
        print('VALUE!')
        json_orders = json.dumps(values)
        return web.json_response(data=json_orders)


async def handle_webhook(request):
    place = ""
    if request.method == 'GET':
        my_logger.debug('handle webhook Method GET')
        return web.Response(text='Success', status=200)
    elif request.method == 'POST':
        my_logger.debug('Method POST')
        try:
            place = 'authorization start'
            # authorization ------------------------------------------ start
            data = await request.read()
            opendata = data.decode('utf-8')
            data_dict = json.loads(opendata)
            print("[CRITICAL INCOMING INFO]", data_dict)
            decrypted_token = check_token(data_dict.get('token'))
            if not decrypted_token:
                my_logger.info(request)
                return web.Response(text='Invalid token', status=404)
            # authorization ------------------------------------------- end
            event = data_dict.get('event')
            if not event:
                my_logger.warning("no event ")
                return web.Response(text='Invalid data', status=404)
            my_logger.info(f"start event : {event}")
            place = event
            match event:
                case "create_order":
                    web_order = await parce_web_order(data_dict)
                    if web_order:
                        web_order_id, web_user, web_user_id = await create_order_web(web_order_data=web_order,
                                                                                     user=decrypted_token)
                        my_logger.debug(f'create order web result: {web_order_id}')
                        await send_meeting_message_to_bot(user_id=web_user_id, user_name=web_user)
                        await send_order_alert_bot(user=decrypted_token.get('username'),
                                                   web_user_id=web_user_id,
                                                   order=web_order_id,
                                                   order_details=web_order
                                                   )
                        return web.Response(text='Success', status=200)
                    else:
                        return web.Response(text='Cant to create web order', status=404)
                case 'change_order_user':
                    """кейс для переназначения пользователя"""
                    result, comment = await replace_user(decrypted_token)
                    print('[INFO change USER]', result, comment)
                    if result:
                        stat = 200
                        result = {'result': 'success'}
                    else:
                        result = {'result': 'Error', 'details': comment}
                        stat = 403
                    content = json.dumps(result)
                    return web.json_response(data=content, status=stat)
                case "create_user":
                    """кейс для создания пользователя"""
                    username = data_dict.get('username')
                    my_logger.info(f'create user with username = {username}')
                    user_id, root_id = await create_user_from_wp_with_meta(data_dict)
                    return web.Response(text="success")
                case "get_user_info_by_order_id":
                    """кейс для получения данных о пользователя по ордер айди"""
                    order_id = decrypted_token.get('order_id')
                    order_id = int(order_id)
                    user_info = await collect_user_data_by_order_id(order_id=order_id)
                    content = json.dumps(user_info)
                    return web.json_response(data=content, status=200)
                case "get_user_info_by_user_id":
                    user_id = decrypted_token.get('user_id')
                    user_info = await collect_user_data_by_user_id(user_id=user_id)
                    content = json.dumps(user_info)
                    return web.json_response(data=content, status=200)
                case "update_user":
                    """кейс для обновления пользователя"""
                    print('кейс для обновления пользователя')
                    result = await update_user_wp_meta(data_dict)
                    my_logger.debug(f'update user result = {result}')
                    return web.Response(text="success")
                case "load_orders":
                    orders_result = await get_orders_by_username(decrypted_token.get('username'),
                                                                 variant=data_dict.get('is_paid'))
                    json_orders = json.dumps(orders_result)
                    print('order_result', orders_result)
                    return web.json_response(data=json_orders, status=200)
                case "check_country_orders":
                    """Отвечает на вопрос в какую страну едет заказ"""
                    my_logger.debug("[Check_order_status]")
                    orders = decrypted_token.get('orders')
                    print(orders)
                    country_report = await collect_country_report_from_orders(orders)
                    print('RESPONSE', country_report)
                    response = json.dumps(country_report)
                    return web.json_response(data=response, status=200)
                case "delete_order":
                    result, comment = await delete_order_(decripted_token=decrypted_token,
                                                          order_id=data_dict.get("order_id"),
                                                          from_who=data_dict.get('from_who'))
                    if result:
                        return web.Response(text="Success", status=200)
                    else:
                        return web.Response(text="BAD REQUEST", status=200)
                case "ReadMessagesInfo":
                    """case for getting info about unread messages for users buttons or"""
                    my_logger.debug("[ReadMessagesInfo]")
                    user_id = decrypted_token.get('user_id')
                    count = await get_all_unread_message_count_by_web_user(user_id)
                    data = {"unreadCount": count}
                    return web.json_response(data=data, status=200)
                case "load_order":
                    result, comment = await get_order_info_by_id(decrypted_token.get('order_id'))
                    if result:
                        stat = 200
                    else:
                        result = {'result': 'Error', 'details': comment}
                        stat = 403
                    content = json.dumps(result)
                    return web.json_response(data=content, status=stat)
                case "change_status":
                    status: str = decrypted_token.get('status')
                    orders = decrypted_token.get('orders_id')
                    buyer_info = None
                    report = {}
                    report_for_buyer = set()
                    for order in orders:
                        print('----------------------------------------> CHANGE STATUS')
                        result, comment = await change_order_status_handler(status=status,
                                                                            order_id=order,
                                                                            data=data_dict)
                        print('-------------------------------------> RESULT', result, comment)
                        if result:
                            report[order] = {'change_status': {'result': 'success', 'details': comment}}
                        else:
                            report[order] = {'change_status': {'result': 'error', 'details': comment}}
                            continue
                        print('-------------------------------------> SEND NOTIFICATION', order)
                        result2, comment2 = await send_one_notification_by_order(order, status)
                        print('-------------------------------------> RESULT', result2, comment2)
                        if result2:
                            buyer_info = result2.get('buyer_info')
                            report_for_buyer.add(buyer_info)
                            report[order]['send_message'] = {'result': 'success', 'details': result2}
                        else:
                            report[order]['send_message'] = {'result': 'error', 'details': comment2}
                            continue
                    if status in BUYER_STATUSES:
                        print('-------------------------------------> SEND TO BUYER')

                        if len(report_for_buyer) == 1:
                            message = await send_to_buyer_instructions(report_for_buyer, orders)
                            report['send_to_buyer'] = message
                        else:
                            print('buyer mistake we have 2 different buyers reports')
                            report['send_to_buyer'] = {'result': 'error', 'details': 'Разные баеры в одном заказе ('
                                                                                    'строке). Такого быть не должно'}
                    print(report)
                    await add_last_string(values=[(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                   'from sheets',
                                                   'notifications',
                                                   str(report))],
                                          sheet='messages_storage')
                    return web.json_response(data=report, status=200)
                case "change_order_status":
                    """эта штука один статус меняет для одного ордера."""
                    status: str = decrypted_token.get('status')
                    order_id = decrypted_token.get('order_id')
                    result, comment = await change_order_status_handler(status=status,
                                                                        order_id=order_id,
                                                                        data=data_dict)
                    if result:
                        data = {'result': 'success', 'details': comment}
                        stat = 200
                    else:
                        stat = 403
                        data = {'result': 'Error', 'details': comment}
                    data = json.dumps(data)
                    my_logger.info(f"End event change_order_data result: {data}")
                    return web.json_response(data, status=stat)
                case "send_status_notification_by_order":
                    """отправить одну оповестительное сообщение по заказу."""
                    my_logger.debug('[SEND NOTIFICATIONS]')
                    order = decrypted_token.get('order')
                    status_order = decrypted_token.get('status')
                    report, comment = await send_one_notification_by_order(order, status_order)
                    if report:
                        data = {'result': 'success', 'details': 'success'}
                        stat = 200
                        await add_last_string(values=[(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                       "[google sheets]",
                                                       f'to order{order}',
                                                       str(report))],
                                              sheet='messages_storage')
                    else:
                        data = {'result': 'error', 'details': comment}
                        stat = 400
                        await add_last_string(values=[(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                       "[google sheets]",
                                                       f'to order{order}', comment)],
                                              sheet='messages_storage')
                    data_r = json.dumps(data)
                    return web.json_response(data=data_r, status=stat)
                case "send_messages_to_orders_owner":
                    """отправить сообщения тектовое владельцам ордеров."""
                    orders = decrypted_token.get('orders')
                    text = data_dict.get('text')
                    full_data, comment = await send_messages_by_orders(orders=orders, text=text)
                    report = full_data.get('report')
                    if report:
                        data = report
                        data['result'] = 'success'
                        status = 200
                    else:
                        status = 400
                        data = {'result': 'error', 'details': comment}
                    data = json.dumps(data)
                    return web.json_response(data=data, status=status)
                case "open_chats":
                    orders = decrypted_token.get('orders')
                    await open_chats_by_orders(orders)
                    data = json.dumps({'result': 'success'})
                    return web.json_response(data=data, status=200)
                case default:
                    my_logger.debug("Unknown case")
                    data = {"message": "event"}
                    return web.json_response(data=data, status=400)
        except Exception as e:
            my_logger.error(f"In {place}. Error args: {e.args}")
            return web.Response(status=500)
    else:
        return web.Response(text='Method Not Allowed', status=405)


async def static_handler(request):
    if request.method == 'POST':
        data = await request.read()
        opendata = data.decode('utf-8')
        data_dict = json.loads(opendata)
        place = data_dict.get('place')
        pass
