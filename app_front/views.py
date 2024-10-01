import json
from django.forms import formset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import View

from app_auth.forms import ProfileModelForm
from app_auth.mixins import ActiveUserConfirmMixin
from app_auth.mixins import EmailVerificationRequiredMixin
from app_auth.models import Profile
from app_front.forms import UnregisteredOrderForm, OrderForm, RegisterOrderItemForm, RegisterOrderItemFormSet
from app_front.management.orders.ai_try import my_logger
from app_front.management.unregister_authorization.token import check_token
from app_front.management.unregister_authorization.unregister_web_users import get_unregister_web_user
from app_front.management.utils import get_user_ip
from app_front.utils import generate_jwt_token
from legacy.models import Exchange, WebUsers, Orders
from legacy.serializers import OrdersSerializer

class TariffsPageView(View):
    """
    {
        "sber_usd": {
            "price": 99.89,
            "data": "Актуально на 21:00 по Москве, 26 сентября 2024 г."
        },
        "sber_euro": {
            "price": 112.98,
            "data": "Актуально на 21:00 по Москве, 26 сентября 2024 г."
        },
        "usd": {
            "price": 92.388,
            "data": "на 26.09.2024"
        },
        "eur": {
            "price": 103.4758,
            "data": "на 26.09.2024"
        }
    }
    """
    def get(self, request):
        eur_obj = Exchange.objects.get(valuta='eur')
        usd_obj = Exchange.objects.get(valuta='usd')
        sber_usd_obj = Exchange.objects.get(valuta='sber_usd')
        sber_euro_obj = Exchange.objects.get(valuta='sber_euro')
        exchange_rates ={'sber_usd': {
                                                    'price': sber_usd_obj.price,
                                                    'data': sber_usd_obj.data
                                                },
                                                'sber_euro': {
                                                    "price": sber_euro_obj.price,
                                                    "data": sber_euro_obj.data
                                                },
                                                'usd': {
                                                    "price": usd_obj.price,
                                                    "data": usd_obj.data
                                                },
                                                'eur': {
                                                    "price": eur_obj.price,
                                                    "data": eur_obj.data
                                                }
                                            }
        json_rates = json.dumps(exchange_rates)
        data = {'exchange_rate': json_rates}


        return render(request,
                      template_name='pages/tariffs.html',
                      context={'data': data})

class BaseOrderView(View):
    template_name = ""
    def get(self, request):
        customer = request.user
        if  customer.is_authenticated and customer.email_verified:
            form = OrderForm()
            formset = RegisterOrderItemFormSet()
            pointer = 'registered'
            return render(request, self.template_name, {'form': form, 'formset': formset, 'pointer': pointer})
        else:
            pointer = 'unregistered'
            form = UnregisteredOrderForm()
            return render(request, self.template_name, {'form': form, 'pointer': pointer})

    def post(self, request):
        customer = request.user
        if customer.is_authenticated and customer.email_verified:
            form = OrderForm(request.POST)
            formset = RegisterOrderItemFormSet(request.POST)
            pointer = 'registered'
        else:
            form = UnregisteredOrderForm(request.POST)
            formset = None
            pointer = 'unregistered'
        if form.is_valid() and  (formset is None or formset.is_valid()):
            data = form.cleaned_data
            user_ip = get_user_ip(request)
            form_data = form.cleaned_data
            if pointer == 'unregistered':
                my_logger.info(request.session)
                shipkz_authorization = request.COOKIES.get('ShipKZAuthorization',None)
                if shipkz_authorization:
                    decoder_token = check_token(shipkz_authorization)
                    username = decoder_token.get('username')
                username = "UNREG_" + str(session_number)
                web_user, create = WebUsers.objects.get_or_create(web_username=username)
                order = Orders.objects.create(
                    type='WEB_ORDER',
                    body=form_data,
                    user_ip=user_ip,
                    web_user=web_user
                )


            return render(request,template_name='pages/success.html',context={"pointer":pointer,"result":"success","data":data})
        else:
            return render(request,template_name=self.template_name,context={'form': form, 'formset': formset, 'pointer': pointer})


class StartingPageView(BaseOrderView):
    template_name = 'pages/start.html'

class KazakhstanPageView(BaseOrderView):
    template_name = 'pages/kazakhstan.html'


class TradeinnPageView(View):
    def get(self, request):
        form = UnregisteredOrderForm()
        return render(request, 'pages/tradeinn.html', {'form': form})

class AboutUsPageView(View):
    def get(self, request):
        return render(request, 'pages/about_us.html')

class ContactsPageView(View):
    def get(self, request):
        return render(request, 'pages/contacts.html')






class LkHelloPageView(ActiveUserConfirmMixin,
                    EmailVerificationRequiredMixin,
                      View):
    def get(self, request):
        return render(request, 'lk-pages/lk-hello-page.html')

class LkCreateOrderPageView(ActiveUserConfirmMixin,EmailVerificationRequiredMixin,View):
    def get(self, request):
        RegisterOrderItemFormSet = formset_factory(RegisterOrderItemForm, extra=1, max_num=10)
        if request.method == 'POST':
            order_form = OrderForm(request.POST)
            formset = RegisterOrderItemFormSet(request.POST)
            if order_form.is_valid() and formset.is_valid():
                where_to = order_form.cleaned_data['where_to']
                for form in formset:
                    goods_link = form.cleaned_data['goods_link']
                    count = form.cleaned_data['count']
                    comment = form.cleaned_data.get('comment', '')
                    print(f"Товар: {goods_link}, Количество: {count}, Комментарий: {comment}")
                return HttpResponse("Форма успешно отправлена")
        else:
            order_form = OrderForm()
            formset = RegisterOrderItemFormSet()

        return render(request, template_name='lk-pages/lk-create-order-page.html',
                      context={
            'form': order_form,
            'formset': formset,
        })

