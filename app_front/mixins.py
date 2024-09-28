from django.contrib.auth.mixins import AccessMixin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse


class ActiveUserConfirmMixin(AccessMixin):
    """Миксин для проверки, что пользователь подтвердил email."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_active:
            return HttpResponseRedirect(reverse('logout'))
        return super().dispatch(request, *args, **kwargs)