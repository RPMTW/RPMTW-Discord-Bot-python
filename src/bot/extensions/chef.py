from typing import TYPE_CHECKING

from discord import Embed, User, Option
from discord.ext import tasks

from packages.cog_data import *

if TYPE_CHECKING:
    from core.bot import RPMTWBot


class ChefCog(InitedCog):
    def __init__(self, bot: "RPMTWBot") -> None:
        super().__init__(bot)
        self.chef_data: dict[str, int] = []
        self.rank_icons = ['🥇', '🥈', '🥉', '🏅']
        
        self.update_top10.start()

    ChefSlashCommandGroup = commands.SlashCommandGroup("chef")

    @ChefSlashCommandGroup.command()
    async def rank(self, ctx: ApplicationContext):
        embed = Embed(
            title = "Chef Rank",
            description = "\n".join(self.top10)
        )
        await ctx.respond(embed=embed)
    
    @commands.slash_command()
    async def rank(self, ctx: ApplicationContext, user: Option(User, default=None), message: str = "好電！"):
        user = user or ctx.author
        if (id:=str(user.id)) not in self.chef_data:
            count = self.chef_data.setdefault(id, 1)
        else:
            self.chef_data[id] += 1
            count = self.chef_data[id]

        await ctx.respond(f'{user.mention} {message}\n被廚了 `{count}` 次')
        

    @tasks.loop(minutes=30)
    async def update_top10(self):
        await self.bot.wait_until_ready()
        
        top10 = []
        for id, count in sorted(self.chef_data, key=lambda x: x[0], reverse=True):
            index = len(top10) + 1
            if user:=self.bot.get_user(id):
                icon = self.rank_icons[index] if index < 4 else self.rank_icons[-1]
                top10.append(f'{icon} **{index}** {user.mention}: `{count}`')
            if index == 10:
                break
        self.top10 = top10

def setup(bot: "RPMTWBot"):
    bot.add_cog(ChefCog(bot))