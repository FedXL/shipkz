from django.contrib.auth import login, logout
from django.contrib.auth.forms import  AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, HttpResponseForbidden
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

class SignUpView(View):
    form_class = RegistrationForm
    success_url = reverse_lazy('confirm_email')
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
            profile = Profile(user=user,email=form.cleaned_data['email'],web_user=web_user)
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
                          template_name='registration/confirm_email.html',
                          context={'user_email': user.email})



class ConfirmEmailApiView(APIView):
    def get(self, request, *args, **kwargs):
        token = request.query_params.get('token')
        if not token:
            return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = CustomUser.objects.get(verification_token=token)
            user.email_verified = True
            user.verification_token = ''
            user.profile.save()
            return Response({'message': 'Email confirmed successfully'}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

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