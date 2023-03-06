import logging

import discord
from discord import ApplicationContext, Bot, commands

logging.basicConfig(level=logging.INFO)


class Config:
    def __init__(self, data: dict) -> None:
        self.data = data

    def __getitem__(self, key: str):
        """
        `key`: dot split keys,
            eg: `data = {"key": {"sub_key": value}}`

            use `value = Config(data)["key.sub_key"]` to get value
        """
        data = self.data
        for _ in key.split("."):
            data = data[_]

        return data


__all__ = [
    "logging",
    "discord",
    "ApplicationContext",
    "Bot",
    "commands",
    "Config",
]
