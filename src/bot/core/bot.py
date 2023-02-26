import logging

from discord import Bot, Intents


class RPMBot(Bot):
    def __init__(self):
        intents = Intents.default()
        intents.message_content = True
        super().__init__(intents=Intents.all())

    async def on_ready(self):
        logging.info("bot is ready")
