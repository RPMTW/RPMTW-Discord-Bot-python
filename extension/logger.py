from collections import namedtuple
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Union

from disnake import Color, Embed, Message, StageChannel, TextChannel, Thread, VoiceChannel
from lux import AppCmdInter, GeneralCog, Lux

GuildMessageable = Union[TextChannel, Thread, VoiceChannel, StageChannel]


@dataclass
class Config:
    channel_id: int


EmbedConfig = namedtuple("EmbedConfig", ["action", "color"])


class EmbedType(Enum):
    delete = EmbedConfig("刪除", Color.red())
    edit = EmbedConfig("修改", Color.yellow())


class Logger(GeneralCog):
    config: Config

    async def cog_load(self):
        await self.bot.wait_until_ready()

        if not (channel := self.bot.get_channel(self.config.channel_id)):
            return self.logger.error("Channel id invalid")
        if not isinstance(channel, TextChannel):
            return self.logger.error("Channel type invalid")

        self.channel = channel

    def generate_embed(self, type_: EmbedType, before: Message, after: Message | None = None):
        try:
            assert isinstance(before.channel, GuildMessageable)
        except AssertionError as e:
            return self.logger.exception(f"{before.channel} is not a GuildMessageable", exc_info=e)

        config = type_.value
        action = config.action
        embed = Embed(
            title=f"訊息{action}紀錄",
            description=f"{before.author.mention} 在 {before.channel.mention} 的訊息被{action}了",
            color=config.color,
        ).set_footer(text=datetime.now(tz=timezone(timedelta(hours=8))).strftime(r"%A"))

        match type_:
            case EmbedType.delete:
                embed.add_field(name=f"{action}的訊息內文", value=before.content)
            case EmbedType.edit:
                assert after is not None
                embed.add_field(name="原始的訊息內文", value=before.content).add_field(
                    name=f"{action}的訊息內文", value=after.content
                )

        return embed

    @GeneralCog.listener()
    async def on_message_delete(self, message: Message):
        if not message.guild:
            return

        self.logger.info(f"{message.author} deleted a message:\n" f"\t{message.content}")

        if embed := self.generate_embed(EmbedType.delete, message):
            await self.channel.send(embed=embed)

    @GeneralCog.listener()
    async def on_message_edit(self, before: Message, after: Message):
        # Note: If the message is not found in the internal message cache, then these events will not be called.
        # Note: Not only edit will trigger this event, but also
        # - pin/unpin
        # - received embed
        # - embed suppressed/unsuppressed
        # - ...
        # More detail: https://docs.disnake.dev/en/stable/api/events.html#disnake.on_message_edit
        if before.content == after.content or not before.guild:
            return

        self.logger.info(
            f"""{before.author}'s message have edited
original:
    {before.content}
after:
    {after.content}
"""
        )

        if embed := self.generate_embed(EmbedType.edit, before, after):
            await self.channel.send(embed=embed)

    @GeneralCog.listener()
    async def on_application_command(self, inter: AppCmdInter):
        self.logger.info(f"{inter.author} used '{inter.application_command.name}' command")


def setup(bot: Lux):
    bot.add_cog(Logger())