class LkOrdersPageView(ActiveUserConfirmMixin, EmailVerificationRequiredMixin, View):
    def get(self, request):
        data=get_orders_by_username(request.user.username)
        return render(request, 'lk-pages/lk-orders-page.html',context={'data':data})

class LkPreordersPageView(ActiveUserConfirmMixin, EmailVerificationRequiredMixin, View):
    def get(self, request):
        return render(request, 'lk-pages/lk-pre-orders-page.html')


class LkProfilePageView(View):
    def get(self, request):
        user = request.user
        if user.is_anonymous:
            return HttpResponseRedirect(reverse('login'))

        profile = get_object_or_404(Profile, user=user)
        form = ProfileModelForm(instance=profile)
        return render(request, 'lk-pages/lk-profile-page.html', {'form': form})

    def post(self, request):
        user = request.user
        if user.is_anonymous:
            return HttpResponseRedirect(reverse('login'))

        profile = get_object_or_404(Profile, user=user)
        form = ProfileModelForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('lk-profile')
        return render(request, 'lk-pages/lk-profile-page.html', {'form': form})

class LkMessagesPageView(ActiveUserConfirmMixin,EmailVerificationRequiredMixin, View):
    def get(self, request):
        token=generate_jwt_token(1, 'admin')
        return render(request,
                      template_name='lk-pages/lk-messages-page.html',
                      context={'token': token})

class LkLogoutPageView(View):
    def get(self, request):
        return HttpResponseRedirect(reverse('logout'))


def testing_view(request):
    return render(request, 'pages/test.html')


def make_text_for_status(data):
    """-заказ выкуплен в магазине
- заказ отправлен в казахстан (получен трек)  / заказ в пути
- заказ поступил на территорию казахстана
- заказ получен для последующей отправки
- заказ отправлен в рф
- закз получен клиентом"""

    order_status_info = data.get('order_status_info')
    is_forwarder = order_status_info.get('is_forwarder_way')
    check_list_1 = [
        'arrived_to_forwarder',
        'send_to_host_country',
        'received_in_host_country',
        'send_to_ru'

    ]

    check_list_2 = [
        'send_to_host_country',
        'arrived_to_host_country',
        'received_in_host_country',
        'send_to_ru'
    ]

    if is_forwarder:
        check_list = check_list_1
    else:
        check_list = check_list_2

    result = {}
    count = 2
    for check in check_list:
        data = order_status_info.get(check)
        if data:
            result[count] = True
        else:
            result[count] = False
        count += 1
    return result

def get_orders_by_username(username):
    web_user = WebUsers.objects.filter(web_username=username).first()
    orders = Orders.objects.filter(web_user=web_user).order_by('-id')
    serializer = OrdersSerializer(orders, many=True)
    serialized_data = serializer.data
    return serialized_data



# async def get_orders_by_username(username: str, variant='paid'):
#     async with AsyncSession(async_engine) as session:
#         async with session.begin():
#             stmt = select(WebUser.user_id).where(WebUser.web_username == username)
#             query = await session.execute(stmt)
#             web_user_id = query.scalar_one_or_none()
#             if not web_user_id:
#                 return False, f"Cant to find user with {username}"
#             stmt = (select(Order, OrderStatusInfo)
#                     .select_from(join(Order, OrderStatusInfo, Order.id == OrderStatusInfo.order_id, isouter=True))
#                     .where(Order.web_user == web_user_id)
#                     .order_by(desc(Order.id)))
#             result_all = await session.execute(stmt)
#             rows = result_all.fetchall()
#             orders_list = []
#             match variant:
#                 case "paid":
#                     for row in rows:
#                         _order = row[0]
#                         _order_dict = _order.to_dict()
#                         sring = _order.body
#                         _order_dict['body'] = json.loads(sring)
#                         _status = row[1]
#                         if _status:
#                             _status_dict = _status.to_dict()
#                             result_dict = {**_order_dict, 'order_status_info': {**_status_dict}}
#                             status_check = make_text_for_status(result_dict)
#                             result_dict['order_status_info']['progres_bar'] = status_check
#                             if result_dict['order_status_info']['host_country'] == 'KAZAKHSTAN':
#                                 result_dict['order_status_info']['host_country'] = 'Казахстан'
#                             elif result_dict['order_status_info']['host_country'] == 'KYRGYZSTAN':
#                                 result_dict['order_status_info']['host_country'] = 'Кыргызстан'
#                                 orders_list.append(result_dict)
#                             orders_list.append(result_dict)
#                         else:
#                             continue
#                 case 'not_yet':
#                     for row in rows:
#                         _order = row[0]
#                         _order_dict = _order.to_dict()
#                         sring = _order.body
#                         _order_dict['body'] = json.loads(sring)
#                         _status = row[1]
#                         if _status:
#                             continue
#                         else:
#                             result_dict = {**_order_dict}
#                             orders_list.append(result_dict)
#
#     return orders_list
