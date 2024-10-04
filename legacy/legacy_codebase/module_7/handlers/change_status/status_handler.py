import datetime
from pydantic import BaseModel
from pydantic_core import ValidationError
from base.good_db_handlers import get_country_by_orders_id
from module_7.base.db_handlers import change_order_status_in_db, add_order_status_info_db


class Paid(BaseModel):
    shop: str
    store_order_number: str | int
    relative_price: str
    is_forward: bool
    host_country: str = None


class ArrivedWarehouse(BaseModel):
    pass


class SendToHostCountry(BaseModel):
    trek: str | int = None
    post_service: str
    buyer: int | str = None
    buyer_reward: str = None


class SendToRU(BaseModel):
    cdek: dict


async def change_order_status_handler(status: str, order_id: int, data: dict):
    print('[INFO][START] Change order status handler with:', status, order_id, data)
    try:
        order_id = int(order_id)
        match status:
            case "PAID":
                """страна меняется только один раз здесь"""
                timedata = {'paid': datetime.datetime.now()}
                paid = Paid(**data)
                data_for_db = {**paid.model_dump(), **timedata}
            case "ARRIVED_AT_FORWARDER_WAREHOUSE":
                timedata = {'arrived_to_forward': datetime.datetime.now()}
                data_for_db = timedata
            case "SENT_TO_HOST_COUNTRY":
                timedata = {'got_track': datetime.datetime.now()}
                send_to_kz = SendToHostCountry(**data)
                data_for_db = {**timedata, **send_to_kz.model_dump()}
            case "ARRIVED_IN_HOST_COUNTRY":
                timedata = {'arrived_to_host_country': datetime.datetime.now()}
                data_for_db = timedata
            case "RECEIVED_IN_HOST_COUNTRY":
                timedata = {'received_in_host_country': datetime.datetime.now()}
                data_for_db = timedata
            case "SENT_TO_RUSSIA":
                timedata = {'send_to_ru': datetime.datetime.now()}
                cdek = {'cdek': data['cdek'][str(order_id)]}
                data_for_db = {**timedata, **cdek}
            case "GET_BY_CLIENT":
                timedata = {'success': datetime.datetime.now()}
                data_for_db = timedata
            case _:
                raise ValueError(f"Invalid status: {status}")
        data_for_db['host_country'] = data.get('host_country')
        result, comment = await change_order_status_in_db(status=status, order_id=order_id) # собирает инфу проверяет есть ли ордер вообще
        if result:
            result, comment = await add_order_status_info_db(order_id=order_id, data=data_for_db) #меняет order_status_info
        return result, comment
    except ValidationError as e:
        return False, f"Invalid data. ValidationError : {e}"
    except ValueError as e:
        return False, f"Invalid order_id: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"


async def collect_country_report_from_orders(orders):
    print('[INFO][START] Collect country report from orders')
    try:
        true_orders = [int(order) for order in orders]
        countries: set = await get_country_by_orders_id(true_orders)
        print('COUNTRIES SET', countries)
        if len(countries) == 1:
            return {'country': [*countries][0]}
        elif len(countries) > 1:
            return {'error': 'Multiple countries',
                    'country': str([*countries])}
        else:
            return {'country': 'FirstCall'}
    except Exception as e:
        return {'error': f"Unexpected error: {e}"}
