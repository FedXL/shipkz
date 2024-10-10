import logging

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import  AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.middleware.csrf import CsrfViewMiddleware
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import  FormView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ObjectDoesNotExist
from app_auth.forms import RegistrationForm
from app_auth.models import CustomUser, Profile
from app_auth.serializers import UnregRegistrationSerializer
from app_front.management.unregister_authorization.token import handle_token, token_handler
from legacy.models import WebUsers
from app_auth.tasks import  send_verification_email_task


class LoginView(FormView):
    template_name = 'registration/login.html'
    success_url = reverse_lazy('lk-profile')
    form_class = AuthenticationForm

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        return super().form_valid(form)

def warning_messages_view(request):
    return render(request, 'registration/auth_messages.html')

class SignUpView(View):
    form_class = RegistrationForm
    success_url = reverse_lazy('confirm_email_message')
    template_name = 'registration/signup.html'

    def get(self, request):
        form = self.form_class()
        api_check_url = reverse('check_for_unique_username')
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = CustomUser(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],)
            user.set_password(form.cleaned_data['password'])
            user.save()
            web_user = WebUsers.objects.create(web_username=form.cleaned_data['username'],
                                               user_name=form.cleaned_data['username'],)
            profile = Profile(user=user,email=form.cleaned_data['email'], web_user=web_user)
            profile.save()
            login(request, user)
            send_verification_email_task.delay(to_mail=user.email,
                                               user=user.username,
                                               token=user.verification_token)
            return HttpResponseRedirect(self.success_url)
        return render(request, self.template_name, {'form': form})


class LogoutCustomView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('home'))


class ConfirmEmailMessageView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        if user.email_verified:
            return HttpResponseForbidden("Your email has not been verified.")
        else:
            return render(request,
                          template_name='registration/email_confirm_message.html',
                          context={'user_email': user.email})


class ConfirmEmailPointView(View):
    def get(self, request, *args, **kwargs):
        token = request.GET.get('token')
        if not token:
            messages.error(request, 'Ошибка, токен подтверждения не найден')
            return render(request, 'registration/auth_messages.html', {'user_email': 'Token not found'})
        try:
            user = CustomUser.objects.get(verification_token=token)
            user.email_verified = True
            user.verification_token = None
            user.save()
            messages.success(request, 'Почта успешно подтверждена. Ваша учетная запись активирована')
            return render(request, 'registration/auth_messages.html', {'user_email': user.email})
        except ObjectDoesNotExist:
            messages.error(request, 'Что то пошло не так, токен неправильный.')
            return render(request, 'registration/auth_messages.html', {'user_email': 'User not found'})

class UniqueUserNameApiView(APIView):
    def get(self, request):
        username = request.query_params.get('username')
        if not username:
            return Response({'ok':False,'message':'no username'}, status=status.HTTP_400_BAD_REQUEST)
        if CustomUser.objects.filter(username=username).exists():
            return Response({'ok':False,'message':'name exist'}, status=status.HTTP_200_OK)
        if WebUsers.objects.filter(web_username=username).exists():
            return Response({'ok':False,'message':'name exist'}, status=status.HTTP_200_OK)
        return Response({'ok':True,'name':'available'}, status=status.HTTP_200_OK)



class AllertsView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('home'))


class UnregRegistrationApiView(APIView):
    serializer = UnregRegistrationSerializer
    def post(self, request):
        csrf_middleware = CsrfViewMiddleware(lambda req: None)
        try:
            csrf_middleware.process_view(request, None, None, None)
        except Exception:
            return Response({'error': 'CSRF token invalid or missing'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.serializer(data=request.data)
        if serializer.is_valid():
            token = serializer.data.get('token')
            ip = serializer.data.get('ip')
            token = token_handler(user_ip=ip, token=token)
            return Response({'token': token}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid data','messages':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)