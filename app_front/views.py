import json
from typing import Tuple
from django.conf import settings
from django.contrib import messages
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
from app_front.management.orders.orders_handler import get_orders_by_username_pre, get_orders_by_username_full, \
    body_parser
from app_front.management.unregister_authorization.token import check_token, handle_no_token_comeback_version
from app_front.management.utils import get_user_ip
from app_front.utils import generate_jwt_token
from legacy.models import Exchange, WebUsers, Orders, WebUsersMeta
from app_front.tasks import unregister_web_task_way, registered_web_task_way
from legacy.serializers import OrderFullSerializer, OrdersSerializerPre


class TariffsPageView(View):
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


def auth_cookie_handler (request) -> Tuple[HttpResponse, str, WebUsers,str]:
    """return [response, token, web_user,user_ip] check ShipKzAuthorization cookie and return token and web_user"""
    user_ip = get_user_ip(request)
    token = request.COOKIES.get('ShipKZAuthorization', None)
    decoded_token = check_token(token)
    if decoded_token:
        web_username = decoded_token.get('username')
        web_user = WebUsers.objects.filter(web_username=web_username).first()
    else:
        token, web_user = handle_no_token_comeback_version(user_ip=user_ip)
    response = render(request, template_name='registration/auth_messages.html')
    response.set_cookie('ShipKZAuthorization',
                        token,
                        max_age=14 * 24 * 60 * 60,
                        httponly=False,
                        secure=not settings.DEBUG
                        )
    return response, token, web_user, user_ip


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
            pointer = 'registered'
            return redirect('lk-create-order')
        else:
            form = UnregisteredOrderForm(request.POST)
            pointer = 'unregistered'
        if form.is_valid():
            data = form.cleaned_data
            form_data = form.cleaned_data
            if pointer == 'unregistered':
                messages.success(request, 'Ваша заявка успешно получена успешно получена')
                messages.success(request, 'В ближайшее время с вами свяжется наш менеджер для уточнения деталей')
                response,token,web_user,user_ip = auth_cookie_handler(request)
                unregister_web_task_way.delay(data=form_data, web_user_id=web_user.user_id, user_ip=user_ip)
                return response
            elif pointer =='registered':
                messages.error(request, 'Как вы сюда попали? Такого быть не должно, что то сломалось.')
                messages.error(request, 'Пожалуйста, обратитесь к администратору')
                redirect('auth_messages')
        else:
            return render(request, template_name=self.template_name,context={'form': form,'pointer': pointer})


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

    def post(self, request):
        form = OrderForm(request.POST)
        formset = RegisterOrderItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            data = form.cleaned_data
            form_set_data = formset.cleaned_data
            user_ip = get_user_ip(request)
            web_user = WebUsers.objects.filter(web_username=request.user.username).first()
            items_parser_data_for_legacy_bot_agrh = body_parser(form_set_data)
            data['items'] = items_parser_data_for_legacy_bot_agrh
            data = json.dumps(data)
            order = Orders.objects.create(
                type='WEB_ORDER',
                body=data,
                user_ip=user_ip,
                web_user=web_user
            )

            messages.success(request, f'Заявка №{order.id} успешно создана!')
            registered_web_task_way.delay(order_id=order.id)
            return HttpResponseRedirect(reverse('lk-pre-orders'))
        return render(request, 'lk-pages/lk-create-order-page.html', {'form': form, 'formset': formset})

class LkOrdersPageView(ActiveUserConfirmMixin, EmailVerificationRequiredMixin, View):
    def get(self, request):
        data=get_orders_by_username_full(request.user.username)
        return render(request, 'lk-pages/lk-orders-page.html',context={'data':data})


class LkOrderPageView(ActiveUserConfirmMixin, EmailVerificationRequiredMixin, View):
    def get(self, request,order_id):
        user = request.user
        web_user = user.profile.web_user
        order = Orders.objects.filter(id=order_id,web_user=web_user).first()
        if order:
            data = OrderFullSerializer(order).data
            data_details = OrdersSerializerPre(order).data
            return render(request, 'lk-pages/lk-order-page.html', context={'order': data,'data_details':data_details})
        messages.error(request, f'У вас нет доступа к данным этого заказа {order_id}.')
        return HttpResponseRedirect(reverse('lk-pre-orders'))


class LkPreordersPageView(ActiveUserConfirmMixin, EmailVerificationRequiredMixin, View):
    def get(self, request):
        data=get_orders_by_username_pre(request.user.username, pre=True)
        return render(request, 'lk-pages/lk-pre-orders-page.html',context={'data':data})



class LkPreordersDeletePageView(ActiveUserConfirmMixin, EmailVerificationRequiredMixin, View):
    def post(self,request):
        order_id=request.POST.get('order_id')
        user = request.user
        order = Orders.objects.filter(id=order_id,web_user=user.profile.web_user).first()
        if order:
            order.delete()
            messages.success(request, f'Заказ №{order_id} успешно удален.')
            return HttpResponseRedirect(reverse('lk-pre-orders'))
        messages.error(request, f'У вас нет доступа к данным этого заказа {order_id}.')
        return HttpResponseRedirect(reverse('auth_messages'))



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

class LkMessagesPageView(ActiveUserConfirmMixin,
                         EmailVerificationRequiredMixin,
                         View):
    def get(self, request):
        user = request.user
        profile = get_object_or_404(Profile, user=user)
        web_user = WebUsers.objects.filter(web_username=user.username).first()
        username = web_user.web_username
        user_id = web_user.user_id
        token=generate_jwt_token(user_id, username)
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



