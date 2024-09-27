from django.urls import path

from app_auth.views import SignUpView, LoginView, LogoutCustomView, ConfirmEmailView, AllertsView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutCustomView.as_view(), name='logout'),
    path('confirm_email/', ConfirmEmailView.as_view(), name='confirm_email'),
    path('allert/', AllertsView.as_view(), name='allert'),
]