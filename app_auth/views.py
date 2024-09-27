from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import CreateView, TemplateView, FormView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from app_auth.forms import RegistrationForm


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
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})



class LogoutCustomView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('home'))



class ConfirmEmailView(APIView):
    def get(self, request, *args, **kwargs):
        token = request.query_params.get('token')
        if not token:
            return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(profile__email_confirmation_token=token)
            user.profile.email_confirmed = True
            user.profile.email_confirmation_token = ''
            user.profile.save()
            return Response({'message': 'Email confirmed successfully'}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

class AllertsView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('home'))