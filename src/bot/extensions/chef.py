from json import dump, load
from pathlib import Path
from typing import TYPE_CHECKING

from bidict import bidict
from discord import Embed, Member
from discord.ext import tasks
from packages.cog_data import *

if TYPE_CHECKING:
    from core.bot import RPMTWBot


class ChefCog(InitedCog):
    def __init__(self, bot: "RPMTWBot") -> None:
        super().__init__(bot)
        self.chef_data_path = Path("./data/chef_data.json")

        if self.chef_data_path.exists():
            with self.chef_data_path.open(encoding="UTF-8") as file:
                chef_data = bidict(load(file))
        else:
            chef_data = bidict()

        self.chef_data: bidict[str, int] = chef_data
        self.save_data.start()

    ChefSlashCommandGroup = commands.SlashCommandGroup("chef")

    @ChefSlashCommandGroup.command()
    async def rank(self, ctx: ApplicationContext):
        embed = Embed(title="電神排名", description="看看誰最電！ (前 10 名)")
        inverse_chef_data = self.chef_data.inverse

        for index, count in enumerate(
            sorted(self.chef_data.values(), reverse=True)[:10], 1
        ):
            embed.add_field(
                name=f"第 {index} 名",
                value=f"<@!{inverse_chef_data[count]}> 被廚了 {count} 次",
                inline=False,
            )

        await ctx.respond(embed=embed)

    @ChefSlashCommandGroup.command()
    async def chef(
        self,
        ctx: ApplicationContext,
        member: Member,
        message: str = "好電！",
    ):
        if member.bot:
            return await ctx.respond("您不能廚機器人")

        # get -> +1 -> assigned to `count`, update `self.chef_data`
        member_id = str(member.id)
        self.chef_data[member_id] = count = self.chef_data.get(str(member_id), 0) + 1
        await ctx.respond(f"{member.mention} {message}\n被廚了 {count} 次")

    @ChefSlashCommandGroup.command()
    async def save(self, ctx: ApplicationContext):
        self.save_chef_data()
        await ctx.respond("Chef data saved")

    def save_chef_data(self):
        with self.chef_data_path.open("w", encoding="UTF-8") as file:
            dump(dict(self.chef_data), file)

    @tasks.loop(minutes=30)
    async def save_data(self):
        await self.bot.wait_until_ready()
        self.save_chef_data()


def setup(bot: "RPMTWBot"):
    bot.add_cog(ChefCog(bot))
