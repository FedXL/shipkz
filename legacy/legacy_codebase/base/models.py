from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, BigInteger, Text, CheckConstraint, func, DateTime, \
    Float, UniqueConstraint
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Posts(Base):
    """Таблица постов (cms sistem) в каналах"""
    __tablename__ = 'posts'
    id = Column(BigInteger, primary_key=True)
    message_id = Column(BigInteger)
    chat_id = Column(BigInteger)
    name = Column(String, unique=True)

    def __repr__(self):
        return f"mess: {self.message_id} | chat: {self.chat_id} | name: {self.name}"


class ParceTask(Base):
    __tablename__ = 'parce_task'
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    login = Column(String)
    password = Column(String)
    type = Column(String)


class WebUserMetaData(Base):
    __tablename__ = 'web_users_meta'
    meta_id: int = Column(Integer, primary_key=True)
    field: str = Column(String, nullable=False)
    value: str = Column(String, nullable=True)
    web_user = Column(Integer, ForeignKey('web_users.user_id'), nullable=False)

    __table_args__ = (
        UniqueConstraint('field', 'web_user', name='uq_field_web_user'),
    )

    def to_dict(self):
        return {self.field: self.value}

    def __repr__(self):
        return f"{self.meta_id} | {self.field} | {self.value} | {self.web_user}"


class WebUserModel(BaseModel):
    user_id: int
    user_name: Optional[str] = None
    web_username: str
    is_kazakhstan: bool
    last_online: datetime
    last_message_telegramm_id: Optional[int] = None

    class Config:
        orm_mode = True


class WebUser(Base):
    __tablename__ = 'web_users'
    user_id: int = Column(Integer, primary_key=True)
    user_name: str = Column(String)
    web_username: str = Column(String, unique=True)
    is_kazakhstan: bool = Column(Boolean)
    last_online: TIMESTAMP = Column(TIMESTAMP)
    last_message_telegramm_id: int = Column(BigInteger)
    messages_relationship = relationship('WebMessage', back_populates='user_relationship')

    def to_model(self):
        return WebUserModel(
            user_id=self.user_id,
            user_name=self.user_name,
            web_username=self.web_username,
            is_kazakhstan=self.is_kazakhstan,
            last_online=self.last_online,
            last_message_telegramm_id=self.last_message_telegramm_id,
        )

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'user_name': self.user_name,
            'web_username': self.web_username,
            'is_kazakhstan': self.is_kazakhstan,
            'last_online': str(self.last_online),
            'last_message_telegramm_id': self.last_message_telegramm_id
        }
class WebMessage(Base):
    __tablename__ = 'web_messages'
    id = Column(BigInteger, primary_key=True)
    message_body = Column(String)
    is_answer = Column(Boolean)
    user = Column(Integer, ForeignKey('web_users.user_id'), nullable=False)
    time = Column(TIMESTAMP, server_default=func.now())
    message_type = Column(String)
    user_relationship = relationship("WebUser", back_populates="messages_relationship")
    is_read = Column(Boolean, default=False)

    def as_dict(self):
        result = {'message_id': self.id,
                  'text': self.message_body,
                  'is_answer': self.is_answer,
                  'user_id': self.user,
                  'time': self.time.strftime("%B %d, %H:%M"),
                  'message_type': self.message_type,
                  'is_read': self.is_read
                  }
        return result

    __table_args__ = (
        CheckConstraint(message_type.in_(['text', 'photo', 'file', 'caption', 'order', 'document']),
                        name='check_message_type'),
    )

    def __repr__(self):
        return f"{self.id} | {self.message_body} | {self.is_answer} | {self.time}"

class User(Base):
    __tablename__ = 'users'
    user_id = Column(BigInteger, primary_key=True)
    user_name = Column(String)
    message_id = Column(Integer)  # Видимо это последнее сообщение
    user_second_name = Column(String)
    tele_username = Column(String)
    main_user = Column(Integer)
    is_kazakhstan = Column(Boolean)

    def __repr__(self):
        return f"{self.user_id} | {self.user_name} | {self.user_second_name} | {self.tele_username}"

    def to_dict(self):
        data = {}
        for column in self.__table__.columns:
            data[column.name] = getattr(self, column.name)
        return data


class RootUser(Base):
    __tablename__ = 'root_users'
    id = Column(Integer, primary_key=True)
    telegram_user = Column(BigInteger, ForeignKey('users.user_id'))
    web_user = Column(Integer, ForeignKey('web_users.user_id'))





class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, autoincrement=True)
    message_body = Column(Text)
    is_answer = Column(Boolean)
    storage_id = Column(BigInteger, ForeignKey('users.user_id'))
    time = Column(TIMESTAMP, default=func.now())
    message_id = Column(BigInteger)


class WebPhoto(Base):
    __tablename__ = 'web_photos'
    id = Column(Integer, primary_key=True)
    photo_path = Column(String)
    message_id = Column(Integer, ForeignKey('web_messages.id'))


class WebDoc(Base):
    __tablename__ = 'web_docs'
    id = Column(Integer, primary_key=True)
    doc_path = Column(String)
    message_id = Column(Integer, ForeignKey('web_messages.id'))


