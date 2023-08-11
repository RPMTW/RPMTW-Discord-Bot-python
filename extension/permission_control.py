from dataclasses import dataclass

from disnake import Member, Message, MessageCommandInteraction, TextChannel, Thread
from disnake.ext.commands import message_command
from lux import GeneralCog, Lux, send_ephemeral


@dataclass
class Config:
    guild_id: int
    role_id: int


class PermissionControl(GeneralCog):
    config: Config

    async def cog_load(self):
        await self.bot.wait_until_ready()

        if not (guild := self.bot.get_guild(self.config.guild_id)):
            return self.logger.error("Guild id invalid")
        if not (_ := guild.get_role(role_id := self.config.role_id)):
            return self.logger.error("Role id invalid")

        self.role_id: int = role_id

    async def check(self, inter: MessageCommandInteraction):
        assert isinstance(author := inter.author, Member)

        if inter.target.is_system():
            await send_ephemeral("本指令不可用於系統訊息")
            return False
        if not isinstance(inter.channel, (TextChannel, Thread)):
            await send_ephemeral("本指令僅能用在文字頻道或討論串")
            return False
        if not author.get_role(self.role_id):
            await send_ephemeral("你沒有權限使用本指令")
            return False
        return True

    @message_command(name="釘選", guild_only=True)
    async def pin(self, inter: MessageCommandInteraction, message: Message):
        if not await self.check(inter):
            return

        await message.pin(reason=f"{inter.author.mention} 使用了 '{inter.application_command.name}' 指令")
        await send_ephemeral("釘選成功")

    @message_command(name="取消釘選", guild_only=True)
    async def unpin(self, inter: MessageCommandInteraction, message: Message):
        if not await self.check(inter):
            return

        await message.unpin(reason=f"{inter.author.mention} 使用了 '{inter.application_command.name}' 指令")
        await send_ephemeral("取消釘選成功")


def setup(bot: Lux):
    bot.add_cog(PermissionControl())
