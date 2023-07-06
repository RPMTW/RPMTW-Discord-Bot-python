from typing import TYPE_CHECKING

from discord.commands import Option
from discord.ext.commands import is_owner
from packages.cog_data import *

if TYPE_CHECKING:
    from core.bot import RPMTWBot

from core.extension import extension_list


class ExtensionManagerCog(InitedCog):
    ExtensionManagerSlashCommandGroup = commands.SlashCommandGroup(
        "ext-manager", guild_ids=[1077436291563671603]
    )

    async def ext_action(self, ctx: ApplicationContext, ext_name: str, action: str):
        try:
            getattr(self.bot, f"{action}_extension")(f"extensions.{ext_name}")
            await ctx.respond(f"{action.title()} extension - {ext_name} success")
        except:
            raise

    @ExtensionManagerSlashCommandGroup.command()
    @is_owner()
    async def load(
        self, ctx: ApplicationContext, ext_name: Option(str, choices=extension_list())  # type: ignore
    ):
        await self.ext_action(ctx, ext_name, "load")

    @ExtensionManagerSlashCommandGroup.command()
    @is_owner()
    async def unload(
        self, ctx: ApplicationContext, ext_name: Option(str, choices=extension_list())  # type: ignore
    ):
        await self.ext_action(ctx, ext_name, "unload")

    @ExtensionManagerSlashCommandGroup.command()
    @is_owner()
    async def reload(
        self, ctx: ApplicationContext, ext_name: Option(str, choices=extension_list())  # type: ignore
    ):
        await self.ext_action(ctx, ext_name, "reload")


def setup(bot: "RPMTWBot"):
    if bot.is_dev:
        bot.add_cog(ExtensionManagerCog(bot))
