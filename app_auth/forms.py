from django import forms
from app_auth.models import CustomUser


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, label="Username")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")


class RegistrationForm(forms.Form):

    username = forms.CharField(max_length=100, label="Логин", required=True)
    email = forms.EmailField(label="Почта", required=True)
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль", required=True)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Подтверждение пароля", required=True)


    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError('Пользователь с таким логином уже существует')
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Пароли не совпадают')
        return cleaned_data


class ProfileForm(forms.Form):
    first_name = forms.CharField(max_length=100, label="Имя", required=False)
    last_name = forms.CharField(max_length=100, label="Фамилия", required=False)
    patronymic_name = forms.CharField(max_length=100, label="Отчество", required=False)
    phone = forms.CharField(max_length=15, label="Телефон", required=False)
    address = forms.CharField(max_length=255, label="Адрес", required=False)
    telegram_id = forms.IntegerField(label="Telegram ID", required=False)

