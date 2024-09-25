from django.contrib import admin
from django.db import models
from .models import (
    AlembicVersion, Buyers, Discounts,
    Documents, EmailTask, Exchange, FastAnswers,
    Jwt, Managers, Messages, OrderStatus, OrderStatusInfo, Orders, ParceTask,
    Photos, Posts, RootUsers, Services, UserMain, Users, UsersApp, WebDocs,
    WebMessages, WebPhotos, WebUsers, WebUsersMeta, Websockets, WebsocketsSupport
)

class ReadOnlyAdminMixin:
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        for field in self.model._meta.fields:
            if isinstance(field, models.ForeignKey):
                readonly_fields += (field.name,)
        return readonly_fields

class AlembicVersionAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = [field.name for field in AlembicVersion._meta.fields]

class BuyersAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = [field.name for field in Buyers._meta.fields]

class DiscountsAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = [field.name for field in Discounts._meta.fields]

class DocumentsAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = [field.name for field in Documents._meta.fields]

class EmailTaskAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = [field.name for field in EmailTask._meta.fields]

class ExchangeAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = [field.name for field in Exchange._meta.fields]

class FastAnswersAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = [field.name for field in FastAnswers._meta.fields]

class JwtAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = [field.name for field in Jwt._meta.fields]

class ManagersAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = [field.name for field in Managers._meta.fields]

class MessagesAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = [field.name for field in Messages._meta.fields]

class OrderStatusAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = [field.name for field in OrderStatus._meta.fields]

class OrderStatusInfoAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = [field.name for field in OrderStatusInfo._meta.fields]

class OrdersAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = [field.name for field in Orders._meta.fields]

class ParceTaskAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = [field.name for field in ParceTask._meta.fields]

class PhotosAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = [field.name for field in Photos._meta.fields]

class PostsAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = [field.name for field in Posts._meta.fields]

class RootUsersAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = [field.name for field in RootUsers._meta.fields]

class ServicesAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = [field.name for field in Services._meta.fields]

class UserMainAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = [field.name for field in UserMain._meta.fields]

class UsersAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = [field.name for field in Users._meta.fields]

class UsersAppAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = [field.name for field in UsersApp._meta.fields]

class WebDocsAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = [field.name for field in WebDocs._meta.fields]

class WebMessagesAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ['id', 'message_body', 'is_answer', 'user', 'message_type', 'is_read']

class WebPhotosAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = [field.name for field in WebPhotos._meta.fields]

class WebUsersAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ['user_id', 'user_name', 'web_username']

class WebUsersMetaAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = [field.name for field in WebUsersMeta._meta.fields]

class WebsocketsAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = [field.name for field in Websockets._meta.fields]

class WebsocketsSupportAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = [field.name for field in WebsocketsSupport._meta.fields]

admin.site.register(AlembicVersion, AlembicVersionAdmin)
admin.site.register(Buyers, BuyersAdmin)
admin.site.register(Discounts, DiscountsAdmin)
admin.site.register(Documents, DocumentsAdmin)
admin.site.register(EmailTask, EmailTaskAdmin)
admin.site.register(Exchange, ExchangeAdmin)
admin.site.register(FastAnswers, FastAnswersAdmin)
admin.site.register(Jwt, JwtAdmin)
admin.site.register(Managers, ManagersAdmin)
admin.site.register(Messages, MessagesAdmin)
admin.site.register(OrderStatus, OrderStatusAdmin)
admin.site.register(OrderStatusInfo, OrderStatusInfoAdmin)
admin.site.register(Orders, OrdersAdmin)
admin.site.register(ParceTask, ParceTaskAdmin)
admin.site.register(Photos, PhotosAdmin)
admin.site.register(Posts, PostsAdmin)
admin.site.register(RootUsers, RootUsersAdmin)
admin.site.register(Services, ServicesAdmin)
admin.site.register(UserMain, UserMainAdmin)
admin.site.register(Users, UsersAdmin)
admin.site.register(UsersApp, UsersAppAdmin)
admin.site.register(WebDocs, WebDocsAdmin)
admin.site.register(WebMessages, WebMessagesAdmin)
admin.site.register(WebPhotos, WebPhotosAdmin)
admin.site.register(WebUsers, WebUsersAdmin)
admin.site.register(WebUsersMeta, WebUsersMetaAdmin)
admin.site.register(Websockets, WebsocketsAdmin)
admin.site.register(WebsocketsSupport, WebsocketsSupportAdmin)