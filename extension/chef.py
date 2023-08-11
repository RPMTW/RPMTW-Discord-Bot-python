from csv import QUOTE_MINIMAL, reader, writer
from heapq import nlargest
from json import load
from pathlib import Path
from typing import TypeAlias

from disnake import Embed, Member
from disnake.ext.tasks import loop
from lux import AppCmdInter, GeneralCog, Lux, slash_command

Id: TypeAlias = int
Count: TypeAlias = int


class Chef(GeneralCog):
    def __init__(self) -> None:
        super().__init__()
        self._legacy_data_path = Path("./data/chef_data.json")
        self._data_path = Path("./chef_data.csv")

        if self._legacy_data_path.exists():
            with self._legacy_data_path.open(encoding="UTF-8") as file:
                data = dict(load(file))
            self._legacy_data_path.unlink()
        elif self._data_path.exists():
            with self._data_path.open(encoding="UTF-8", newline="") as file:
                data = {Id(row[0]): Count(row[1]) for row in reader(file)}
        else:
            data = dict()

        self.data: dict[Id, Count] = data
        self.data_snapshot: dict[Id, Count] = data.copy()
        self.save_data.start()

    def _save_data(self):
        data_changed = self.data != self.data_snapshot

        if not data_changed:
            return

        self.data_snapshot = self.data.copy()

        with self._data_path.open("w", encoding="UTF-8", newline="") as file:
            writer_ = writer(file, quoting=QUOTE_MINIMAL)
            writer_.writerows(self.data.items())

    @loop(minutes=30)
    async def save_data(self):
        await self.bot.loop.run_in_executor(None, self._save_data)

    @save_data.before_loop
    async def before_save_data(self):
        await self.bot.wait_until_ready()

    @slash_command(name="chef", dm_permission=False)
    async def chef_(self, inter: AppCmdInter):
        return None

    @chef_.sub_command()
    async def chef(self, inter: AppCmdInter, member: Member, message: str = "好電！"):
        if member.bot:
            return await inter.send("您不能廚機器人")

        member_id = member.id
        self.data[member_id] = count = self.data.get(member_id, 0) + 1
        await inter.send(f"{member.mention} {message}\n被廚了 {count} 次")

    @chef_.sub_command()
    async def rank(self, inter: AppCmdInter):
        embed = Embed(title="電神排名", description="看看誰最電！ (前 10 名)")
        top_10 = nlargest(10, self.data.items(), key=lambda _: _[1])

        for index, rank_data in enumerate(top_10, 1):
            embed.add_field(
                name=f"第 {index} 名",
                value=f"<@!{rank_data[0]}> 被廚了 {rank_data[1]} 次",
                inline=False,
            )

        await inter.send(embed=embed)


def setup(bot: Lux):
    bot.add_cog(Chef())
