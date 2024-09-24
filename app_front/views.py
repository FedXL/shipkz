from django.forms import formset_factory
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from app_front.forms import UnregisteredOrderForm, RegisterOrderItemFormSet, OrderForm, RegisterOrderItemForm


class TariffsPageView(View):
    def get(self, request):
        return render(request, 'pages/tariffs.html')


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

class LkHelloPageView(View):
    def get(self, request):
        return render(request, 'lk-pages/lk-hello-page.html')

class LkCreateOrderPageView(View):
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

class LkOrdersPageView(View):
    def get(self, request):
        return render(request, 'lk-pages/lk-orders-page.html')

class LkPreordersPageView(View):
    def get(self, request):
        return render(request, 'lk-pages/lk-pre-orders-page.html')

class LkProfilePageView(View):
    def get(self, request):
        return render(request, 'lk-pages/lk-profile-page.html')

class LkMessagesPageView(View):
    def get(self, request):
        return render(request, 'lk-pages/lk-messages-page.html')

class LkLogoutPageView(View):
    def get(self, request):
        return render(request, 'lk-pages/lk-logout-page.html')

def form_for_register_user(request):
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

    return render(request, 'pages/forma_test.html', {
        'form': order_form,
        'formset': formset,
    })



