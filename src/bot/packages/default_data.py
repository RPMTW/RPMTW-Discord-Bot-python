import logging

import discord
from discord import ApplicationContext, Bot, commands
from discord.ext.commands import check

logging.basicConfig(level=logging.INFO)


class ApplicationOption:
    default = {"guild_ids": [815819580840607807]}


class Config:
    def __init__(self, data: dict) -> None:
        for key, value in data.items():
            if isinstance(value, dict):
                setattr(self, key, Config(value))
            else:
                setattr(self, key, value)

    def __getitem__(self, key: str):
        return getattr(self, key)


class CommandChecks:
    @staticmethod
    def is_developer():
        def predicate(ctx):
            return ctx.author.id in {
                467532880625664000,  # YT Mango#4092
                645588343228334080,  # 菘菘#8663
                577086242806693898,  # Euxcbsks#5316
            }

        return check(predicate)


__all__ = [
    "logging",
    "discord",
    "ApplicationContext",
    "Bot",
    "commands",
    "ApplicationOption",
    "Config",
    "CommandChecks",
]
