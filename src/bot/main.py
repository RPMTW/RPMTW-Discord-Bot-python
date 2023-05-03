from sys import argv

import dotenv
from core.bot import RPMTWBot
from core.extension import extension_list

if __name__ == "__main__":
    dotenv.load_dotenv()

    try:
        arg = argv[1]
    except IndexError:
        arg = None

    bot = RPMTWBot(is_dev=False) if arg == "--prod" else RPMTWBot()
    bot.load_extensions(*(f"extensions.{file}" for file in extension_list()))
    bot.run()
