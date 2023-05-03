from json import dump, load
from pathlib import Path

from discord import Embed, Member
from discord.ext import tasks

from packages import InitedCog, commands, RPMTWBot, ApplicationContext


class ChefCog(InitedCog):
    def __init__(self, bot: "RPMTWBot") -> None:
        super().__init__(bot)
        self.chef_data_path = Path("./data/chef_data.json")

        if self.chef_data_path.exists():
            with self.chef_data_path.open(encoding="UTF-8") as file:
                chef_data = dict(load(file))
        else:
            chef_data = dict()

        self.chef_data: dict[int, int] = chef_data
        self.save_data.start()

    ChefSlashCommandGroup = commands.SlashCommandGroup("chef")

    @ChefSlashCommandGroup.command()
    async def rank(self, ctx: ApplicationContext):
        embed = Embed(title="電神排名", description="看看誰最電！ (前 10 名)")
        sorted_data = sorted(self.chef_data.items(), key=lambda _: _[1], reverse=True)

        for index, rank_data in enumerate(sorted_data, 1):
            embed.add_field(
                name=f"第 {index} 名",
                value=f"<@!{rank_data[0]}> 被廚了 {rank_data[1]} 次",
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
        member_id = member.id
        self.chef_data[member_id] = count = self.chef_data.get(member_id, 0) + 1
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
