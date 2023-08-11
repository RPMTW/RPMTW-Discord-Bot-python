from dataclasses import dataclass

from disnake import DiscordException, Member, Message
from disnake.ext.commands.errors import NotOwner
from lux import AppCmdInter, GeneralCog, Lux, send_ephemeral


@dataclass
class Config:
    guild_id: int
    role_id: int
    channel_id: int


class Event(GeneralCog):
    config: Config

    async def cog_load(self):
        await self.bot.wait_until_ready()

        if not (guild := self.bot.get_guild(self.config.guild_id)):
            return self.logger.error("Guild id invalid")
        if not (role := guild.get_role(self.config.role_id)):
            return self.logger.error("Role id invalid")
        if not (channel := guild.get_channel(self.config.channel_id)):
            return self.logger.error("Channel id invalid")

        self.role = role
        self.channel = channel

    @GeneralCog.listener()
    async def on_application_command_error(self, inter: AppCmdInter, exc: DiscordException):
        if not isinstance(exc, NotOwner):
            raise exc
        await send_ephemeral("你不是機器人所有者，無法使用該指令")

    @GeneralCog.listener()
    async def on_message(self, message: Message):
        if (author := message.author).bot or not isinstance(author, Member):
            return

        if message.channel == self.channel:
            await author.add_roles(self.role)


def setup(bot: Lux):
    bot.add_cog(Event())
