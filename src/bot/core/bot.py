import logging
from os import listdir

from discord import Bot, Intents
from packages.default_data import Config
from tomllib import load


class RPMBot(Bot):
    def __init__(self):
        intents = Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)

        data = {}
        for filename in listdir("./src/bot/data"):
            with open(f"./src/bot/data/{filename}", "rb") as file:
                data[filename.removesuffix(".toml")] = load(file)
        self.config = Config(data)

    async def on_ready(self):
        logging.info("bot is ready")
