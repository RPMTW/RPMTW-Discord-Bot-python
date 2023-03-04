from typing import TYPE_CHECKING

from discord import (
    CategoryChannel,
    Member,
    PermissionOverwrite,
    VoiceChannel,
    VoiceState,
)
from packages.cog_data import *

if TYPE_CHECKING:
    from core.bot import RPMTWBot


class DynamicVoiceCog(InitedCog):
    def __init__(self, bot: "RPMTWBot") -> None:
        super().__init__(bot)

        self.voice_mapping: dict[int, VoiceChannel] = {}
        self.config = self.bot.config[f"constant.{self.bot.stat}.dynamic.voice"]
        self.main_channel: VoiceChannel = None  # type: ignore

    async def ensure_exist(self):
        await self.bot.wait_until_ready()
        if not self.main_channel:
            self.main_channel = self.bot.get_channel(self.config["channel_id"])  # type: ignore

    @InitedCog.listener()
    async def on_voice_state_update(
        self, member: Member, before: VoiceState, after: VoiceState
    ):
        if member.bot:
            return

        await self.ensure_exist()

        # leave/move from exclusive channel
        if (
            (channel := self.voice_mapping.get(member.id))
            and (_ := before.channel)
            and channel.id == _.id
        ):
            del self.voice_mapping[member.id]
            await channel.delete()
            logging.info(f"{member} leave his/her exclusive channel(id={channel.id})")

        # join/move to main_channel
        if (channel := after.channel) and channel.id == self.main_channel.id:
            overwrites = {
                member: PermissionOverwrite(manage_roles=True, manage_channels=True),
                member.guild.default_role: PermissionOverwrite(priority_speaker=True),
                self.bot.user: PermissionOverwrite(priority_speaker=False),
            }
            self.voice_mapping[
                member.id
            ] = exclusive_channel = await channel.category.create_voice_channel(  # type: ignore
                f"{member.name}的頻道", overwrites=overwrites
            )
            await member.move_to(exclusive_channel)
            logging.info(
                f"{member} create his/her exclusive channel(id={exclusive_channel.id})"
            )

    @InitedCog.listener()
    async def on_ready(self):  # clear empty voice channel after restart
        logging.info("Try to clear empty dynamic voice channel")
        category: CategoryChannel = self.bot.get_channel(self.config["category_id"])  # type: ignore
        if category:
            for sub_channel in category.voice_channels:
                if (
                    sub_channel.id != self.config["channel_id"]
                    and not sub_channel.members
                ):
                    await sub_channel.delete()


def setup(bot: "RPMTWBot"):
    bot.add_cog(DynamicVoiceCog(bot))
