import logging
from pathlib import Path

from core.bot import RPMTWBot
from discord import Cog

extension_list = lambda: [i.stem for i in Path("./src/bot/extensions").glob("*.py")]


class InitedCog(Cog):
    def __init__(self, bot: RPMTWBot) -> None:
        super().__init__()
        self.bot = bot
        logging.debug(f"load extension - {self.__cog_name__}")