class WebSocket(Base):
    __tablename__ = 'websockets'
    id = Column(BigInteger, primary_key=True)
    socket_id = Column(BigInteger)
    user_id = Column(BigInteger, ForeignKey('web_users.user_id'), unique=True)


class WebSocketSupport(Base):
    __tablename__ = "websockets_support"
    id = Column(BigInteger, primary_key=True)
    socket_id = Column(BigInteger)
    user_id = Column(BigInteger, ForeignKey('web_users.user_id'), unique=True)


class Jwt(Base):
    __tablename__ = 'jwt'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('web_users.user_id'), unique=True)
    jwt_hash = Column(String)


class OrderStatus(Base):
    __tablename__ = 'order_status'
    id = Column(Integer, primary_key=True)
    status = Column(Boolean)
    order_id = Column(Integer, ForeignKey('orders.id'))
    manager_id = Column(BigInteger)
    order_price = Column(String)

    def __repr__(self):
        return f'{self.order_id} | {self.order_price} | {self.status}'


class OrderStatusInfo(Base):
    __tablename__ = 'order_status_info'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id', ondelete='CASCADE'), unique=True, nullable=False)

    is_forward = Column(Boolean, nullable=False)
    paid = Column(DateTime, nullable=False)
    arrived_to_forward = Column(DateTime, nullable=True)
    got_track = Column(DateTime, nullable=True)
    arrived_to_host_country = Column(DateTime, nullable=True)
    received_in_host_country = Column(DateTime, nullable=True)
    send_to_ru = Column(DateTime, nullable=True)
    success = Column(DateTime, nullable=True)

    relative_price = Column(String, nullable=False)
    shop = Column(String, nullable=False)
    store_order_number = Column(String, nullable=False)
    trek = Column(String, nullable=True)
    cdek = Column(String, nullable=True)
    post_service = Column(String, nullable=True)
    host_country = Column(String, nullable=True)

    buyer = Column(BigInteger, nullable=True)
    buyer_reward = Column(String, nullable=True)

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


class Order(Base):
    __tablename__ = 'orders'
    id: int = Column(Integer, primary_key=True)
    client: int = Column(BigInteger, ForeignKey("users.user_id"))
    web_user: int = Column(Integer, ForeignKey("web_users.user_id"))
    user_ip: str = Column(String)
    buyer: int = Column(BigInteger)
    time = Column(TIMESTAMP, server_default=func.now())
    type: str = Column(String)
    body: str = Column(Text)
    status: str = Column(String)

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


class UserData(Base):
    __tablename__ = 'users_app'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(250), nullable=False)


class Discount(Base):
    __tablename__ = 'discounts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    is_vip = Column(Boolean)
    user_id = Column(BigInteger, ForeignKey('users.user_id'), unique=True)


class Photo(Base):
    __tablename__ = 'photos'
    photo_id = Column(Integer, primary_key=True)
    file_id = Column(Text)
    message_id = Column(Integer, ForeignKey('messages.id'))


class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    document_id = Column(Text)
    message_id = Column(BigInteger, ForeignKey('messages.id'))


class Manager(Base):
    __tablename__ = 'managers'
    id = Column(Integer, primary_key=True)
    short_name = Column(String, unique=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    key = Column(String, unique=True)
    is_active = Column(Boolean)


class Exchange(Base):
    __tablename__ = 'exchange'

    valuta = Column(String, primary_key=True, nullable=False)
    price = Column(Float, nullable=True)
    data = Column(String, nullable=True)


class Services(Base):
    __tablename__ = 'services'

    service_name = Column(String, primary_key=True, nullable=False)
    status = Column(Boolean, nullable=True)
    created_at = Column(TIMESTAMP, nullable=True)
    report = Column(String(length=255), nullable=True)


class Buyers(Base):
    __tablename__ = 'buyers'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    phone = Column(BigInteger, nullable=True)
    telegram_id = Column(BigInteger, nullable=True)
    first_name = Column(String(length=50), nullable=True)
    second_name = Column(String(length=50), nullable=True)
    comments = Column(Text, nullable=True)


class FastAnswers(Base):
    __tablename__ = 'fast_answers'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    body = Column(Text, nullable=True)
    button_name = Column(String, nullable=True)
    type = Column(String, nullable=True)
    manager = Column(BigInteger, ForeignKey('managers.user_id'), nullable=True)


class UserMain(Base):
    __tablename__ = 'user_main'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    first_name = Column(String(length=50), nullable=True)
    second_name = Column(String(length=50), nullable=True)
    third_name = Column(String(length=50), nullable=True)
    comment = Column(Text, nullable=True)


class EmailTaskStatus:
    AWAIT = "await"
    EXECUTED = "executed"
    CANCELED = "canceled"


class EmailTask(Base):
    __tablename__ = 'email_task'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    web_user = Column(BigInteger, ForeignKey('web_users.user_id'), nullable=False)
    text = Column(Text, nullable=False)
    header = Column(String, nullable=False)
    execute_time = Column(TIMESTAMP, nullable=False)
    status = Column(String, nullable=False)

    __table_args__ = (
        CheckConstraint(status.in_(['await', 'executed', 'canceled']), name='check_status'),
    )
