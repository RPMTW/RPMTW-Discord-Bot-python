from datetime import datetime
from os import environ
from tomllib import load
from typing import TYPE_CHECKING

from core.universe_chat import RPMTWApiClient
from discord import Bot, Intents
from packages.default_data import bot_logger

if TYPE_CHECKING:
    from core.extension import InitedCog


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

    def add_cog(self, cog: "InitedCog", *, override: bool = False) -> None:
        if not hasattr(cog.cog_load, "__cog_special_method__"):
            self.loop.create_task(cog.cog_load())
        return super().add_cog(cog, override=override)

    async def on_ready(self):
        await self.rpmtw_api_client.connect(environ.get("CHAT_TOKEN"))
        bot_logger.info("bot is ready")

    def run(self):
        super().run(self.token)
