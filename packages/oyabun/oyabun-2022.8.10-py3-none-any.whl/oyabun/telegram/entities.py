from datetime import datetime
from typing import Optional
from typing import Type
from typing import Union

from pydantic import Field

from oyabun.telegram.base import TelegramBotApiType


class User(TelegramBotApiType):
    """
    This object represents a Telegram user or bot.

    https://core.telegram.org/bots/api#user
    """

    id: int = Field(...)  # noqa: A003, VNE003
    is_bot: bool = Field(...)
    first_name: str = Field(...)
    last_name: Optional[str] = Field(None)
    username: Optional[str] = Field(None)


class Chat(TelegramBotApiType):
    """
    This object represents a chat.

    https://core.telegram.org/bots/api#chat
    """

    id: int = Field(...)  # noqa: A003, VNE003
    title: Optional[str] = Field(None)
    username: Optional[str] = Field(None)


class MessageEntity(TelegramBotApiType):
    """
    This object represents one special entity in a text message.

    For example, hashtags, usernames, URLs, etc.

    https://core.telegram.org/bots/api#messageentity
    """

    type: str = Field(...)  # noqa: A003, VNE003
    offset: int = Field(...)
    length: int = Field(...)
    url: Optional[str] = Field(None)
    user: Optional[User] = Field(None)
    language: Optional[str] = Field(None)


class PhotoSize(TelegramBotApiType):
    """
    This object represents one size of a photo or a file / sticker thumbnail.

    https://core.telegram.org/bots/api#photosize
    """

    file_id: str = Field(...)
    file_unique_id: str = Field(...)
    width: int = Field(...)
    height: int = Field(...)
    file_size: Optional[int] = Field(None)


class Message(TelegramBotApiType):
    """
    This object represents a message.

    https://core.telegram.org/bots/api#message
    """

    message_id: int = Field(...)
    from_: Optional[User] = Field(None)
    date: datetime = Field(...)
    chat: Chat = Field(...)
    edit_date: Optional[datetime] = Field(None)
    reply_to_message: Optional["Message"] = Field(None)
    text: Optional[str] = Field(None)
    entities: Optional[list[MessageEntity]] = Field(None)
    photo: Optional[list[PhotoSize]] = Field(None)
    caption: Optional[str] = Field(None)
    reply_markup: Optional["InlineKeyboardMarkup"] = Field(None)

    class Config:
        fields = {
            "from_": "from",
        }


class Update(TelegramBotApiType):
    """
    This object represents an incoming update.

    At most one of the optional parameters
    can be present in any given update.

    https://core.telegram.org/bots/api#update
    """

    update_id: int = Field(...)
    message: Optional[Message] = Field(None)
    edited_message: Optional[Message] = Field(None)
    channel_post: Optional[Message] = Field(None)
    edited_channel_post: Optional[Message] = Field(None)


class WebhookInfo(TelegramBotApiType):
    """
    Contains information about the current status of a webhook.

    https://core.telegram.org/bots/api#webhookinfo
    """

    url: str = Field(...)
    has_custom_certificate: bool = Field(...)
    pending_update_count: int = Field(0)
    ip_address: Optional[str] = Field(None)
    last_error_date: Optional[datetime] = Field(None)
    last_error_message: Optional[str] = Field(None)
    max_connections: Optional[int] = Field(None)
    allowed_updates: Optional[list[str]] = Field(None)


class InlineKeyboardButton(TelegramBotApiType):
    """
    This object represents one button of an inline keyboard.

    You MUST use exactly one of the optional fields.

    https://core.telegram.org/bots/api#inlinekeyboardbutton
    """

    text: str = Field(...)
    url: Optional[str] = Field(None)
    callback_data: Optional[str] = Field(None, min_length=1, max_length=64)


class InlineKeyboardMarkup(TelegramBotApiType):
    """
    This object represents an inline keyboard
    that appears right next to the message it belongs to.

    https://core.telegram.org/bots/api#inlinekeyboardmarkup
    """

    inline_keyboard: list[list[InlineKeyboardButton]] = Field(
        default_factory=list,
    )


