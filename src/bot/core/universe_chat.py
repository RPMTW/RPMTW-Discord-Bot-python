from asyncio import Future, get_event_loop
from dataclasses import asdict, dataclass
from json import dumps, loads
from logging import INFO, getLogger
from re import compile
from typing import TYPE_CHECKING

from aiohttp import ClientSession
from bidict import bidict
from discord import DiscordException, Member, Message, TextChannel
from exceptions import ChannelTypeError
from socketio import AsyncClient

if TYPE_CHECKING:
    from core.bot import RPMTWBot

_EMOJI_TO_DISCORD = compile(r":([a-zA-Z0-9_]+):")
_EMOJI_TO_MINECRAFT = compile(r"<:([a-zA-Z0-9_]+):([0-9]+)>")
_EMOJI_DATA: dict[str, int] = {}
_ID_UUID: bidict[int, str] = bidict()
_LOGGER = getLogger(__name__)
_LOGGER.setLevel(INFO)


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

    def is_from_discord(self):
        return self.userType == "discord"

    async def get_reply(self, api_base_url: str):
        if not (reply_uuid := self.replyMessageUUID):
            return None
        link = f"{api_base_url}/universe-chat/view/{reply_uuid}"

        async with ClientSession() as session:
            async with session.get(link) as response:
                response_data: dict = await response.json()
                return self.__class__(**response_data["data"])

    def get_name(self):
        if nickname := self.nickname:
            return f"{self.username} ({nickname})".replace("_", "\\_")
        return self.username.replace("_", "\\_")

    @classmethod
    def from_raw(cls, raw_data: list[int]):
        data = loads(
            "".join(chr(_) for _ in raw_data).encode("raw_unicode_escape").decode()
        )
        return cls(**data)


@dataclass
class DiscordMessage:
    message: str
    username: str
    userId: str
    avatarUrl: str | None = None
    nickname: str | None = None
    replyMessageUUID: str | None = None

    def encode(self):
        return [
            ord(_)
            for _ in dumps(asdict(self), separators=(",", ":"), ensure_ascii=False)
            .encode()
            .decode("raw_unicode_escape")
        ]

    @classmethod
    def from_message(cls, message: Message):
        content = _format_emoji_to_minecraft(message.content)

        if attachments := message.attachments:
            content += "".join(f"\n{attachment.url}" for attachment in attachments)

        reply = _.resolved if (_ := message.reference) else None
        author: Member = message.author  # type: ignore
        return cls(
            content,
            author.name,
            str(author.id),
            author.display_avatar.url,
            author.nick,
            _ID_UUID.get(reply.id) if reply else None,
        )


def _format_emoji_to_minecraft(message: str):
    for _ in _EMOJI_TO_MINECRAFT.finditer(message):
        message = message.replace(_.group(0), f":{_.group(1)}:")

    return message


def _format_emoji_to_discord(message: str):
    for _ in _EMOJI_TO_DISCORD.finditer(message):
        message = message.replace(
            _.group(0), f"<:{_.group(1)}:{_EMOJI_DATA[_.group(1)]}>"
        )

    return message


class RPMTWApiClient:
    def __init__(self, bot: "RPMTWBot", config: dict):
        self._bot = bot
        self._config = config
        self._sio = AsyncClient(binary=True)
        self._loop = get_event_loop()
        self._api_base_url: str = config["api_base_url"]

        self._sio.on("connect", self._handle_connect)
        self._sio.on("disconnect", self._handle_disconnect)
        self._sio.on("connect_error", self._handle_connect_error)
        self._sio.on("sentMessage", self._handle_sentMessage)
        self._loop.create_task(self.init())

    async def init(self):
        await self._bot.wait_until_ready()

        if not (
            channel := self._bot.get_channel(channel_id := self._config["channel_id"])
        ):
            raise ValueError("Channel id invalid")
        if not isinstance(channel, TextChannel):
            raise ChannelTypeError(self._config["channel_id"], "TextChannel")

        webhooks = await channel.webhooks()

        try:
            webhook = webhooks[0]
        except IndexError as e:
            raise ValueError(f"Channel with id `{channel_id}` has no webhook(s)") from e

        if not (guild := self._bot.get_guild(self._config["guild_id"])):
            raise ValueError("Guild id invalid")

        self._channel = channel
        self._webhook = webhook
        _EMOJI_DATA.update({emoji.name: emoji.id for emoji in guild.emojis})

    async def connect(self, token: str | None = None):
        await self._sio.connect(
            self._config["universe_chat_base_url"],
            transports="websocket",
            headers={"rpmtw_auth_token": token} if token else {},
        )

    async def disconnect(self):
        await self._sio.disconnect()

    async def send_discord_message(self, message: Message):
        """Send a discord message to Universe Chat"""
        future: Future[str] = self._loop.create_future()
        await self._sio.emit(
            "discordMessage",
            DiscordMessage.from_message(message).encode(),
            callback=lambda uuid: future.set_result(uuid),
        )
        _ID_UUID[message.id] = await future

    async def _handle_sentMessage(self, raw_data: list[int]):
        if (message := ReceivedMessage.from_raw(raw_data)).is_from_discord():
            return

        try:
            webhook_message = await self._webhook.send(
                await self._get_content(message),
                avatar_url=message.avatarUrl,
                username=message.get_name(),
                wait=True,
            )
        except DiscordException as e:
            _LOGGER.error(f"Send cosmic chat message to discord failed: {e}")
        else:
            _ID_UUID[webhook_message.id] = message.uuid

    def _handle_connect(self):
        _LOGGER.info("Connected to Universe Chat server")

    def _handle_disconnect(self):
        _LOGGER.info("Disconnected from Universe Chat server")

    def _handle_connect_error(self, data):
        _LOGGER.error(f"Connection error: {data}")

    async def _get_content(self, message: ReceivedMessage):
        content = _format_emoji_to_discord(message.message)

        if not (reply := await message.get_reply(self._api_base_url)):
            return content

        content = f"：{reply.message}\n-> {content}"

        if not (reply_id := _ID_UUID.inverse.get(reply.uuid)):
            return f"回覆 {reply.get_name()}{content}"

        discord_message = await self._channel.fetch_message(reply_id)
        content = f"（<{discord_message.jump_url}>）{content}"

        if reply.is_from_discord():
            return f"回覆 {discord_message.author.mention}{content}"
        return f"回覆 {reply.get_name()}{content}"
