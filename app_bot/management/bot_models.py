import datetime
from enum import Enum
from pydantic import BaseModel, Field


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
