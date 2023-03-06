import logging
from datetime import datetime
from os import environ, listdir

from core.extension import extension_list
from core.universe_chat import RPMTWApiClient
from discord import Bot, Intents
from packages.default_data import Config
from tomllib import load


class RPMTWBot(Bot):
    def __init__(self):
        with open("./constant.toml", "rb") as file:
            data = load(file)
            is_dev: bool = data["is_dev"]
            self.config: dict = data["test" if is_dev else "main"]

        self.test: bool = self.config["constant.is_test"]  # type: ignore
        self.stat = "test" if self.test else "main"
        self.online_time = datetime.now()

        intents = Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(
            intents=intents,
            **self.config[f"constant.{self.stat}.bot.settings"],
        )

        self.rpmtw_api_client = RPMTWApiClient(self, self.config["UniverseChat"])

    async def on_ready(self):
        self.load_extensions(*(f"extensions.{file}" for file in extension_list()))
        await self.rpmtw_api_client.connect(environ.get("CHAT_TOKEN"))
        logging.info("bot is ready")
