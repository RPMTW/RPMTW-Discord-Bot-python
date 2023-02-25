import logging
from pathlib import Path

from core.bot import RPMBot
from discord import Cog

extension_list = [i.stem for i in Path("./src/bot/extensions").glob("*.py")]


class InitedCog(Cog):
    def __init__(self, bot: RPMBot) -> None:
        super().__init__()
        self.bot = bot
        logging.debug(f"load extension - {self.__cog_name__}")
