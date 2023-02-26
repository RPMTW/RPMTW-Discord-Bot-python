import logging
import tomllib
import os

from discord import Bot, Intents

from packages.default_data import Config

class RPMBot(Bot):
    def __init__(self):
        super().__init__(intents=Intents.all())
        
        _config = {}
        for filename in os.listdir('./src/bot/data'):
            with open(f'./src/bot/data/{filename}', 'rb') as file:
                _config[filename.removesuffix('.toml')] = tomllib.load(file)
        self.config = Config(_config)

    async def on_ready(self):
        logging.info("bot is ready")
