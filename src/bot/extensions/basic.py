from typing import TYPE_CHECKING
from datetime import datetime

from discord import Embed, Color

from packages.cog_data import *

if TYPE_CHECKING:
    from core.bot import RPMTWBot


class BasicCog(InitedCog):
    @commands.slash_command()
    async def hello(self, ctx: ApplicationContext):
        await ctx.respond(f"Hello, {ctx.author.mention}")

    @commands.slash_command()
    async def info(self, ctx: ApplicationContext):
        embed = Embed(color=Color.dark_gray())
        embed.set_author(name=f'{self.bot.user}', icon_url=self.bot.user.avatar.url)
        for name, value in zip(('正常運作時間', f'{(self.bot.online_time-datetime.now()).min}'),
                               ('記憶體用量（目前使用量/常駐記憶體大小）', ''),
                               ('使用者快取', f'{self.bot.users.__len__()}'),
                               ('頻道快取', f'{self.bot.get_all_channels().__len__()}'),
                               ('訊息快取', f'{self.bot.cached_messages}'),
                               ('Shard 數量', f'{self.bot.shard_count}')):
            embed.add_field(name=name, value=value)
        await ctx.respond(embed = embed)


def setup(bot: "RPMTWBot"):
    bot.add_cog(BasicCog(bot))
