# from legacy.legacy_codebase.module_7.utils.create_web_order_parcer import OrderReg, OrderNotReg
# from legacy.models import Orders, WebUsers
# class BaseModel:
#     pass
#
#
# def register_order(data):
#     web_user=data.get('web_user')
#     web_user = WebUsers.objects.filter(web_username=web_user).first()
#     if not web_user:
#         raise ValueError('Web user not found')
#     order = Orders.objects.create()

# class Item(BaseModel):
#     url: str
#     amount: int
#     comment: str
#
# class OrderReg(BaseModel):
#     """order for registered web users"""
#     country: str
#     items: Dict[int, Item]
#     username: str | None = None
#     phone_number: str | None = None
#     cdek_adress: str | None = None
#
#
# class OrderNotReg(BaseModel):
#     country: str
#     url: str
#     price: str
#     comment: str
#     email: str
#     phone: str
#     username: str
#     user_ip: str
#
#
# async def create_order_web(web_order_data: OrderReg | OrderNotReg, user: dict):
#     order = Order(type='WEB_ORDER',
#                   body=web_order_data.model_dump_json())
#     if user.get('user_id') == 0:
#         my_logger.debug(f"start unregistered user branch")
#         order.user_ip = web_order_data.user_ip
#         web_user = web_order_data.username
#         if web_user:
#             order_id, web_user_id = await save_order_web(order=order, web_user=web_user)
#         else:
#             my_logger.error("cant to find webusername in incoming data")
#             raise AssertionError
#     else:
#         my_logger.info(f"start registered user branch")
#         web_user = user.get('username')
#         order_id, web_user_id = await save_order_web(order=order, web_user=web_user)
#     if order_id:
#         return order_id, web_user, web_user_id
#     else:
#         my_logger.error('cant to save order and get order id')
#         raise AssertionError