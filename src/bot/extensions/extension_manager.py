from typing import TYPE_CHECKING

from discord.commands import Option
from packages.cog_data import *

if TYPE_CHECKING:
    from core.bot import RPMBot

from core.extension import extension_list


class ExtensionManagerCog(InitedCog):
    ExtensionManagerSlashCommandGroup = commands.SlashCommandGroup(
        "ext-manager", **ApplicationOption.default
    )

    async def ext_action(self, ctx: ApplicationContext, ext_name: str, action: str):
        try:
            getattr(self.bot, f"{action}_extension")(f"extensions.{ext_name}")
            await ctx.respond(f"{action.title()} extension - {ext_name} success")
        except:
            raise

    @ExtensionManagerSlashCommandGroup.command(**ApplicationOption.default)
    @CommandChecks.is_developer()
    async def load(
        self, ctx: ApplicationContext, ext_name: Option(str, choices=extension_list)  # type: ignore
    ):
        await self.ext_action(ctx, ext_name, "load")

    @ExtensionManagerSlashCommandGroup.command(**ApplicationOption.default)
    @CommandChecks.is_developer()
    async def unload(
        self, ctx: ApplicationContext, ext_name: Option(str, choices=extension_list)  # type: ignore
    ):
        await self.ext_action(ctx, ext_name, "unload")

    @ExtensionManagerSlashCommandGroup.command(**ApplicationOption.default)
    @CommandChecks.is_developer()
    async def reload(
        self, ctx: ApplicationContext, ext_name: Option(str, choices=extension_list)  # type: ignore
    ):
        await self.ext_action(ctx, ext_name, "reload")


def setup(bot: "RPMBot"):
    bot.add_cog(ExtensionManagerCog(bot))
