from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

from discord import Color, Embed, Message, TextChannel
from packages.cog_data import *

if TYPE_CHECKING:
    from core.bot import RPMBot


class LoggerCog(InitedCog):
    def __init__(self, bot: "RPMBot") -> None:
        super().__init__(bot)
        self.config = self.bot.config[
            f"constant.{'test' if self.bot.test else 'main'}.logger"
        ]
        self.event_config = None
        self.embed_config = {
            "delete": {"name": "刪除", "color": Color.red()},
            "edit": {"name": "修改", "color": Color.green()},
        }

    async def ensure_exist(self):
        await self.bot.wait_until_ready()
        if not self.event_config:
            self.event_config = {
                "msg": {"channel": self.bot.get_channel(self.config["msg"]["channel_id"])}
            }

    def embed_gen(self, type_: str, *msgs: Message):
        translated_type, color = self.embed_config[type_].values()
        msg = msgs[0]
        embed = Embed(
            title=f"訊息{translated_type}紀錄",
            description=f"{msg.author.mention}在{msg.channel.mention}{translated_type}了訊息",  # type: ignore
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
        await self.ensure_exist()
        channel: TextChannel = self.event_config["msg"]["channel"]  # type: ignore
        await channel.send(embed=self.embed_gen("delete", msg))
        logging.info(f"{msg.author} delete message:\n" f"\t{msg.content}")

    @InitedCog.listener()
    async def on_message_edit(self, before_msg: Message, after_msg: Message):
        await self.ensure_exist()
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


def setup(bot: "RPMBot"):
    bot.add_cog(LoggerCog(bot))
