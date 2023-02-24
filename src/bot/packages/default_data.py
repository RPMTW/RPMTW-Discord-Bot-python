import logging

import discord
from default_data import commands_checks, option
from discord import ApplicationContext, Bot, commands
from discord.ext.commands import check


class BotOption:
    default = {"guild_ids": [815819580840607807]}


option = BotOption()


class Config:
    def __init__(self, data: dict) -> None:
        for key, value in data.items():
            if isinstance(value, dict):
                setattr(self, key, Config(value))
            else:
                setattr(self, key, value)

    def __getitem__(self, key: str):
        return getattr(self, key)


class commands_checks:
    @staticmethod
    def is_developer():
        def predicate(ctx):
            return ctx.author.id in {
                467532880625664000,  # YT Mango#4092
                645588343228334080,  # 菘菘#8663
                577086242806693898,  # Euxcbsks#5316
            }

        return check(predicate)
