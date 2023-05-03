from typing import TYPE_CHECKING
from pathlib import Path

from discord import Cog

if TYPE_CHECKING:
    from packages import RPMTWBot

extension_list = lambda: (i.stem for i in Path("./src/bot/extensions").glob("*.py"))


class InitedCog(Cog):
    def __init__(self, bot: "RPMTWBot") -> None:
        super().__init__()
        self.bot = bot
        self.config: dict = bot.config.get(self._get_sub_class_name(), {})
        self._maybe_none = {}
        self.log = bot.log

        self.log.info(f"load extension - {self.__cog_name__}")

    @classmethod
    def _get_sub_class_name(cls):
        return cls.__name__
