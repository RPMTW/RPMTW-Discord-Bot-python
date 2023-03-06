import logging
from asyncio import Queue
from json import dumps, loads
from re import compile
from typing import TYPE_CHECKING

from aiohttp import ClientSession
from bidict import bidict
from discord import DiscordException, Webhook
from socketio import AsyncClient

if TYPE_CHECKING:
    from core.bot import RPMTWBot
    from discord import Message, TextChannel


class RPMTWApiClient:
    def __init__(self, bot: "RPMTWBot", config: dict) -> None:
        self.bot = bot
        self.config = config
        self.sio = AsyncClient()
        self.received_data: Queue[dict] = Queue()
        self.id_uuid = bidict()
        self.channel: TextChannel = bot.get_channel(config["channel_id"])  # type: ignore
        self.webhook: Webhook = None  # type: ignore

        @self.sio.event
        def connect():
            logging.info("Connected to Universe Chat server")

        @self.sio.event
        def disconnect():
            logging.info("Disconnected from Universe Chat server")

        @self.sio.event
        def connect_error(data):
            logging.error(f"Connection error: {data}")

        @self.sio.event
        async def sentMessage(data: list[int]):
            decoded_data = self.decode_data(data)

            if decoded_data["userType"] == "discord":
                return

            webhook = await self.get_webhook()

            try:
                discord_message: Message = await webhook.send(
                    await self.get_content(decoded_data),
                    avatar_url=decoded_data["avatarUrl"],
                    username=self._format_nickname(decoded_data),
                )  # type: ignore
                self.id_uuid[discord_message.id] = decoded_data["uuid"]
            except DiscordException as e:
                logging.error(f"Send cosmic chat message to discord failed: {e}")

        self.api_base_url = config["api_base_url"]
        self.emoji_data = {
            emoji.name: str(emoji.id)
            for emoji in bot.get_guild(config["guild_id"]).emojis  # type: ignore
        }

    async def get_webhook(self):
        if not self.webhook:
            webhooks = await self.channel.webhooks()
            self.webhook = webhooks[0]

        return self.webhook

    def get_emoji_data(self):
        if not self.emoji_data:
            self.emoji_data = {
                emoji.name: str(emoji.id)
                for emoji in self.bot.get_guild(self.config["guild_id"]).emojis  # type: ignore
            }

        return self.emoji_data

    async def get_message_data_by_uuid(self, uuid) -> dict:
        link = f"{self.api_base_url}/universe-chat/view/{uuid}"

        async with ClientSession() as session:
            async with session.get(link) as response:
                return await response.json()

    async def get_content(self, decoded_data: dict):
        content: str = decoded_data["message"]

        if not (reply_uuid := decoded_data["replyMessageUUID"]):
            return content

        reply_message_data = await self.get_message_data_by_uuid(reply_uuid)

        if not (discord_message_id := self.id_uuid.get(reply_message_data["uuid"])):
            # Data not in memory, so treat it as in game message
            return f"回覆 {self._format_nickname(reply_message_data)}: {reply_message_data['message']}\n> {content}"

        discord_message = await self.channel.fetch_message(discord_message_id)

        return (
            f"回覆 {self._format_nickname(reply_message_data)}: {reply_message_data['message']}\n> {content}"
            if discord_message.webhook_id
            else f"回覆 {discord_message.author.mention}: {discord_message.content}\n {content}"
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
            self.api_base_url,
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

        uuid = str()
        reply_message_uuid = (
            self.id_uuid.get(reply_message.id)
            if (reference := message.reference)
            and (reply_message := reference.resolved)
            else None
        )
        data = {
            "message": content,
            "username": message.author.name,
            "userId": message.author.id,
            "avaterUrl": message.author.display_avatar.url,
            "nickname": message.author.nick,  # type: ignore
            "replyMessageUUID": reply_message_uuid if reply_message_uuid else None,
        }

        def callback(_uuid: str):
            nonlocal uuid
            uuid = _uuid

        await self.sio.emit(
            "discordMessage",
            self.encode_data(data),
            callback=callback,
        )

        self.id_uuid[message.id] = uuid

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
                _.group(0), f"<:{_.group(1)}:{self.emoji_data[_.group(1)]}>"
            )

        return message

    def _format_emoji_to_minecraft(self, message: str):
        pattern = compile(r"<:([a-zA-Z0-9_]+):([0-9]+)>")

        for _ in pattern.finditer(message):
            message = message.replace(_.group(0), f":{_.group(1)}:")

        return message
