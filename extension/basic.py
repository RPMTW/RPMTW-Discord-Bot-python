from datetime import datetime

from disnake import Color, Embed
from lux import AppCmdInter, GeneralCog, Lux, slash_command
from psutil import Process, virtual_memory


class Basic(GeneralCog):
    async def cog_load(self) -> None:
        await super().cog_load()
        online_time = datetime.now()
        self.logger.info(f"Set online time to {online_time}")
        self.online_time = online_time

    @slash_command()
    async def hello(self, inter: AppCmdInter):
        await inter.send(f"Hello, {inter.author.mention}")

    @slash_command()
    async def info(self, inter: AppCmdInter):
        embed = Embed(color=Color.dark_gray())
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.display_avatar.url).add_field(
            "正常運作時間",
            f"{round(((datetime.now()-self.online_time).total_seconds())/60, 2)} 分鐘",
            inline=False,
        ).add_field(
            "記憶體用量（目前使用量/總記憶體大小）",
            f"{Process().memory_info().rss / 1024 ** 2:.2f} / {virtual_memory().total / 1024 ** 2:.2f} MiB",
            inline=False,
        )
        embed.add_field("使用者快取", len(self.bot.users))
        embed.add_field("頻道快取", len(list(self.bot.get_all_channels())))
        embed.add_field("訊息快取", len(self.bot.cached_messages))
        embed.add_field("Shard 數量", self.bot.shard_count or 0, inline=False)

        await inter.send(embed=embed)


def setup(bot: Lux):
    bot.add_cog(Basic())
