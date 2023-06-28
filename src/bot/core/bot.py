from datetime import datetime
from os import environ
from tomllib import load

from core.universe_chat import RPMTWApiClient
from discord import Bot, Intents
from packages.default_data import bot_logger


class RPMTWBot(Bot):
    def __init__(self, *, is_dev=True):
        self.online_time = datetime.now()

        with open("./data/constant.toml", "rb") as file:
            data = load(file)
            self.config: dict = data["dev" if is_dev else "main"]

        intents = Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(intents=intents, **self.config["bot_settings"])

        self.rpmtw_api_client = RPMTWApiClient(self, self.config["UniverseChat"])
        self.token = environ["TEST_BOT_TOKEN" if is_dev else "BOT_TOKEN"]

    async def on_ready(self):
        await self.rpmtw_api_client.connect(environ.get("CHAT_TOKEN"))
        bot_logger.info("bot is ready")

    def run(self):
        super().run(self.token)
