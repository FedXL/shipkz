
from django.db import models
from django.utils import timezone


class Posts(models.Model):
    """Таблица постов (cms sistem) в каналах"""
    id = models.BigAutoField(primary_key=True)
    message_id = models.BigIntegerField()
    chat_id = models.BigIntegerField()
    name = models.CharField(max_length=255, unique=True)

    def __repr__(self):
        return f"mess: {self.message_id} | chat: {self.chat_id} | name: {self.name}"


class ParceTask(models.Model):
    id = models.AutoField(primary_key=True)
    order_id = models.ForeignKey('Order', on_delete=models.CASCADE)
    login = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    type = models.CharField(max_length=255)


class WebUserMetaData(models.Model):
    meta_id = models.AutoField(primary_key=True)
    field = models.CharField(max_length=255)
    value = models.CharField(max_length=255, null=True, blank=True)
    web_user = models.ForeignKey('WebUser', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('field', 'web_user')

    def to_dict(self):
        return {self.field: self.value}

    def __repr__(self):
        return f"{self.meta_id} | {self.field} | {self.value} | {self.web_user}"


class WebUser(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=255, null=True, blank=True)
    web_username = models.CharField(max_length=255, unique=True)
    is_kazakhstan = models.BooleanField()
    last_online = models.DateTimeField()
    last_message_telegramm_id = models.BigIntegerField(null=True, blank=True)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'user_name': self.user_name,
            'web_username': self.web_username,
            'is_kazakhstan': self.is_kazakhstan,
            'last_online': str(self.last_online),
            'last_message_telegramm_id': self.last_message_telegramm_id
        }


class User(models.Model):
    user_id = models.BigAutoField(primary_key=True)
    user_name = models.CharField(max_length=255)
    message_id = models.IntegerField()  # Видимо это последнее сообщение
    user_second_name = models.CharField(max_length=255)
    tele_username = models.CharField(max_length=255)
    main_user = models.IntegerField()
    is_kazakhstan = models.BooleanField()

    def __repr__(self):
        return f"{self.user_id} | {self.user_name} | {self.user_second_name} | {self.tele_username}"

    def to_dict(self):
        data = {}
        for field in self._meta.fields:
            data[field.name] = getattr(self, field.name)
        return data


class RootUser(models.Model):
    id = models.AutoField(primary_key=True)
    telegram_user = models.ForeignKey('User', on_delete=models.CASCADE)
    web_user = models.ForeignKey('WebUser', on_delete=models.CASCADE)


class WebMessage(models.Model):
    id = models.BigAutoField(primary_key=True)
    message_body = models.TextField()
    is_answer = models.BooleanField()
    user = models.ForeignKey('WebUser', on_delete=models.CASCADE)
    time = models.DateTimeField(default=timezone.now)
    message_type = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(message_type__in=['text', 'photo', 'file', 'caption', 'order', 'document']),
                name='check_message_type')
        ]

    def as_dict(self):
        return {
            'message_id': self.id,
            'text': self.message_body,
            'is_answer': self.is_answer,
            'user_id': self.user_id,
            'time': self.time.strftime("%B %d, %H:%M"),
            'message_type': self.message_type,
            'is_read': self.is_read
        }

    def __repr__(self):
        return f"{self.id} | {self.message_body} | {self.is_answer} | {self.time}"


class Message(models.Model):
    id = models.AutoField(primary_key=True)
    message_body = models.TextField()
    is_answer = models.BooleanField()
    storage_id = models.ForeignKey('User', on_delete=models.CASCADE)
    time = models.DateTimeField(default=timezone.now)
    message_id = models.BigIntegerField()


class WebPhoto(models.Model):
    id = models.AutoField(primary_key=True)
    photo_path = models.CharField(max_length=255)
    message_id = models.ForeignKey('WebMessage', on_delete=models.CASCADE)


class WebDoc(models.Model):
    id = models.AutoField(primary_key=True)
    doc_path = models.CharField(max_length=255)
    message_id = models.ForeignKey('WebMessage', on_delete=models.CASCADE)


class WebSocket(models.Model):
    id = models.BigAutoField(primary_key=True)
    socket_id = models.BigIntegerField()
    user_id = models.ForeignKey('WebUser', on_delete=models.CASCADE, unique=True)


class WebSocketSupport(models.Model):
    id = models.BigAutoField(primary_key=True)
    socket_id = models.BigIntegerField()
    user_id = models.OneToOneField('WebUser', on_delete=models.CASCADE)


