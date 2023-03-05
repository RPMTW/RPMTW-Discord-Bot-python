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
        data = {}
        for filename in listdir("./src/bot/data"):
            with open(f"./src/bot/data/{filename}", "rb") as file:
                data[filename.removesuffix(".toml")] = load(file)
        self.config = Config(data)
        self.test: bool = self.config["constant.is_test"]  # type: ignore
        self.stat = "test" if self.test else "main"
        self.online_time = datetime.now()
        self.rpmtw_api_client = None

        intents = Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(
            intents=intents,
            **self.config[f"constant.{self.stat}.bot.settings"],
        )

    def get_rpmtw_api_client(self):
        if not self.rpmtw_api_client:
            self.rpmtw_api_client = RPMTWApiClient(self)

        return self.rpmtw_api_client

    async def on_ready(self):
        self.load_extensions(*(f"extensions.{file}" for file in extension_list()))
        await self.get_rpmtw_api_client().connect(environ.get("CHAT_TOKEN"))
        logging.info("bot is ready")
