import dotenv
from core.bot import RPMTWBot
from packages.default_data import *

if __name__ == "__main__":
    dotenv.load_dotenv()

    bot = RPMTWBot()
    bot.run()
