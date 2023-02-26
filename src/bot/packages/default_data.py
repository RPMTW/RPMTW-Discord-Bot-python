import logging

import discord
from discord import ApplicationContext, Bot, commands
from discord.ext.commands import check

logging.basicConfig(level=logging.INFO)


class ApplicationOption:
    default = {"guild_ids": [815819580840607807]}


class Config:
    def __init__(self, data: dict) -> None:
        self.data = data

    def __getitem__(self, key: str):
        """
        `key`: dot split keys,
            eg: `data = {"key": {"subkey": value}}`

            use `value = Config(data)["key.subkey"]` to get value
        """
        data = self.data
        for _ in key.split("."):
            data = data[_]

        return data


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
