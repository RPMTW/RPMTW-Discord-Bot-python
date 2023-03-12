import logging
from datetime import datetime
from os import environ
from tomllib import load

from core.extension import extension_list
from core.universe_chat import RPMTWApiClient
from discord import Bot, Intents


class RPMTWBot(Bot):
    def __init__(self):
        self.online_time = datetime.now()

        with open("./data/constant.toml", "rb") as file:
            data = load(file)
            is_dev: bool = data["is_dev"]
            self.config: dict = data["dev" if is_dev else "main"]

        intents = Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(intents=intents, **self.config["bot_settings"])

        self.rpmtw_api_client = RPMTWApiClient(self, self.config["UniverseChat"])
        self.token = environ["TEST_BOT_TOKEN" if is_dev else "BOT_TOKEN"]

    async def on_ready(self):
        self.load_extensions(*(f"extensions.{file}" for file in extension_list()))
        await self.rpmtw_api_client.connect(environ.get("CHAT_TOKEN"))
        logging.info("bot is ready")

    def run(self):
        super().run(self.token)
