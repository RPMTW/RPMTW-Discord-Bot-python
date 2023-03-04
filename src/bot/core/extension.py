import logging
from pathlib import Path
from typing import TYPE_CHECKING

from discord import Cog

if TYPE_CHECKING:
    from core.bot import RPMTWBot

extension_list = lambda: [i.stem for i in Path("./src/bot/extensions").glob("*.py")]


class InitedCog(Cog):
    def __init__(self, bot: "RPMTWBot") -> None:
        super().__init__()
        self.bot = bot
        logging.debug(f"load extension - {self.__cog_name__}")
