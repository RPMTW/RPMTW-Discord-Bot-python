from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

from discord import Color, Embed, Message, TextChannel
from exceptions import ChannelNotFoundError, ChannelTypeError
from packages.cog_data import *

if TYPE_CHECKING:
    from core.bot import RPMTWBot


class LoggerCog(InitedCog):
    def __init__(self, bot: "RPMTWBot") -> None:
        super().__init__(bot)
        self.event_config = {
            "msg": {"channel": self.bot.get_channel(self.config["msg"]["channel_id"])}
        }
        self.embed_config = {
            "delete": {"name": "刪除", "color": Color.red()},
            "edit": {"name": "修改", "color": Color.yellow()},
        }

    def get_log_channel(self):
        if not (channel := self.bot.get_channel(self.config["msg"]["channel_id"])):
            raise ChannelNotFoundError(self.config["msg"]["channel_id"])

        if not isinstance(channel, TextChannel):
            raise ChannelTypeError(channel.id, "TextChannel")

        return channel

    def embed_gen(self, type_: str, *msgs: Message):
        translated_type, color = self.embed_config[type_].values()
        msg = msgs[0]
        embed = Embed(
            title=f"訊息{translated_type}紀錄",
            description=f"{msg.author.mention} 在 {msg.channel.mention} 的訊息被{translated_type}了",  # type: ignore
            color=color,
        ).set_footer(text=datetime.now(tz=timezone(timedelta(hours=8))).strftime(r"%A"))

        match type_:
            case "delete":
                embed.add_field(name=f"{translated_type}的訊息內文", value=msg.content)
            case "edit":
                embed.add_field(name="原始的訊息內文", value=msg.content).add_field(
                    name=f"{translated_type}的訊息內文", value=msgs[1].content
                )

        return embed

    @InitedCog.listener()
    async def on_message_delete(self, msg: Message):
        channel: TextChannel = self.event_config["msg"]["channel"]  # type: ignore
        await channel.send(embed=self.embed_gen("delete", msg))
        logging.info(f"{msg.author} delete message:\n" f"\t{msg.content}")

    @InitedCog.listener()
    async def on_message_edit(self, before_msg: Message, after_msg: Message):
        # on_messaege_edit will be call when a Message receives an update event(not only edit)
        # https://docs.pycord.dev/en/stable/api/events.html#discord.on_message_edit
        if before_msg.content == after_msg.content:
            return

        channel: TextChannel = self.event_config["msg"]["channel"]  # type: ignore
        await channel.send(embed=self.embed_gen("edit", before_msg, after_msg))
        logging.info(
            f"{before_msg.author}'s message have deleted\n"
            "origin message:\n"
            f"\t{before_msg.content}\n"
            "edited message:\n"
            f"\t{after_msg.content}"
        )

    @InitedCog.listener()
    async def on_application_command(self, ctx: ApplicationContext):
        logging.info(f"{ctx.author} used {ctx.command.name}")


def setup(bot: "RPMTWBot"):
    bot.add_cog(LoggerCog(bot))
