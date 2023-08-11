from dataclasses import dataclass
from os import environ

from disnake import Message, TextChannel
from lib.universe_chat import APIClient
from lux import GeneralCog, Lux


@dataclass
class Config:
    guild_id: int
    channel_id: int
    universe_chat_api_base_url: str
    universe_chat_base_url: str


class UniverseChat(GeneralCog):
    config: Config

    async def cog_load(self) -> None:
        await self.bot.wait_until_ready()

        if not (channel := self.bot.get_channel(self.config.channel_id)):
            return self.logger.error("Channel id invalid")
        if not isinstance(channel, TextChannel):
            return self.logger.error("Channel type incorrect")

        self.channel = channel

        if not (api_client := await APIClient(self.config, self.logger.getChild("api_client")).init(channel)):
            return self.logger.error("API client init failed")

        self.api_client = api_client
        await self.api_client.connect(environ.get("UNIVERSE_CHAT_TOKEN"))

    async def cog_unload(self) -> None:
        await self.api_client.disconnect()

    @GeneralCog.listener()
    async def on_message(self, message: Message):
        if message.channel != self.channel or message.author.bot or not message.guild:
            return

        await self.api_client.send_discord_message(message)


def setup(bot: Lux):
    bot.add_cog(UniverseChat())
