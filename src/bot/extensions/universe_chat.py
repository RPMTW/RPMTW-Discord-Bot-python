from typing import TYPE_CHECKING

from discord import Message
from packages.cog_data import *

if TYPE_CHECKING:
    from core.bot import RPMTWBot


class UniverseChat(InitedCog):
    def __init__(self, bot: "RPMTWBot") -> None:
        super().__init__(bot)
        self.channel_id: int = self.config["channel_id"]

    @InitedCog.listener()
    async def on_message(self, message: Message):
        if message.channel.id != self.channel_id or message.author.bot:
            return

        await self.bot.rpmtw_api_client.send_discord_message(message)


def setup(bot: "RPMTWBot"):
    bot.add_cog(UniverseChat(bot))
