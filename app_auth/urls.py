from django.urls import path
from app_auth.views import SignUpView, LoginView, LogoutCustomView, AllertsView, ConfirmEmailMessageView, \
    UniqueUserNameApiView, UnregRegistrationApiView, ConfirmEmailPointView, warning_messages_view, RecoveryPasswordView, \
    ConfirmRecoveryPasswordView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutCustomView.as_view(), name='logout'),
    path('confirm_email/', ConfirmEmailPointView.as_view(), name='confirm_email'),
    path('confirm_email_message/', ConfirmEmailMessageView.as_view(), name='confirm_email_message'),
    path('warning_messages/', warning_messages_view, name='auth_messages'),
    path('allert/', AllertsView.as_view(), name='allert'),
    path('unique_username/', UniqueUserNameApiView.as_view(), name='check_for_unique_username'),
    path('unreg_auth_token/', UnregRegistrationApiView.as_view(), name='api-unreg-auth'),
    path('repair_password/', RecoveryPasswordView.as_view(), name='repair_password'),
    path('confirm_repair_password/', ConfirmRecoveryPasswordView.as_view(), name='repair_password_message'),

]