from logging import basicConfig
from sys import argv

import dotenv
from core.bot import RPMTWBot
from core.extension import extension_list
from packages.default_data import *

if __name__ == "__main__":
    dotenv.load_dotenv()

    try:
        arg = argv[1]
    except IndexError:
        arg = None

    if arg != "--prod":
        basicConfig(level="INFO")
        bot = RPMTWBot(is_dev=True)
    else:
        bot = RPMTWBot()

    bot.load_extensions(*(f"extensions.{file}" for file in extension_list()))
    bot.run()
