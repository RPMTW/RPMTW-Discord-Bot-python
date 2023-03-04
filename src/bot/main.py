from os import environ

import dotenv
from core.bot import RPMTWBot
from core.extension import extension_list
from packages.default_data import *

if __name__ == "__main__":
    dotenv.load_dotenv()

    bot = RPMTWBot()
    bot.load_extensions(*(f"extensions.{file}" for file in extension_list))
    bot.run(environ["TEST_TOKEN" if bot.test else "TOKEN"])
