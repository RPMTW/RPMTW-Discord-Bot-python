from typing import TYPE_CHECKING

from discord import Member, VoiceChannel, VoiceState, PermissionOverwrite
from packages.cog_data import *

if TYPE_CHECKING:
    from core.bot import RPMBot


class DynamicVoiceCog(InitedCog):
    def __init__(self, bot: "RPMBot") -> None:
        super().__init__(bot)

        self.voice_list: dict[str, int] = {}
        self.config = self.bot.config["constant.dynamic.voice"]
        self.main_channel: VoiceChannel = None  # type: ignore

    async def ensure_exist(self):
        await self.bot.wait_until_ready()
        if not self.main_channel:
            self.main_channel = self.bot.get_channel(self.config["main_channel_id"])  # type: ignore

    @InitedCog.listener()
    async def on_voice_state_update(
        self, member: Member, before: VoiceState, after: VoiceState
    ):
        if member.bot:
            return

        await self.ensure_exist()

        # leave/move from exclusive channel
        if (channel := self.voice_list.get(member.id)) and (_ := before.channel) and channel.id == _.id:
            del self.voice_list[member.id]
            await channel.delete()

        # join/move to main_channel
        if (channel := after.channel) and channel.id == self.main_channel.id:
            overwrites = {
                member: PermissionOverwrite(manage_roles=True, manage_channels=True),
                member.guild.default_role: PermissionOverwrite(priority_speaker=True),
                self.bot.user: PermissionOverwrite(priority_speaker=False)
            }
            self.voice_list[member.id] = await channel.category.create_voice_channel(f"{member.name}的頻道", overwrites=overwrites)


def setup(bot: "RPMBot"):
    bot.add_cog(DynamicVoiceCog(bot))
