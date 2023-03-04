from typing import TYPE_CHECKING

from discord import DiscordException
from discord.ext.commands import errors

from packages.cog_data import *

if TYPE_CHECKING:
    from core.bot import RPMTWBot

class EventCog(InitedCog):
    @InitedCog.listener()
    async def on_application_command_error(self, ctx: ApplicationContext, exc: DiscordException):
        if isinstance(exc, errors.NotOwner):
            await ctx.respond('你不是機器人所有者，無法使用該指令')
        else:
            raise exc

def setup(bot: "RPMTWBot"):
    bot.add_cog(EventCog(bot))