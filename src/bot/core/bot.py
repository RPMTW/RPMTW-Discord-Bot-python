import logging

from discord import Bot, Intents


class RPMBot(Bot):
    def __init__(self):
        super().__init__(intent=Intents.all())

    async def on_ready(self):
        logging.info("bot is ready")