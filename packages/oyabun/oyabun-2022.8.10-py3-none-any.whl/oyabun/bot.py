from io import BytesIO
from pathlib import Path
from typing import IO
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import Union

from httpx import AsyncClient
from httpx import Response as HttpResponse

from oyabun.telegram import DeleteWebhookResponse
from oyabun.telegram import File
from oyabun.telegram import GetFileRequest
from oyabun.telegram import GetFileResponse
from oyabun.telegram import GetMeResponse
from oyabun.telegram import GetWebhookInfoResponse
from oyabun.telegram import Message
from oyabun.telegram import MessageEntity
from oyabun.telegram import SendMessageRequest
from oyabun.telegram import SendMessageResponse
from oyabun.telegram import SendPhotoRequest
from oyabun.telegram import SendPhotoResponse
from oyabun.telegram import SetWebhookRequest
from oyabun.telegram import SetWebhookResponse
from oyabun.telegram import User
from oyabun.telegram import WebhookInfo
from oyabun.telegram.base import Request
from oyabun.telegram.base import Response
from oyabun.telegram.entities import ReplyMarkupType


class Bot:
    """
    The class represents an entrypoint to communicate with Telegram Bot API.

    The methods are synchronized with those from official API doc.

    Usage: instantiate using bot token and go.

    If something is wrong, you'll get the `Bot.RequestError` exception raised.
    """

    TELEGRAM_BOT_API_URL = "https://api.telegram.org"

    class RequestError(RuntimeError):
        """
        A base exception for any internal error, including those
        caused by malformed requests and invalid data.
        """

        pass

    def __init__(self, token: str):
        """
        Sets up the new Bot instance.

        :param token: a bot token which BotFather gives to you.
        """

        self.__token = token

    @property
    def api_url(self) -> str:
        """
        An API URL to make requests to.

        :return: the completed API URL as a string
        """

        return f"{self.TELEGRAM_BOT_API_URL}/bot{self.__token}"

    @property
    def file_url(self) -> str:
        """
        A URL to download files from.

        :return: the completed URL as a string
        """

        return f"{self.TELEGRAM_BOT_API_URL}/file/bot{self.__token}"

    async def downloadFile(self, file: File) -> BytesIO:
        """
        Downloads the file's content into the BytesIO object.

        https://core.telegram.org/bots/api#getfile
        https://core.telegram.org/bots/api#file

        :param file: a File object

        :return: a BytesIO object with content of the file
        """

        if not file.file_path:
            raise self.RequestError(f"file {file} has no file_path set")

        return await self._download_file(file.file_path)

    async def getFile(self, file_id: str) -> File:
        """
        Use this method to get basic info about a file
        and prepare it for downloading.

        For the moment, bots can download files of up to 20MB in size.

        The file can then be downloaded
        via the link https://api.telegram.org/file/bot<token>/<file_path>,
        where <file_path> is taken from the response.

        It is guaranteed that the link will be valid for at least 1 hour.

        When the link expires,
        a new one can be requested by calling getFile again.

        https://core.telegram.org/bots/api#getfile

        :return: on success, a File object
        """

        request = GetFileRequest(file_id=file_id)

        return await self._call_api(
            "getFile",
            request,
            response_cls=GetFileResponse,
        )

    async def getMe(self) -> User:
        """
        A simple method for testing your bot's auth token.

        https://core.telegram.org/bots/api#getme

        :return: basic information about the bot in form of a User object
        """

        return await self._call_api(
            "getMe",
            response_cls=GetMeResponse,
        )

    async def getWebhookInfo(self) -> WebhookInfo:
        return await self._call_api(
            "getWebhookInfo",
            response_cls=GetWebhookInfoResponse,
        )

    async def deleteWebhook(self) -> bool:
        return await self._call_api(
            "deleteWebhook",
            response_cls=DeleteWebhookResponse,
        )

    async def setWebhook(self, *, url: str) -> bool:
        request = SetWebhookRequest(
            url=url,
        )

        return await self._call_api(
            "setWebhook",
            request,
            response_cls=SetWebhookResponse,
        )

    async def sendMessage(
        self,
        *,
        chat_id: Union[int, str],
        text: str,
        parse_mode: Optional[str] = None,
        entities: Optional[list[MessageEntity]] = None,
        disable_web_page_preview: Optional[bool] = None,
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: Optional[bool] = None,
        reply_markup: Optional[ReplyMarkupType] = None,
    ) -> Message:
        """
        Use this method to send text messages.

        https://core.telegram.org/bots/api#sendmessage

        :param chat_id: Unique identifier for the target chat
        or username of the target channel
        (in the format @channelusername).

        :param text: Text of the message to be sent,
        1-4096 characters after entities parsing.

        :param parse_mode: Mode for parsing entities in the message text.
        See formatting options for more details.

        :param entities: A JSON-serialized list of special entities
        that appear in message text,
        which can be specified instead of parse_mode.

        :param disable_web_page_preview: Disables link previews
        for links in this message.

        :param disable_notification: Sends the message silently.
        Users will receive a notification with no sound.

        :param reply_to_message_id: If the message is a reply,
        ID of the original message.

        :param allow_sending_without_reply: Pass True,
        if the message should be sent
        even if the specified replied-to message is not found.

        :param reply_markup: Additional interface options.
        A JSON-serialized object for an inline keyboard,
        custom reply keyboard,
        instructions to remove reply keyboard
        or to force a reply from the user.

        :return: on success, the sent Message.
        """

        request = SendMessageRequest(
            allow_sending_without_reply=allow_sending_without_reply,
            chat_id=chat_id,
            disable_notification=disable_notification,
            disable_web_page_preview=disable_web_page_preview,
            entities=entities,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            reply_to_message_id=reply_to_message_id,
            text=text,
        )

        return await self._call_api(
            "sendMessage",
            request,
            response_cls=SendMessageResponse,
        )

    async def sendPhoto(
        self,
        *,
        chat_id: Union[int, str],
        photo: Union[str, Path, IO],
        caption: Optional[str] = None,  # 0-1024
        parse_mode: Optional[str] = None,
        caption_entities: Optional[list[MessageEntity]] = None,
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: Optional[bool] = None,
        reply_markup: Optional[ReplyMarkupType] = None,
    ) -> Message:
        """
        Use this method to send photos.

        https://core.telegram.org/bots/api#sendphoto

        :param chat_id: Unique identifier for the target chat
        or username of the target channel
        (in the format @channelusername).

        :param photo: Photo to send.
        Pass a file_id as String to send a photo
        that exists on the Telegram servers (recommended),
        pass an HTTP URL as a String for Telegram
        to get a photo from the Internet,
        or upload a new photo using multipart/form-data.

        The photo must be at most 10 MB in size.
        The photo's width and height must not exceed 10000 in total.
        Width and height ratio must be at most 20.

        :param caption: Photo caption
        (may also be used when resending photos by file_id),
        0-1024 characters after entities parsing.

        :param parse_mode: Mode for parsing entities in the message text.
        See formatting options for more details.

        :param caption_entities: A JSON-serialized list of special entities
        that appear in the caption,
        which can be specified instead of parse_mode.

        :param disable_notification: Sends the message silently.
        Users will receive a notification with no sound.

        :param reply_to_message_id: If the message is a reply,
        ID of the original message.

        :param allow_sending_without_reply: Pass True,
        if the message should be sent
        even if the specified replied-to message is not found.

        :param reply_markup: Additional interface options.
        A JSON-serialized object for an inline keyboard,
        custom reply keyboard,
        instructions to remove reply keyboard
        or to force a reply from the user.

        :return: on success, the sent Message.
        """

        request = SendPhotoRequest(
            allow_sending_without_reply=allow_sending_without_reply,
            caption=caption,
            caption_entities=caption_entities,
            chat_id=chat_id,
            disable_notification=disable_notification,
            parse_mode=parse_mode,
            photo=photo,
            reply_markup=reply_markup,
            reply_to_message_id=reply_to_message_id,
        )

        return await self._call_api(
            "sendPhoto", request, response_cls=SendPhotoResponse
        )

    _T = TypeVar(
        "_T"
    )  # don't worry about this: used as a generic type var in `_call_api`

    async def _call_api(  # noqa: CCR001
        self,
        method: str,
        request: Optional[Request] = None,
        *,
        response_cls: Type[Response[_T]] = Response[_T],
    ) -> _T:
        """
        Performs the call to the Bot API returning a value of proper type.
        In case of error raises `Bot.RequestError`.

        https://core.telegram.org/bots/api#making-requests

        :param method: name of the supported Telegram Bot API method

        :param request: request object,
        composed from input params of public method

        :param response_cls: desired response class with actual result type

        :return: object of response class' result type
        """

        try:
            url = f"{self.api_url}/{method}"

            request = (
                request or Request()
            )  # for methods which do not need request at all

            client: AsyncClient
            async with AsyncClient() as client:
                with request.files() as files:
                    # if files, data must be of multipart/form-data
                    # otherwise JSON bytes with Content-Type=application/json
                    data = request.dict() if files else request.json()
                    headers = (
                        {} if files else {"Content-Type": "application/json"}
                    )
                    http_response: HttpResponse = await client.post(
                        url,
                        # mypy can't into X if P else Y
                        data=data,  # type: ignore
                        files=files,
                        headers=headers,
                    )

            if http_response.status_code != 200:
                raise self.RequestError(http_response.content)

            payload = http_response.json()
            if not payload:
                raise self.RequestError(
                    f"unexpected empty payload on /{method}"
                )

            # actual&valid Telegram response
            response = response_cls.parse_obj(payload)

            if not response.ok:
                raise self.RequestError(response.description)

            if response.result is None:
                raise self.RequestError(
                    f"unexpected null result on /{method} -> {response}"
                )

            return response.result

        except Exception as err:
            raise self.RequestError(err) from err

    async def _download_file(
        self,
        file_path: str,
    ) -> BytesIO:
        """
        Downloads a file using file path from API.

        https://core.telegram.org/bots/api#getfile
        https://core.telegram.org/bots/api#file

        :param file_path: File path.
        Use https://api.telegram.org/file/bot<token>/<file_path>
        to get the file.

        :return: a BytesIO object with file content.
        """

        try:
            url = f"{self.file_url}/{file_path}"

            client: AsyncClient
            async with AsyncClient() as client:
                http_response: HttpResponse = await client.get(url)

            if http_response.status_code != 200:
                raise self.RequestError(http_response.content)

            buffer = BytesIO()
            buffer.write(http_response.content)
            buffer.seek(0)

            return buffer

        except Exception as err:
            raise self.RequestError(err) from err
