from typing import TYPE_CHECKING

from discord import DiscordException, Member, Message
from discord.ext.commands import errors
from packages.cog_data import *

if TYPE_CHECKING:
    from core.bot import RPMTWBot


class EventCog(InitedCog):
    async def cog_load(self):
        await self.bot.wait_until_ready()

        if not (guild := self.bot.get_guild(self.bot.config["guild_id"])):
            raise ValueError("Guild id invalid")
        if not (role := guild.get_role(self.config["role_id"])):
            raise ValueError("Role id invalid")
        if not (channel := guild.get_channel(self.config["channel_id"])):
            raise ValueError("Channel id invalid")

        self.role = role
        self.channel = channel

    @InitedCog.listener()
    async def on_application_command_error(
        self, ctx: ApplicationContext, exc: DiscordException
    ):
        if isinstance(exc, errors.NotOwner):
            await ctx.respond("你不是機器人所有者，無法使用該指令")
        else:
            raise exc

    @InitedCog.listener()
    async def on_message(self, message: Message):
        if (author := message.author).bot or not isinstance(author, Member):
            return

        if message.channel == self.channel:
            await author.add_roles(self.role)


def setup(bot: "RPMTWBot"):
    bot.add_cog(EventCog(bot))
