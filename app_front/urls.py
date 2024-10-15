from django.urls import path

from app_front.views import StartingPageView, KazakhstanPageView, TradeinnPageView, AboutUsPageView, ContactsPageView, \
    TariffsPageView, LkHelloPageView, LkCreateOrderPageView, LkOrdersPageView, LkPreordersPageView, LkProfilePageView, \
    LkMessagesPageView, LkLogoutPageView, testing_view, LkOrderPageView

urlpatterns = [
    path('', StartingPageView.as_view(), name='home'),
    path('test/', testing_view, name='test'),
    path('kazakhstan/', KazakhstanPageView.as_view(), name='kazakhstan'),
    path('trade_inn/', TradeinnPageView.as_view(), name='trade_inn'),
    path('about_us/', AboutUsPageView.as_view(), name='about_us'),
    path('contacts/', ContactsPageView.as_view(), name='contacts'),
    path('tariffs/', TariffsPageView.as_view(), name='tariffs'),
    path('lk/', LkHelloPageView.as_view(), name='lk-start'),
    path('lk/create_order/', LkCreateOrderPageView.as_view(), name='lk-create-order'),
    path('lk/orders/', LkOrdersPageView.as_view(), name='lk-orders'),
    path('lk/order/<int:order_id>',LkOrderPageView.as_view(), name='lk-order'),
    path('lk/preorders/', LkPreordersPageView.as_view(), name='lk-pre-orders'),
    path('lk/profile/', LkProfilePageView.as_view(), name='lk-profile'),
    path('lk/messages/', LkMessagesPageView.as_view(), name='lk-messages'),
    path('lk/logout/', LkLogoutPageView.as_view(), name='lk-logout')
]