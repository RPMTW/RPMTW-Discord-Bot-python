import logging
from os import listdir
from datetime import datetime

from core.extension import extension_list
from discord import Bot, Intents
from packages.default_data import Config
from tomllib import load


class RPMTWBot(Bot):
    def __init__(self):
        data = {}
        for filename in listdir("./src/bot/data"):
            with open(f"./src/bot/data/{filename}", "rb") as file:
                data[filename.removesuffix(".toml")] = load(file)
        self.config = Config(data)
        self.test: bool = self.config["constant.is_test"]  # type: ignore
        self.online_time = datetime.now()

        intents = Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(
            intents=intents,
            **self.config[f"constant.{'test' if self.test else 'main'}.bot.settings"],
        )

    async def on_ready(self):
        self.load_extensions(*(f"extensions.{file}" for file in extension_list()))
        logging.info("bot is ready")
