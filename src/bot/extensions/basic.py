from typing import TYPE_CHECKING

from packages.cog_data import *

if TYPE_CHECKING:
    from core.bot import RPMTWBot


class BasicCog(InitedCog):
    @commands.slash_command()
    async def hello(self, ctx: ApplicationContext):
        await ctx.respond(f"Hello, {ctx.author.mention}")

    @commands.slash_command()
    async def info(self, ctx: ApplicationContext):
        await ctx.respond("WIP")


def setup(bot: "RPMTWBot"):
    bot.add_cog(BasicCog(bot))
