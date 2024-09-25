from django.db import models

class AlembicVersion(models.Model):
    version_num = models.CharField(primary_key=True, max_length=32)

    class Meta:
        managed = False
        db_table = 'alembic_version'




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
    valuta = models.CharField(primary_key=True)
    price = models.FloatField(blank=True, null=True)
    data = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'exchange'


class FastAnswers(models.Model):
    body = models.TextField(blank=True, null=True)
    button_name = models.CharField(blank=True, null=True)
    type = models.CharField(blank=True, null=True)
    manager = models.ForeignKey('Managers', models.DO_NOTHING, db_column='manager', to_field='user_id', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'fast_answers'


class Jwt(models.Model):
    user = models.OneToOneField('WebUsers', models.DO_NOTHING, blank=True, null=True)
    jwt_hash = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'jwt'


class Managers(models.Model):
    short_name = models.CharField(blank=True, null=True)
    user = models.OneToOneField('Users', models.DO_NOTHING, blank=True, null=True)
    key = models.CharField(blank=True, null=True)
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
    order_price = models.CharField(blank=True, null=True)
    order = models.ForeignKey('Orders', models.DO_NOTHING, blank=True, null=True)
    manager = models.ForeignKey(Managers, models.DO_NOTHING, to_field='user_id', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_status'


class OrderStatusInfo(models.Model):
    order = models.OneToOneField('Orders', models.DO_NOTHING)
    is_forward = models.BooleanField()
    paid = models.DateTimeField()
    arrived_to_forward = models.DateTimeField(blank=True, null=True)
    got_track = models.DateTimeField(blank=True, null=True)
    arrived_to_host_country = models.DateTimeField(blank=True, null=True)
    received_in_host_country = models.DateTimeField(blank=True, null=True)
    send_to_ru = models.DateTimeField(blank=True, null=True)
    success = models.DateTimeField(blank=True, null=True)
    relative_price = models.CharField()
    shop = models.CharField()
    store_order_number = models.CharField()
    trek = models.CharField(blank=True, null=True)
    cdek = models.CharField(blank=True, null=True)
    post_service = models.CharField(max_length=50, blank=True, null=True)
    host_country = models.CharField(blank=True, null=True)
    buyer = models.BigIntegerField(blank=True, null=True)
    buyer_reward = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_status_info'


class Orders(models.Model):
    client = models.ForeignKey('Users', models.DO_NOTHING, db_column='client', blank=True, null=True)
    buyer = models.ForeignKey(Buyers, models.DO_NOTHING, db_column='buyer', blank=True, null=True)
    type = models.CharField(blank=True, null=True)
    body = models.TextField(blank=True, null=True)
    time = models.DateTimeField(blank=True, null=True)
    web_user = models.ForeignKey('WebUsers', models.DO_NOTHING, db_column='web_user', blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    user_ip = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'orders'


class ParceTask(models.Model):
    order = models.ForeignKey(Orders, models.DO_NOTHING, blank=True, null=True)
    login = models.CharField(blank=True, null=True)
    password = models.CharField(blank=True, null=True)
    type = models.CharField(blank=True, null=True)

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
    name = models.CharField(unique=True, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'posts'


class RootUsers(models.Model):
    telegram_user = models.ForeignKey('Users', models.DO_NOTHING, db_column='telegram_user', blank=True, null=True)
    web_user = models.ForeignKey('WebUsers', models.DO_NOTHING, db_column='web_user', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'root_users'


class Services(models.Model):
    service_name = models.CharField(primary_key=True)
    status = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    report = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'services'


class UserMain(models.Model):
    first_name = models.CharField(max_length=50, blank=True, null=True)
    second_name = models.CharField(max_length=50, blank=True, null=True)
    third_name = models.CharField(max_length=50, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_main'


class Users(models.Model):
    user_id = models.BigIntegerField(primary_key=True)
    user_name = models.CharField(blank=True, null=True)
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
    doc_path = models.CharField(blank=True, null=True)
    message = models.ForeignKey('WebMessages', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'web_docs'


class WebUsers(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(blank=True, null=True)
    web_username = models.CharField(unique=True, blank=True, null=True)
    is_kazakhstan = models.BooleanField(blank=True, null=True)
    last_online = models.DateTimeField(blank=True, null=True)
    last_message_telegramm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'web_users'

class WebMessages(models.Model):
    id = models.BigAutoField(primary_key=True)
    message_body = models.CharField(blank=True, null=True)
    is_answer = models.BooleanField(blank=True, null=True)
    user = models.ForeignKey('WebUsers', models.DO_NOTHING, db_column='user')
    time = models.DateTimeField(blank=True, null=True)
    message_type = models.CharField(blank=True, null=True)
    is_read = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'web_messages'

class WebPhotos(models.Model):
    photo_path = models.CharField(blank=True, null=True)
    message = models.ForeignKey(WebMessages, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'web_photos'

class WebUsersMeta(models.Model):
    meta_id = models.AutoField(primary_key=True)
    field = models.CharField()
    value = models.CharField(blank=True, null=True)
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