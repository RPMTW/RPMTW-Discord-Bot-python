from typing import TYPE_CHECKING
from json import dump, load

from discord import Embed, User, Option
from discord.ext import tasks

from packages.cog_data import *

if TYPE_CHECKING:
    from core.bot import RPMTWBot


class ChefCog(InitedCog):
    def __init__(self, bot: "RPMTWBot") -> None:
        super().__init__(bot)
        
        try:
            with open("./data/chef_data.json", "w") as file:
                self.chef_data: dict[str, int] = load(file)
        except FileNotFoundError:
            self.chef_data: dict[str, int] = {}
        self.rank_icons = ['🥇', '🥈', '🥉', '🏅']
        
        self.save_data.start()

    ChefSlashCommandGroup = commands.SlashCommandGroup("chef")

    @ChefSlashCommandGroup.command()
    async def rank(self, ctx: ApplicationContext):
        top10 = []
        for id, count in sorted(self.chef_data, key=lambda x: x[0], reverse=True):
            index = len(top10) + 1
            if user:=self.bot.get_user(id):
                icon = self.rank_icons[index] if index < 4 else self.rank_icons[-1]
                top10.append(f'{icon} **{index}** {user.mention}: `{count}`')
            if index == 10:
                break
        
        embed = Embed(
            title = "Chef Rank",
            description = "\n".join(top10)
        )
        await ctx.respond(embed=embed)
    
    @commands.slash_command()
    async def chef(self, ctx: ApplicationContext, user: Option(User, default=None), message: str = "好電！"):
        user = user or ctx.author
        if (id:=str(user.id)) not in self.chef_data:
            count = self.chef_data.setdefault(id, 1)
        else:
            self.chef_data[id] += 1
            count = self.chef_data[id]

        await ctx.respond(f'{user.mention} {message}\n被廚了 `{count}` 次')

    @tasks.loop(minutes=30)
    async def save_data(self, ):
        await self.bot.wait_until_ready()
        with open("./data/chef_data.json", "w") as file:
            dump(self.chef_data, file, indent=2)

def setup(bot: "RPMTWBot"):
    bot.add_cog(ChefCog(bot))