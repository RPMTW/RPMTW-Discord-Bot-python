from typing import TYPE_CHECKING

from packages.cog_data import *

if TYPE_CHECKING:
    from core.bot import RPMBot


class Basic(InitedCog):
    @commands.slash_command(**ApplicationOption.default)
    async def hello(self, ctx: ApplicationContext):
        await ctx.respond(f"Hello, {ctx.author.mention}")

    @commands.slash_command(**ApplicationOption.default)
    async def info(self, ctx: ApplicationContext):
        await ctx.respond("WIP")


def setup(bot: "RPMBot"):
    bot.add_cog(Basic(bot))
