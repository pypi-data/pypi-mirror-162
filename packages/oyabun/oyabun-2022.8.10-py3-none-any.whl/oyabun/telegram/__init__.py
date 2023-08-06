from typing import Type

from oyabun.telegram.base import __models__ as __models__base
from oyabun.telegram.base import Request
from oyabun.telegram.base import Response
from oyabun.telegram.base import ResponseParameters
from oyabun.telegram.base import TelegramBotApiType
from oyabun.telegram.entities import __models__ as __models__entities
from oyabun.telegram.entities import BotCommand
from oyabun.telegram.entities import BotCommandScope
from oyabun.telegram.entities import BotCommandScopeDefault
from oyabun.telegram.entities import Chat
from oyabun.telegram.entities import File
from oyabun.telegram.entities import ForceReply
from oyabun.telegram.entities import InlineKeyboardButton
from oyabun.telegram.entities import InlineKeyboardMarkup
from oyabun.telegram.entities import KeyboardButton
from oyabun.telegram.entities import Message
from oyabun.telegram.entities import MessageEntity
from oyabun.telegram.entities import ReplyKeyboardMarkup
from oyabun.telegram.entities import ReplyKeyboardRemove
from oyabun.telegram.entities import Update
from oyabun.telegram.entities import User
from oyabun.telegram.entities import WebhookInfo
from oyabun.telegram.requests import __models__ as __models__requests
from oyabun.telegram.requests import DeleteWebhookRequest
from oyabun.telegram.requests import GetFileRequest
from oyabun.telegram.requests import GetMeRequest
from oyabun.telegram.requests import GetWebhookInfoRequest
from oyabun.telegram.requests import SendMessageRequest
from oyabun.telegram.requests import SendPhotoRequest
from oyabun.telegram.requests import SetWebhookRequest
from oyabun.telegram.responses import __models__ as __models__responses
from oyabun.telegram.responses import DeleteWebhookResponse
from oyabun.telegram.responses import GetFileResponse
from oyabun.telegram.responses import GetMeResponse
from oyabun.telegram.responses import GetWebhookInfoResponse
from oyabun.telegram.responses import SendMessageResponse
from oyabun.telegram.responses import SendPhotoResponse
from oyabun.telegram.responses import SetWebhookResponse

__models__: set[Type[TelegramBotApiType]] = (
    __models__base
    | __models__entities  # noqa: W503
    | __models__requests  # noqa: W503
    | __models__responses  # noqa: W503
)

for _model in __models__:
    _model.update_forward_refs()

__all__ = (
    "BotCommand",
    "BotCommandScope",
    "BotCommandScopeDefault",
    "Chat",
    "DeleteWebhookRequest",
    "DeleteWebhookResponse",
    "File",
    "ForceReply",
    "GetFileRequest",
    "GetFileResponse",
    "GetMeRequest",
    "GetMeResponse",
    "GetWebhookInfoRequest",
    "GetWebhookInfoResponse",
    "InlineKeyboardButton",
    "InlineKeyboardMarkup",
    "KeyboardButton",
    "Message",
    "MessageEntity",
    "ReplyKeyboardMarkup",
    "ReplyKeyboardRemove",
    "Request",
    "Response",
    "ResponseParameters",
    "SendMessageRequest",
    "SendMessageResponse",
    "SendPhotoRequest",
    "SendPhotoResponse",
    "SetWebhookRequest",
    "SetWebhookResponse",
    "Update",
    "User",
    "WebhookInfo",
)
