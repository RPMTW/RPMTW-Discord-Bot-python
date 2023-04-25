from typing import TYPE_CHECKING

from discord import DiscordException, Message
from discord.ext.commands import errors

from packages.cog_data import *

if TYPE_CHECKING:
    from core.bot import RPMTWBot
    from discord import Role


class EventCog(InitedCog):
    def get_role(self) -> "Role":
        if _ := self._maybe_none.get("role"):
            return _
        
        if not (_ := self.bot.get_guild(815819580840607807).get_role(945632168124751882)):
            raise ValueError("Guild or role id invalid")
        
        self._maybe_none["role"] = _
        return _
            
    @InitedCog.listener()
    async def on_application_command_error(self, ctx: ApplicationContext, exc: DiscordException):
        if isinstance(exc, errors.NotOwner):
            await ctx.respond('你不是機器人所有者，無法使用該指令')
        else:
            raise exc
    
    @InitedCog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return
        if message.channel.id == 940533694697975849:
            await message.author.add_roles(self.get_role())

def setup(bot: "RPMTWBot"):
    bot.add_cog(EventCog(bot))
