import datetime
from os import getenv

from django.conf import settings
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
from app_auth.forms import RegistrationForm, RecoveryPasswordForm, RecoveryPasswordFormChangePasswordForm
from app_auth.models import CustomUser, Profile
from app_auth.serializers import UnregRegistrationSerializer
from app_front.management.unregister_authorization.token import handle_token, token_handler, create_token, check_token
from app_front.management.utils import get_user_ip
from legacy.models import WebUsers
from app_auth.tasks import send_verification_email_task, send_repair_password_email_task


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


class RecoveryPasswordView(View):
    def get(self, request):
        form = RecoveryPasswordForm()
        return render(request, 'registration/recovery_password_first_step.html',context={'form': form})

    def post(self, request):
        form = RecoveryPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            profile = Profile.objects.filter(email=email).first()
            if not profile:
                messages.success(request, f'Письмо для восстановления пароля отправлено на {email}.')
                messages.success(request, 'Если вы не получили письмо, проверьте правильность введенного адреса электронной почты.')
                return HttpResponseRedirect(reverse('auth_messages'))
            else:
                ip = get_user_ip(request)
                user = profile.user
                token  = create_token(username=user.username,
                                      user_id=user.id,
                                      timedelta=datetime.timedelta(hours=12),
                                      ip=ip, secret=settings.REPAIR_PASSWORD_SECRET)

                user.repair_verification_token = token
                user.save()
                messages.success(request, f'Письмо для восстановления пароля отправлено на {email}.')
                send_repair_password_email_task.delay(to_mail=user.email, token=user.repair_verification_token)
                return HttpResponseRedirect(reverse('auth_messages'))
        return render(request, 'registration/recovery_password_first_step.html', {'form': form})


class ConfirmRecoveryPasswordView(View):
    def get(self, request):
        token = request.GET.get('token')
        if not token:
            messages.error(request, 'A токен, токен то где?')
            return render(request, 'registration/auth_messages.html')
        token_dict, comment = check_token(token, secret=settings.REPAIR_PASSWORD_SECRET, is_comment=True)
        if not token_dict:
            messages.error(request, f'Что то пошло не так, пишите в администрацию если эта ошибка повторится')
            messages.error(request, 'токен странный')
            messages.error(request, comment)
            return render(request, 'registration/auth_messages.html')
        user = CustomUser.objects.filter(repair_verification_token=token).first()
        if not user:
            messages.error(request, 'Что то пошло не так, пишите в администрацию если эта ошибка повторится.')
            messages.error(request, 'Пользователь не найден')
            return render(request, 'registration/auth_messages.html')
        token_user_id = token_dict.get('user_id')
        if token_user_id != user.id:
            messages.error(request, 'Что то пошло не так, пишите в администрацию если эта ошибка повторится.')
            messages.error(request, 'Айди равенство')
            return render(request, 'registration/auth_messages.html')
        user_ip = get_user_ip(request)
        if token_dict.get('ip') != user_ip:
            messages.error(request, 'Что то пошло не так, пишите в администрацию если эта ошибка повторится.')
            messages.error(request, 'IP равенство')
            return render(request, 'registration/auth_messages.html')
        form = RecoveryPasswordFormChangePasswordForm(initial={'token': token})

        return render(request, 'registration/recovery_password_second_step.html', context={'form': form})


    def post (self,request):
        form = RecoveryPasswordFormChangePasswordForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data.get('token')
            if not token:
                messages.error(request, 'Что то пошло не так, пишите в администрацию если эта ошибка повторится.')
                return render(request, 'registration/auth_messages.html')
            password = form.cleaned_data.get('password')
            user = CustomUser.objects.filter(repair_verification_token=token).first()
            if not user:
                messages.error(request, 'Что то пошло не так, пишите в администрацию если эта ошибка повторится.')
                return render(request, 'registration/auth_messages.html')
            token_dict = check_token(token, secret=settings.REPAIR_PASSWORD_SECRET)
            if not token_dict:
                messages.error(request, 'Что то пошло не так, пишите в администрацию если эта ошибка повторится.')
                return render(request, 'registration/auth_messages.html')
            user_id = token_dict.get('user_id')
            if user_id != user.id:
                messages.error(request, 'Что то пошло не так, пишите в администрацию если эта ошибка повторится.')
                return render(request, 'registration/auth_messages.html')
            if token_dict.get('ip') != get_user_ip(request):
                messages.error(request, 'Что то пошло не так, пишите в администрацию если эта ошибка повторится.')
                return render(request, 'registration/auth_messages.html')

            user.set_password(password)
            user.repair_verification_token = None
            user.save()
            messages.success(request, 'Пароль успешно изменен')
            return render(request, 'registration/auth_messages.html')
        else:
            messages.error(request, 'Что то пошло не так, пишите в администрацию если эта ошибка повторится.')
            return render(request, 'registration/recovery_password_second_step.html', {'form': form})
