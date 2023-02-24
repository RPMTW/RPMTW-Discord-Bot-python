from os import environ
from pathlib import Path

import dotenv

from packages.default_data import *


class Bot(discord.Bot):
    def __init__(self):
        super().__init__(
            intent = discord.Intents.all()
        )

        self.load_extensions(
            *(f'extensions.{i.stem}' for i in Path('./src/bot/extensions').glob(r'*.py'))
        )
    
    async def on_ready(self):
        logging.info('bot is ready')
    
    @commands.slash_command(**ApplicationOption.default)
    async def hello(self, ctx: ApplicationContext):
        await ctx.respond(f'Hello, {ctx.author.mention}')
    
    @commands.slash_command(**ApplicationOption.default)
    async def info(self, ctx: ApplicationContext):
        await ctx.respond('WIP')


if __name__ == '__main__':
    dotenv.load_dotenv('./src/bot/config/.env')
    
    bot = Bot()
    bot.run(environ.get('TOKEN'))