from typing import Any
from typing import Optional
from typing import Type
from typing import Union

from pydantic import Field

from oyabun.telegram.base import Request
from oyabun.telegram.entities import MessageEntity
from oyabun.telegram.entities import ReplyMarkupType


class GetFileRequest(Request):
    file_id: str = Field(...)


class GetMeRequest(Request):
    pass


class SendMessageRequest(Request):
    chat_id: Union[int, str] = Field(...)
    text: str = Field(...)
    parse_mode: Optional[str] = Field(None)
    entities: Optional[list[MessageEntity]] = Field(None)
    disable_web_page_preview: Optional[bool] = Field(None)
    disable_notification: Optional[bool] = Field(None)
    reply_to_message_id: Optional[int] = Field(None)
    allow_sending_without_reply: Optional[bool] = Field(None)
    reply_markup: Optional[ReplyMarkupType] = Field(None)


class SendPhotoRequest(Request):
    chat_id: Union[int, str] = Field(...)
    photo: Any = Field(...)
    caption: Optional[str] = Field(None)
    parse_mode: Optional[str] = Field(None)
    caption_entities: Optional[list[MessageEntity]] = Field(None)
    disable_notification: Optional[bool] = Field(None)
    reply_to_message_id: Optional[int] = Field(None)
    allow_sending_without_reply: Optional[bool] = Field(None)
    reply_markup: Optional[ReplyMarkupType] = Field(None)


class SetWebhookRequest(Request):
    url: str = Field(...)
    certificate: Any = Field(None)
    ip_address: Optional[str] = Field(None)
    max_connections: Optional[int] = Field(None)
    allowed_updates: Optional[list[str]] = Field(None)
    drop_pending_updates: Optional[bool] = Field(None)


class DeleteWebhookRequest(Request):
    drop_pending_updates: Optional[bool] = Field(None)


class GetWebhookInfoRequest(Request):
    pass


__models__: set[Type[Request]] = {
    DeleteWebhookRequest,
    GetFileRequest,
    GetMeRequest,
    GetWebhookInfoRequest,
    SendMessageRequest,
    SendPhotoRequest,
    SetWebhookRequest,
}

__all__ = (
    "__models__",
    "DeleteWebhookRequest",
    "GetFileRequest",
    "GetMeRequest",
    "GetWebhookInfoRequest",
    "SendMessageRequest",
    "SendPhotoRequest",
    "SetWebhookRequest",
)
