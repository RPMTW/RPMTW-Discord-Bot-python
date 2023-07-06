from typing import TYPE_CHECKING

from discord import DiscordException, Member, Message
from discord.ext.commands import errors
from packages.cog_data import *

if TYPE_CHECKING:
    from core.bot import RPMTWBot


class EventCog(InitedCog):
    async def cog_load(self):
        await self.bot.wait_until_ready()

        if not (guild := self.bot.get_guild(815819580840607807)):
            raise ValueError("Guild id invalid")
        if not (role := guild.get_role(945632168124751882)):
            raise ValueError("Role id invalid")

        self.role = role

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

        if message.channel.id == 940533694697975849:
            await author.add_roles(self.role)


def setup(bot: "RPMTWBot"):
    bot.add_cog(EventCog(bot))
