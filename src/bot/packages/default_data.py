import logging

import discord
from discord import Bot, commands, ApplicationContext

class Option:
    default = {
        "guild_ids": [
            815819580840607807
        ]
    }

option = Option()

class Config:
    def __init__(self, data: dict) -> None:
        for key, value in data.items():
            if isinstance(value, dict):
                setattr(key, Config(value))
            else:
                setattr(key, value)
    
    def __getitem__(self, key: str):
        return getattr(self, key)

class commands_checks:
    def is_developer(ctx: ApplicationContext):
        return ctx.author.id in {
            467532880625664000, # YT Mango#4092
            645588343228334080  # 菘菘#8663
        }