from django.contrib.auth.mixins import AccessMixin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse

class EmailVerificationRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.email_verified:
            return redirect(reverse('confirm_email'))
        return super().dispatch(request, *args, **kwargs)

class ActiveUserConfirmMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_active:
            return HttpResponseRedirect(reverse('logout'))
        return super().dispatch(request, *args, **kwargs)