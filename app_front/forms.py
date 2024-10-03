from django import forms
from django.forms import formset_factory


class OrderForm(forms.Form):
    country = forms.ChoiceField(
        label='Где покупаем?',
        choices=[
            ('USA', 'США'),
            ('EUROPE', 'Европа'),
            ('ENGLAND', 'Англия'),
            ('OTHER', 'Другое'),
        ],
        widget=forms.RadioSelect
    )




class UnregisteredOrderForm(OrderForm):
    url = forms.CharField(
        label='Ссылка на товар:',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Например: https://www.amazon.com/'})
    )
    price = forms.CharField(
        label='Стоимость товара:',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Например: 100 Долларов'})
    )
    count = forms.IntegerField(
        label='Количество товара:',
        required=True,
        widget=forms.NumberInput(attrs={'placeholder': 'Например: 5 штук'})
    )
    comment = forms.CharField(
        label='Комментарий к заказу:',
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Любая информация которая вам покажется важной. Например: размер или цвет',
                                     'rows': 3})
    )
    email = forms.EmailField(
        label='Email:',
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Введите ваш email'})
    )
    phone = forms.CharField(
        label='Телефон:',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Введите ваш телефон'})
    )

class RegisterOrderItemForm(forms.Form):
    goods_link = forms.CharField(
        label='Ссылка на товар:',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Например: https://www.amazon.com/'})
    )
    count = forms.IntegerField(
        label='Количество товара:',
        required=True,
        widget=forms.NumberInput(attrs={'placeholder': 'Например: 5 штук'})
    )
    comment = forms.CharField(
        label='Комментарий к товару:',
        required=False,
        widget=forms.TextInput(attrs={'placeholder':  'Например: размер или цвет',
                                     'rows': 1})
    )

RegisterOrderItemFormSet = formset_factory(RegisterOrderItemForm, extra=1, max_num=10)
