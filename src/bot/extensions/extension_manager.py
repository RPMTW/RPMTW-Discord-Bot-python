from pathlib import Path

from discord.commands import Option
from packages.cog_data import *

extension_list = [i.stem for i in Path("./src/bot/extensions").glob("*.py")]



class ExtensionManagerCog(InitedCog):
    ExtensionManagerSlashCommandGroup = commands.SlashCommandGroup(
        "ext-manager", **ApplicationOption.default
    )

    async def ext_action(self, ctx: ApplicationContext, ext_name: str, action: str):
        try:
            getattr(self.bot, f"{action}_extension")(f"extensions.{ext_name}")
        except:
            raise
        else:
            await ctx.respond(f"{action.title()} extension - {ext_name} success")

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


def setup(bot: Bot):
    bot.add_cog(ExtensionManagerCog(bot))
