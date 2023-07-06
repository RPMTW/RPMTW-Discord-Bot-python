from datetime import datetime
from os import getpid
from typing import TYPE_CHECKING

from discord import Color, Embed
from packages.cog_data import *
from psutil import Process, virtual_memory

if TYPE_CHECKING:
    from core.bot import RPMTWBot


class BasicCog(InitedCog):
    @commands.slash_command()
    async def hello(self, ctx: ApplicationContext):
        await ctx.respond(f"Hello, {ctx.author.mention}")

    @commands.slash_command()
    async def info(self, ctx: ApplicationContext):
        embed = Embed(color=Color.dark_gray())
        embed.set_author(name=f"{self.bot.user}", icon_url=self.bot.user.avatar.url)  # type: ignore
        for name, value, inline in (
            (
                "正常運作時間",
                f"{round(((datetime.now()-self.bot.online_time).seconds)/60, 2)} 分鐘",
                False,
            ),
            (
                "記憶體用量（目前使用量/總記憶體大小）",
                f"{round(Process(getpid()).memory_info().rss / 1024 ** 2, 2)} / {round(virtual_memory().total / 1024 ** 2, 2)} MiB",
                False,
            ),
            ("使用者快取", f"{self.bot.users.__len__()}", True),
            ("頻道快取", f"{[*self.bot.get_all_channels()].__len__()}", True),
            ("訊息快取", f"{self.bot.cached_messages.__len__()}", True),
            ("Shard 數量", f'{self.bot.shard_count or "0"}', False),
        ):
            embed.add_field(name=name, value=value, inline=inline)
        await ctx.respond(embed=embed)


def setup(bot: "RPMTWBot"):
    bot.add_cog(BasicCog(bot))