class Jwt(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey('WebUser', on_delete=models.CASCADE, unique=True)
    jwt_hash = models.CharField(max_length=255)


class OrderStatus(models.Model):
    id = models.AutoField(primary_key=True)
    status = models.BooleanField()
    order_id = models.ForeignKey('Order', on_delete=models.CASCADE)
    manager_id = models.BigIntegerField()
    order_price = models.CharField(max_length=255)

    def __repr__(self):
        return f'{self.order_id} | {self.order_price} | {self.status}'


class OrderStatusInfo(models.Model):
    id = models.AutoField(primary_key=True)
    order_id = models.ForeignKey('Order', on_delete=models.CASCADE, unique=True)

    is_forward = models.BooleanField()
    paid = models.DateTimeField()
    arrived_to_forward = models.DateTimeField(null=True, blank=True)
    got_track = models.DateTimeField(null=True, blank=True)
    arrived_to_host_country = models.DateTimeField(null=True, blank=True)
    received_in_host_country = models.DateTimeField(null=True, blank=True)
    send_to_ru = models.DateTimeField(null=True, blank=True)
    success = models.DateTimeField(null=True, blank=True)

    relative_price = models.CharField(max_length=255)
    shop = models.CharField(max_length=255)
    store_order_number = models.CharField(max_length=255)
    trek = models.CharField(max_length=255, null=True, blank=True)
    cdek = models.CharField(max_length=255, null=True, blank=True)
    post_service = models.CharField(max_length=255, null=True, blank=True)
    host_country = models.CharField(max_length=255, null=True, blank=True)

    buyer = models.BigIntegerField(null=True, blank=True)
    buyer_reward = models.CharField(max_length=255, null=True, blank=True)

    def __repr__(self):
        return f" order {self.order_id} | init  {self.paid}"

    def to_dict(self):
        result = {
            'order_id': self.order_id,
            'is_forwarder_way': self.is_forward,
            'relative_price': self.relative_price,
            'shop': self.shop,
            'store_order_number': self.store_order_number,
            'trek': self.trek,
            'cdek': self.cdek,
            'shopped': self.paid.strftime("%Y-%m-%d %H:%M"),
            'post_service': self.post_service,
            'host_country': self.host_country,
            'buyer': self.buyer,
            'buyer_reward': self.buyer_reward
        }

        if self.arrived_to_forward:
            result['arrived_to_forwarder'] = self.arrived_to_forward.strftime("%Y-%m-%d %H:%M")
        else:
            result['arrived_to_forwarder'] = self.arrived_to_forward
        if self.got_track:
            result['send_to_host_country'] = self.got_track.strftime("%Y-%m-%d %H:%M")
        else:
            result['send_to_host_country'] = self.got_track
        if self.arrived_to_host_country:
            result['arrived_to_host_country'] = self.arrived_to_host_country.strftime("%Y-%m-%d %H:%M")
        else:
            result['arrived_to_host_country'] = self.arrived_to_host_country
        if self.received_in_host_country:
            result['received_in_host_country'] = self.received_in_host_country.strftime("%Y-%m-%d %H:%M")
        else:
            result['received_in_host_country'] = self.received_in_host_country
        if self.send_to_ru:
            result['send_to_ru'] = self.send_to_ru.strftime("%Y-%m-%d %H:%M")
        else:
            result['send_to_ru'] = self.send_to_ru
        if self.success:
            result['received_by_client'] = self.success.strftime("%Y-%m-%d %H:%M")
        else:
            result['received_by_client'] = self.success
        return result


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    client = models.ForeignKey('User', on_delete=models.CASCADE)
    web_user = models.ForeignKey('WebUser', on_delete=models.CASCADE)
    user_ip = models.CharField(max_length=255)
    buyer = models.BigIntegerField()
    time = models.DateTimeField(default=timezone.now)
    type = models.CharField(max_length=255)
    body = models.TextField()
    status = models.CharField(max_length=255)

    def __repr__(self):
        return f'{self.id} | telegram user {self.client}| web user {self.web_user} | anonimus web user {self.time} | {self.type}'

    def to_dict(self):
        order = {"id": self.id}
        if self.client:
            order["telegram_user"] = self.client
        if self.web_user:
            order["web_user"] = self.web_user
        if self.user_ip:
            order["anonim_user"] = self.user_ip
        if self.time:
            order["time"] = self.time.strftime("%Y-%m-%d %H:%M")
        order["body"] = self.body
        order["order_type"] = self.type
        order["status"] = self.status
        return order


class UserData(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=250)


class Discount(models.Model):
    id = models.AutoField(primary_key=True)
    is_vip = models.BooleanField()
    user_id = models.ForeignKey('User', on_delete=models.CASCADE, unique=True)


class Photo(models.Model):
    photo_id = models.AutoField(primary_key=True)
    file_id = models.TextField()
    message_id = models.ForeignKey('Message', on_delete=models.CASCADE)


class Document(models.Model):
    id = models.AutoField(primary_key=True)
    document_id = models.TextField()
    message_id = models.ForeignKey('Message', on_delete=models.CASCADE)


class Manager(models.Model):
    id = models.AutoField(primary_key=True)
    short_name = models.CharField(max_length=255, unique=True)
    user_id = models.ForeignKey('User', on_delete=models.CASCADE)
    key = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField()


class Exchange(models.Model):
    valuta = models.CharField(max_length=255, primary_key=True)
    price = models.FloatField(null=True, blank=True)
    data = models.CharField(max_length=255, null=True, blank=True)


class Services(models.Model):
    service_name = models.CharField(max_length=255, primary_key=True)
    status = models.BooleanField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    report = models.CharField(max_length=255, null=True, blank=True)


class Buyers(models.Model):
    id = models.AutoField(primary_key=True)
    phone = models.BigIntegerField(null=True, blank=True)
    telegram_id = models.BigIntegerField(null=True, blank=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    second_name = models.CharField(max_length=50, null=True, blank=True)
    comments = models.TextField(null=True, blank=True)


class FastAnswers(models.Model):
    id = models.AutoField(primary_key=True)
    body = models.TextField(null=True, blank=True)
    button_name = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=255, null=True, blank=True)
    manager = models.ForeignKey('Manager', on_delete=models.CASCADE, null=True, blank=True)


class UserMain(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    second_name = models.CharField(max_length=50, null=True, blank=True)
    third_name = models.CharField(max_length=50, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)


class EmailTaskStatus:
    AWAIT = "await"
    EXECUTED = "executed"
    CANCELED = "canceled"


class EmailTask(models.Model):
    id = models.AutoField(primary_key=True)
    web_user = models.ForeignKey('WebUser', on_delete=models.CASCADE)
    text = models.TextField()
    header = models.CharField(max_length=255)
    execute_time = models.DateTimeField()
    status = models.CharField(max_length=255)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(status__in=['await', 'executed', 'canceled']), name='check_status')
        ]



