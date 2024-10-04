import datetime
from enum import Enum
from typing import List
from pydantic import BaseModel, Field


class Event(str, Enum):
    message = 'message'
    new_token = 'new_token'
    ask_username = 'ask_username'
    download_history = 'download_history'
    readMessage = 'readMessage'


class EventWordPress(str, Enum):
    create_order = "create_order"
    create_user = "create_user"
    load_orders = "load_orders"


class MessageType(str, Enum):
    text = 'text'
    photo = 'photo'
    document = 'document'
    order = 'order'
    fastDocument = 'fastDocument'
    fastPhoto = 'fastPhoto'


class MessageDetails(BaseModel):
    message_id: int | None
    is_answer: bool
    user_id: int | None
    message_type: MessageType
    text: str | None = None
    mimi_type: str = None
    file: str = None
    time: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())
    user_name: str = None
    is_read: bool = Field(default=False)


class HistoryDetails(MessageDetails):
    pass


class NewTokenDetails(BaseModel):
    pass


class AskUserNameDetails(BaseModel):
    pass


class HistoryLoad(BaseModel):
    event: Event
    data: List[HistoryDetails]


class MessageLoad(BaseModel):
    """use this model to send and get ws.onmessage with Event message"""
    event: Event
    name: str | None
    details: MessageDetails


class EventSupport(str, Enum):
    UnreadMessageCount = "UnreadMessageCount"


class SupportDetails(BaseModel):
    count: int


class SupportLoad(BaseModel):
    event: EventSupport
    userID: int
    userName: str = None
    details: SupportDetails
