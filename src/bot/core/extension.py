from pathlib import Path
from typing import TYPE_CHECKING

from discord.cog import Cog, _cog_special_method
from packages.default_data import bot_logger

if TYPE_CHECKING:
    from core.bot import RPMTWBot

extension_list = lambda: (i.stem for i in Path("./src/bot/extensions").glob("*.py"))


class InitedCog(Cog):
    def __init__(self, bot: "RPMTWBot") -> None:
        super().__init__()
        self.bot = bot
        self.config: dict = bot.config.get(self._get_sub_class_name(), {})
        bot_logger.info(f"load extension - {self.__cog_name__}")

    @_cog_special_method
    async def cog_load(self):
        pass

    @classmethod
    def _get_sub_class_name(cls):
        return cls.__name__
