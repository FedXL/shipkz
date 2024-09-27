import json

from django.forms import formset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from app_front.forms import UnregisteredOrderForm, OrderForm, RegisterOrderItemForm
from app_front.mixins import ActiveUserConfirmMixin
from app_front.utils import generate_jwt_token
from legacy.models import Exchange


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

class StartingPageView(View):
    def get(self, request):
        form = UnregisteredOrderForm()
        return render(request, 'pages/start.html', {'form': form})

class KazakhstanPageView(View):
    def get(self, request):
        form = UnregisteredOrderForm()
        return render(request, 'pages/kazakhstan.html', {'form': form})

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

class LkHelloPageView(ActiveUserConfirmMixin,View):
    def get(self, request):
        return render(request, 'lk-pages/lk-hello-page.html')

class LkCreateOrderPageView(ActiveUserConfirmMixin,View):
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

class LkOrdersPageView(ActiveUserConfirmMixin, View):
    def get(self, request):
        return render(request, 'lk-pages/lk-orders-page.html')

class LkPreordersPageView(ActiveUserConfirmMixin, View):
    def get(self, request):
        return render(request, 'lk-pages/lk-pre-orders-page.html')

class LkProfilePageView(View):
    def get(self, request):
        return render(request, 'lk-pages/lk-profile-page.html')

class LkMessagesPageView(ActiveUserConfirmMixin, View):
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