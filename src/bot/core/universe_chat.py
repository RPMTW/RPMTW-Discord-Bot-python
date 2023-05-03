from asyncio import Queue
from json import dumps, loads
from re import compile

from aiohttp import ClientSession
from bidict import bidict
from discord import DiscordException, TextChannel, Message, Webhook, WebhookMessage
from socketio import AsyncClient

from exceptions import (
    ChannelNotFoundError,
    ChannelTypeError,
    GuildNotFoundError,
    HasNoWebhookError,
)
from packages import RPMTWBot


class RPMTWApiClient:
    def __init__(self, bot: "RPMTWBot", config: dict) -> None:
        self.bot = bot
        self.config = config
        self.sio = AsyncClient()
        self.received_data: Queue[dict] = Queue()
        self.id_uuid = bidict()
        self._maybe_none = {}
        self.log = bot.log

        @self.sio.event
        def connect():
            self.log.info("Connected to Universe Chat server")

        @self.sio.event
        def disconnect():
            self.log.info("Disconnected from Universe Chat server")

        @self.sio.event
        def connect_error(data):
            self.log.error(f"Connection error: {data}")

        @self.sio.event
        async def sentMessage(data: list[int]):
            decoded_data = self.decode_data(data)

            if decoded_data["userType"] == "discord":
                return

            webhook = await self.get_webhook()

            try:
                discord_message: WebhookMessage = await webhook.send(
                    await self.get_content(decoded_data),
                    avatar_url=decoded_data["avatarUrl"],
                    username=self._format_nickname(decoded_data),
                    wait=True,
                )
                self.id_uuid[discord_message.id] = decoded_data["uuid"]
            except DiscordException as e:
                self.log.error(f"Send cosmic chat message to discord failed: {e}")

        self.api_base_url = config["api_base_url"]
        self.universe_chat_base_url = config["universe_chat_base_url"]

    def get_channel(self) -> TextChannel:
        if channel := self._maybe_none.get("channel"):
            return channel

        if not (channel := self.bot.get_channel(self.config["channel_id"])):
            raise ChannelNotFoundError(self.config["channel_id"])

        if not isinstance(channel, TextChannel):
            raise ChannelTypeError(self.config["channel_id"], "TextChannel")

        self._maybe_none["channel"] = channel
        return channel

    async def get_webhook(self) -> "Webhook":
        if webhook := self._maybe_none.get("webhook"):
            return webhook

        webhooks = await self.get_channel().webhooks()

        try:
            webhook = webhooks[0]
        except IndexError as e:
            raise HasNoWebhookError(self.config["channel_id"]) from e

        self._maybe_none["webhook"] = webhook
        return webhook

    def get_emoji_data(self) -> dict[str, str]:
        if emoji_data := self._maybe_none["emoji_data"]:
            return emoji_data

        if not (guild := self.bot.get_guild(self.config["guild_id"])):
            raise GuildNotFoundError(self.config["guild_id"])

        self._maybe_none["emoji_data"] = emoji_data = {
            emoji.name: str(emoji.id) for emoji in guild.emojis
        }
        return emoji_data

    async def get_message_data_by_uuid(self, uuid) -> dict:
        link = f"{self.api_base_url}/universe-chat/view/{uuid}"

        async with ClientSession() as session:
            async with session.get(link) as response:
                response_data = await response.json()
                return response_data["data"]

    async def get_content(self, decoded_data: dict):
        content: str = decoded_data["message"]

        if not (reply_uuid := decoded_data["replyMessageUUID"]):
            return content

        reply_message_data = await self.get_message_data_by_uuid(reply_uuid)

        if not (
            discord_message_id := self.id_uuid.inverse.get(reply_message_data["uuid"])
        ):
            # Data not in memory, so treat it as in game message
            return (
                f"回覆 {self._format_nickname(reply_message_data)}:"
                f" {reply_message_data['message']}\n> {content}"
            )

        discord_message = await self.get_channel().fetch_message(discord_message_id)

        return (
            (
                f"回覆 {self._format_nickname(reply_message_data)}："
                f"{reply_message_data['message']}\n> {content}"
            )
            if discord_message.webhook_id
            else (
                f"回覆 {discord_message.author.mention}：{discord_message.content}"
                f"\n {content}"
            )
        )

    @staticmethod
    def decode_data(data: list[int]) -> dict:
        return loads(
            "".join(chr(_) for _ in data).encode("raw_unicode_escape").decode()
        )

    @staticmethod
    def encode_data(data: dict):
        return [
            ord(_)
            for _ in dumps(data, separators=(",", ":"), ensure_ascii=False)
            .encode()
            .decode("raw_unicode_escape")
        ]

    async def connect(self, token: str | None = None):
        await self.sio.connect(
            self.universe_chat_base_url,
            transports="websocket",
            headers={"rpmtw_auth_token": token} if token else {},
        )

    async def disconnect(self):
        await self.sio.disconnect()

    async def send_discord_message(self, message: "Message"):
        content = message.content

        # Turn attachment(s) to url then append to content
        if attachments := message.attachments:
            content += "".join(f"\n{attachment.url}" for attachment in attachments)

        reply_message_uuid = (
            self.id_uuid.get(reply_message.id)
            if (reference := message.reference)
            and (reply_message := reference.resolved)
            else None
        )
        data = {
            "message": content,
            "username": message.author.name,
            "userId": str(message.author.id),
            "avaterUrl": message.author.display_avatar.url,
            "nickname": message.author.nick,
            "replyMessageUUID": reply_message_uuid if reply_message_uuid else None,
        }

        def callback(uuid: str):
            self.id_uuid[message.id] = uuid

        await self.sio.emit(
            "discordMessage",
            self.encode_data(data),
            callback=callback,
        )

    @staticmethod
    def _format_nickname(data: dict) -> str:
        return (
            f"{data['username']} ({nickname})"
            if (nickname := data["nickname"])
            else data["username"]
        )

    def _format_emoji_to_discord(self, message: str):
        pattern = compile(r":([a-zA-Z0-9_]+):")

        for _ in pattern.finditer(message):
            message = message.replace(
                _.group(0), f"<:{_.group(1)}:{self.get_emoji_data()[_.group(1)]}>"
            )

        return message

    def _format_emoji_to_minecraft(self, message: str):
        pattern = compile(r"<:([a-zA-Z0-9_]+):([0-9]+)>")

        for _ in pattern.finditer(message):
            message = message.replace(_.group(0), f":{_.group(1)}:")

        return message
