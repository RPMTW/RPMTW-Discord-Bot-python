from typing import TYPE_CHECKING

from core.extension import InitedCog
from discord import ApplicationContext, Member, Message, TextChannel, Thread
from discord.commands import message_command

if TYPE_CHECKING:
    from core.bot import RPMTWBot

from threading import Thread


class PermissionControl(InitedCog):
    async def cog_load(self):
        await self.bot.wait_until_ready()

        if not (guild := self.bot.get_guild(self.bot.config["guild_id"])):
            raise ValueError("Guild id invalid")
        if not (_ := guild.get_role(role_id := self.config["role_id"])):
            raise ValueError("Role id invalid")

        self.role_id: int = role_id

    async def check(self, ctx: ApplicationContext):
        assert isinstance(author := ctx.author, Member)

        if not isinstance(ctx.channel, (TextChannel, Thread)):
            await self.send_ephemeral(ctx, "本指令僅能用在文字頻道或討論串")
            return False
        if not author.get_role(self.role_id):
            await self.send_ephemeral(ctx, "你沒有權限使用本指令")
            return False
        return True

    @staticmethod
    async def send_ephemeral(ctx: ApplicationContext, content: str):
        await ctx.interaction.response.send_message(content, ephemeral=True)

    @message_command(name="釘選", guild_only=True)
    async def pin(self, ctx: ApplicationContext, message: Message):
        if not await self.check(ctx):
            return

        await message.pin()
        await self.send_ephemeral(ctx, "釘選成功")

    @message_command(name="取消釘選", guild_only=True)
    async def unpin(self, ctx: ApplicationContext, message: Message):
        if not await self.check(ctx):
            return

        await message.unpin()
        await self.send_ephemeral(ctx, "取消釘選成功")


def setup(bot: "RPMTWBot"):
    bot.add_cog(PermissionControl(bot))
