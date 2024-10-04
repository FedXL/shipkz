from base.good_db_handlers import delete_orders_by_webusername


async def delete_order_(decripted_token: dict, order_id, from_who):
    try:
        order_id = int(order_id)
    except:
        return False, 'Cant to convert order id to int'
    match from_who:
        case "SHIP_KZ_WORD_PRESS":
            result, comment = await delete_orders_by_webusername(username=decripted_token.get('username'),
                                                                 order_id=order_id)
            return result, comment
        case "SHIP_KZ_APP_SCRIPT":
            return True, "SUCCESS"
