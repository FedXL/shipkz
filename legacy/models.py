from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

class Buyers(models.Model):
    phone = models.BigIntegerField(blank=True, null=True)
    telegram_id = models.BigIntegerField(blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    second_name = models.CharField(max_length=50, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'buyers'

class Discounts(models.Model):
    is_vip = models.BooleanField(blank=True, null=True)
    user = models.OneToOneField('Users', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'discounts'


class Documents(models.Model):
    document_id = models.TextField(blank=True, null=True)
    message = models.ForeignKey('Messages', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'documents'


class EmailTask(models.Model):
    web_user = models.ForeignKey('WebUsers', models.DO_NOTHING, db_column='web_user')
    text = models.TextField()
    header = models.CharField(max_length=255)
    execute_time = models.DateTimeField()
    status = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'email_task'


class Exchange(models.Model):
    valuta = models.CharField(primary_key=True, max_length=10)
    price = models.FloatField(blank=True, null=True)
    data = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'exchange'


class FastAnswers(models.Model):
    body = models.TextField(blank=True, null=True)
    button_name = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    manager = models.ForeignKey('Managers', models.DO_NOTHING, db_column='manager', to_field='user_id', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'fast_answers'


class Jwt(models.Model):
    user = models.OneToOneField('WebUsers', models.DO_NOTHING, blank=True, null=True)
    jwt_hash = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'jwt'


class Managers(models.Model):
    short_name = models.CharField(max_length=255, blank=True, null=True)
    user = models.OneToOneField('Users', models.DO_NOTHING, blank=True, null=True)
    key = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'managers'


class Messages(models.Model):
    message_body = models.TextField(blank=True, null=True)
    is_answer = models.BooleanField(blank=True, null=True)
    storage = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    time = models.DateTimeField(blank=True, null=True)
    message_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'messages'


class OrderStatus(models.Model):
    status = models.BooleanField(blank=True, null=True)
    order_price = models.CharField(max_length=255, blank=True, null=True)
    order = models.ForeignKey('Orders', models.DO_NOTHING, blank=True, null=True)
    manager = models.ForeignKey(Managers, models.DO_NOTHING, to_field='user_id', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_status'


class OrderStatusInfo(models.Model):
    order = models.OneToOneField('Orders', models.DO_NOTHING, related_name='ori')
    is_forward = models.BooleanField()
    paid = models.DateTimeField()
    arrived_to_forward = models.DateTimeField(blank=True, null=True)
    got_track = models.DateTimeField(blank=True, null=True)
    arrived_to_host_country = models.DateTimeField(blank=True, null=True)
    received_in_host_country = models.DateTimeField(blank=True, null=True)
    send_to_ru = models.DateTimeField(blank=True, null=True)

    success = models.DateTimeField(blank=True, null=True)
    relative_price = models.CharField(max_length=255)
    shop = models.CharField(max_length=255)
    store_order_number = models.CharField(max_length=255)
    trek = models.CharField(max_length=255, blank=True, null=True)
    cdek = models.CharField(max_length=255, blank=True, null=True)
    post_service = models.CharField(max_length=50, blank=True, null=True)
    host_country = models.CharField(max_length=255, blank=True, null=True)
    buyer = models.BigIntegerField(blank=True, null=True)
    buyer_reward = models.CharField(max_length=255, blank=True, null=True)


    class Meta:
        managed = False
        db_table = 'order_status_info'


class  Orders(models.Model):
    client = models.ForeignKey('Users', models.DO_NOTHING, db_column='client', blank=True, null=True)
    buyer = models.ForeignKey(Buyers, models.DO_NOTHING, db_column='buyer', blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    body = models.TextField(blank=True, null=True)
    time = models.DateTimeField(blank=True, null=True, auto_now_add=True)

    web_user = models.ForeignKey('WebUsers', models.DO_NOTHING, db_column='web_user', blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    user_ip = models.CharField(max_length=100, blank=True, null=True)

    def clean(self):
        if not self.client and not self.web_user:
            raise ValidationError('Either client or web_user must be filled.')

    class Meta:
        managed = False
        db_table = 'orders'

class ParceTask(models.Model):
    order = models.ForeignKey(Orders, models.DO_NOTHING, blank=True, null=True)
    login = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'parce_task'


class Photos(models.Model):
    photo_id = models.AutoField(primary_key=True)
    file_id = models.TextField(blank=True, null=True)
    message = models.ForeignKey(Messages, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'photos'


class Posts(models.Model):
    id = models.BigAutoField(primary_key=True)
    message_id = models.BigIntegerField(blank=True, null=True)
    chat_id = models.BigIntegerField(blank=True, null=True)
    name = models.CharField(unique=True, max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'posts'


class Services(models.Model):
    service_name = models.CharField(primary_key=True, max_length=255)
    status = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    report = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'services'


class Users(models.Model):
    user_id = models.BigIntegerField(primary_key=True)
    user_name = models.CharField(max_length=255, blank=True, null=True)
    message_id = models.IntegerField(blank=True, null=True)
    tele_username = models.CharField(max_length=50, blank=True, null=True)
    user_second_name = models.CharField(max_length=50, blank=True, null=True)
    main_user = models.IntegerField(blank=True, null=True)
    is_kazakhstan = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'


class UsersApp(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=250)

    class Meta:
        managed = False
        db_table = 'users_app'


class WebDocs(models.Model):
    doc_path = models.CharField(max_length=255, blank=True, null=True)
    message = models.ForeignKey('WebMessages', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'web_docs'


class WebUsers(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=255, blank=True, null=True) # FIXME: не используется надо бы удалить

    web_username = models.CharField(unique=True, max_length=255, blank=True, null=True)
    is_kazakhstan = models.BooleanField(blank=True, null=True, default=True)
    last_online = models.DateTimeField(blank=True, null=True)
    last_message_telegramm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'web_users'

    def get_chat_id(self):
        if self.is_kazakhstan:
            chat_id = settings.KAZAKHSTAN_CATCH_CHAT
        else:
            chat_id = settings.TRADEINN_CATCH_CHAT
        return chat_id


class WebMessages(models.Model):
    id = models.BigAutoField(primary_key=True)
    message_body = models.CharField(max_length=255, blank=True, null=True)
    is_answer = models.BooleanField(blank=True, null=True)
    user = models.ForeignKey(WebUsers, models.DO_NOTHING, db_column='user')
    time = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    message_type = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'web_messages'

    def as_dict(self):
        result = {'message_id': self.id,
                  'text': self.message_body,
                  'is_answer': self.is_answer,
                  'user_id': self.user.user_id,
                  'time': self.time.strftime("%B %d, %H:%M"),
                  'message_type': self.message_type,
                  'is_read': self.is_read
                  }
        return result


class WebPhotos(models.Model):
    photo_path = models.CharField(max_length=255, blank=True, null=True)
    message = models.ForeignKey(WebMessages, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'web_photos'


class WebUsersMeta(models.Model):
    meta_id = models.AutoField(primary_key=True)
    field = models.CharField(max_length=255)
    value = models.CharField(max_length=255, blank=True, null=True)
    web_user = models.ForeignKey(WebUsers, models.DO_NOTHING, db_column='web_user')

    class Meta:
        managed = False
        db_table = 'web_users_meta'
        unique_together = (('field', 'web_user'),)


class Websockets(models.Model):
    id = models.BigAutoField(primary_key=True)
    socket_id = models.BigIntegerField(blank=True, null=True)
    user = models.OneToOneField(WebUsers, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'websockets'


class WebsocketsSupport(models.Model):
    socket_id = models.BigIntegerField(blank=True, null=True)
    user = models.OneToOneField(WebUsers, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'websockets_support'


class RootUsers(models.Model):
    telegram_user = models.ForeignKey(Users, models.DO_NOTHING, db_column='telegram_user', blank=True, null=True)
    web_user = models.ForeignKey(WebUsers, models.DO_NOTHING, db_column='web_user', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'root_users'
