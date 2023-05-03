import logging

from discord import ApplicationContext, commands

logging.basicConfig(level=logging.INFO)
logging.getLogger("RPMTWBot").setLevel(logging.INFO)


__all__ = (
    "ApplicationContext",
    "commands",
    "Config",
)


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
