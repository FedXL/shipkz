from django.urls import path
from app_auth.views import SignUpView, LoginView, LogoutCustomView, AllertsView, ConfirmEmailMessageView, \
     UniqueUserNameApiView


urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutCustomView.as_view(), name='logout'),
    path('confirm_email/', ConfirmEmailMessageView.as_view(), name='confirm_email'),
    path('allert/', AllertsView.as_view(), name='allert'),
    path('unique_username/', UniqueUserNameApiView.as_view(), name='check_for_unique_username'),
]