from asyncio import Future, get_event_loop
from dataclasses import asdict, dataclass
from enum import StrEnum, auto
from json import dumps, loads
from re import compile
from typing import TYPE_CHECKING, Self

from aiohttp import ClientSession
from bidict import bidict
from disnake import DiscordException, Member, Message, TextChannel
from socketio import AsyncClient

if TYPE_CHECKING:
    from logging import Logger

    from extension.universe_chat import Config

_EMOJI_TO_DISCORD = compile(r":([a-zA-Z0-9_]+):")
_EMOJI_TO_MINECRAFT = compile(r"<:([a-zA-Z0-9_]+):([0-9]+)>")
_EMOJI_DATA: dict[str, int] = {}
_ID_UUID: bidict[int, str] = bidict()


class Event(StrEnum):
    connect = auto()
    disconnect = auto()
    connect_error = auto()
    sentMessage = auto()


@dataclass
class ReceivedMessage:
    uuid: str
    username: str
    userIdentifier: str
    message: str
    nickname: str
    avatarUrl: str
    sentAt: str
    userType: str
    replyMessageUUID: str

    @property
    def content(self) -> str:
        """Alias of `self.message`"""
        return self.message

    def is_from_discord(self) -> bool:
        return self.userType == "discord"

    async def get_reply(self, api_base_url: str) -> "Self | None":
        if (reply_uuid := self.replyMessageUUID) == "":
            return None

        link = f"{api_base_url}/universe-chat/view/{reply_uuid}"

        async with ClientSession() as session:
            async with session.get(link) as response:
                response_data: dict = await response.json()
                return self.__class__(**response_data["data"])

    def get_name(self) -> str:
        if nickname := self.nickname:
            return f"{self.username} ({nickname})"
        return self.username

    def get_name_escaped(self) -> str:
        return self.get_name().replace("_", "\\_")

    @classmethod
    def from_raw(cls, raw_data: list[int]) -> "Self":
        data: dict[str, str] = loads("".join(chr(_) for _ in raw_data).encode("raw_unicode_escape").decode())
        return cls(**data)


@dataclass
class DiscordMessage:
    message: str
    username: str
    userId: str
    avatarUrl: str | None = None
    nickname: str | None = None
    replyMessageUUID: str | None = None

    def encode(self) -> list[int]:
        return [
            ord(_)
            for _ in dumps(asdict(self), separators=(",", ":"), ensure_ascii=False)
            .encode()
            .decode("raw_unicode_escape")
        ]

    @classmethod
    def from_discord(cls, message: Message) -> "Self":
        content = _format_emoji_to_minecraft(message.content)

        if attachments := message.attachments:
            content += "".join(f"\n{attachment.url}" for attachment in attachments)

        reply = _.resolved if (_ := message.reference) else None
        assert isinstance(author := message.author, Member)
        return cls(
            content,
            author.name,
            str(author.id),
            author.display_avatar.url,
            author.nick,
            _ID_UUID.get(reply.id) if reply else None,
        )


def _format_emoji_to_minecraft(message: str) -> str:
    for _ in _EMOJI_TO_MINECRAFT.finditer(message):
        message = message.replace(_.group(0), f":{_.group(1)}:")

    return message


def _format_emoji_to_discord(message: str) -> str:
    for _ in _EMOJI_TO_DISCORD.finditer(message):
        message = message.replace(_.group(0), f"<:{_.group(1)}:{_EMOJI_DATA[_.group(1)]}>")

    return message


class APIClient:
    def __init__(self, config: "Config", logger: "Logger") -> None:
        self._config = config
        self._logger = logger
        self._sio = AsyncClient(binary=True)
        self._loop = get_event_loop()

        self._sio.on(Event.connect.value, self._handle_connect)
        self._sio.on(Event.disconnect.value, self._handle_disconnect)
        self._sio.on(Event.connect_error.value, self._handle_connect_error)
        self._sio.on(Event.sentMessage.value, self._handle_sentMessage)
        self._inited = False

    async def init(self, channel: TextChannel) -> "Self | None":
        self._logger.info("Start initialization.")
        webhooks = await channel.webhooks()

        try:
            # TODO: let user specify use which webhook
            webhook = webhooks[0]
        except IndexError as e:
            self._logger.exception("Channel has no webhook(s)", exc_info=e)
            raise e

        self._channel = channel
        self._webhook = webhook
        self._logger.info("Update emoji data")
        _EMOJI_DATA.update({emoji.name: emoji.id for emoji in channel.guild.emojis})
        self._inited = True
        self._logger.info("Finish initialization.")
        return self

    async def connect(self, token: str | None = None) -> None:
        self._logger.info("Connecting to Universe chat server...")
        await self._sio.connect(
            self._config.universe_chat_base_url,
            transports="websocket",
            headers={"rpmtw_auth_token": token} if token else {},
        )

    async def disconnect(self) -> None:
        await self._sio.disconnect()

    async def send_discord_message(self, message: Message) -> None:
        """Send a discord message to Universe Chat"""
        future: Future[str] = self._loop.create_future()
        await self._sio.emit(
            "discordMessage",
            DiscordMessage.from_discord(message).encode(),
            callback=lambda uuid: future.set_result(uuid),
        )
        _ID_UUID[message.id] = await future

    def _raise_not_inited(self):
        message = "APIClient not inited"
        self._logger.error(message)
        raise RuntimeError(message)

    async def _sync_message_to_discord(self, message: ReceivedMessage) -> None:
        if not self._inited:
            self._raise_not_inited()

        try:
            webhook_message = await self._webhook.send(
                await self._get_content(message),
                avatar_url=message.avatarUrl,
                username=message.get_name(),
                wait=True,
            )
        except DiscordException as e:
            self._logger.exception("Send cosmic chat message to discord failed", exc_info=e)
        else:
            _ID_UUID[webhook_message.id] = message.uuid

    async def _handle_sentMessage(self, raw_data: list[int]) -> None:
        if not (message := ReceivedMessage.from_raw(raw_data)).is_from_discord():
            await self._sync_message_to_discord(message)

    def _handle_connect(self) -> None:
        self._logger.info("Connected to Universe Chat server")

    def _handle_disconnect(self) -> None:
        self._logger.info("Disconnected from Universe Chat server")

    def _handle_connect_error(self, data) -> None:
        self._logger.error(f"Connection error: {data}")

    async def _get_content(self, message: ReceivedMessage) -> str:
        content = _format_emoji_to_discord(message.content)

        if not (reply := await message.get_reply(self._config.universe_chat_api_base_url)):
            return content

        content = f"：{reply.message}\n-> {content}"

        if not (reply_id := _ID_UUID.inverse.get(reply.uuid)):
            return f"回覆 {reply.get_name_escaped()}{content}"
        if not self._inited:
            self._raise_not_inited()

        discord_message = await self._channel.fetch_message(reply_id)
        content = f"（ {discord_message.jump_url} ）{content}"

        if reply.is_from_discord():
            return f"回覆 {discord_message.author.mention}{content}"
        return f"回覆 {reply.get_name_escaped()}{content}"
