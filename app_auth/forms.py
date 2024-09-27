from django import forms
from django.contrib.auth.models import User  # Используем встроенную модель User в Django

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, label="Username")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")


class RegistrationForm(forms.Form):

    username = forms.CharField(max_length=100, label="Username")
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    phone = forms.CharField(max_length=15, label="Phone")
    billing_address = forms.CharField(max_length=255, label="Billing Address")
    first_name = forms.CharField(max_length=100, label="First Name")
    last_name = forms.CharField(max_length=100, label="Last Name")
    omg_name = forms.CharField(max_length=100, label="OMG Name")

    cdek_address = forms.CharField(max_length=255, label="CDEK Address")


    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Passwords do not match')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

