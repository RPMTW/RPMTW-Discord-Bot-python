import logging

import discord
from discord import Bot, commands, ApplicationContext

class Option:
    __slots__ = ['default']
    
    default = {
        "guild_ids": [
            815819580840607807
        ]
    }

option = Option()