class KeyboardButton(TelegramBotApiType):
    """
    This object represents one button of the reply keyboard.

    For simple text buttons String can be used
    instead of this object to specify text of the button.

    Optional fields request_contact, request_location,
    and request_poll are mutually exclusive.

    https://core.telegram.org/bots/api#keyboardbutton
    """

    text: str = Field(...)


class ReplyKeyboardMarkup(TelegramBotApiType):
    """
    This object represents a custom keyboard with reply options
    (see Introduction to bots for details and examples).

    https://core.telegram.org/bots#keyboards
    https://core.telegram.org/bots/api#replykeyboardmarkup
    """

    keyboard: list[list[KeyboardButton]] = Field(default_factory=list)
    resize_keyboard: bool = Field(False)
    one_time_keyboard: bool = Field(False)


class ReplyKeyboardRemove(TelegramBotApiType):
    """
    Upon receiving a message with this object,
    Telegram clients will remove the current custom keyboard
    and display the default letter-keyboard.

    By default, custom keyboards are displayed
    until a new keyboard is sent by a bot.

    An exception is made for one-time keyboards
    that are hidden immediately
    after the user presses a button (see ReplyKeyboardMarkup).

    https://core.telegram.org/bots/api#replykeyboardremove
    """

    remove_keyboard: bool = Field(True)


class ForceReply(TelegramBotApiType):
    """
    Upon receiving a message with this object,
    Telegram clients will display a reply interface to the user
    (act as if the user has selected the bot's message and tapped 'Reply').

    This can be extremely useful
    if you want to create user-friendly step-by-step interfaces
    without having to sacrifice privacy mode.

    Example: A poll bot for groups runs in privacy mode
    (only receives commands, replies to its messages and mentions).

    There could be two ways to create a new poll:

    -   Explain the user how to send a command with parameters
        (e.g. /newpoll question answer1 answer2).

        May be appealing for hardcore users but lacks modern day polish.

    -   Guide the user through a step-by-step process.
        'Please send me your question',
        'Cool, now let's add the first answer option',
        'Great. Keep adding answer options,
         then send /done when you're ready'.

        The last option is definitely more attractive.

        And if you use ForceReply in your bot's questions,
        it will receive the user's answers
        even if it only receives replies, commands and mentions —
        without any extra work for the user.

    https://core.telegram.org/bots/api#forcereply
    """

    force_reply: bool = Field(True)


class File(TelegramBotApiType):
    file_id: str = Field(...)
    file_unique_id: str = Field(...)
    file_size: Optional[int] = Field(None)
    file_path: Optional[str] = Field(None)


class BotCommand(TelegramBotApiType):
    command: str = Field(..., min_length=1, max_length=32)
    description: str = Field(..., min_length=3, max_length=256)


class BotCommandScope(TelegramBotApiType):
    type: str = Field(...)  # noqa: A003,VNE003


class BotCommandScopeDefault(BotCommandScope):
    type: str = "default"  # noqa: A003,VNE003


ReplyMarkupType = Union[
    ForceReply,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
]

__models__: set[Type[TelegramBotApiType]] = {
    BotCommand,
    BotCommandScope,
    BotCommandScopeDefault,
    Chat,
    File,
    ForceReply,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    MessageEntity,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    User,
    WebhookInfo,
}

__all__ = (
    "__models__",
    "BotCommand",
    "BotCommandScope",
    "BotCommandScopeDefault",
    "Chat",
    "File",
    "ForceReply",
    "InlineKeyboardButton",
    "InlineKeyboardMarkup",
    "KeyboardButton",
    "Message",
    "MessageEntity",
    "ReplyKeyboardMarkup",
    "ReplyKeyboardRemove",
    "ReplyMarkupType",
    "Update",
    "User",
    "WebhookInfo",
)
