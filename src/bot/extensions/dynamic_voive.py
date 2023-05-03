from discord import (
    CategoryChannel,
    Member,
    PermissionOverwrite,
    VoiceChannel,
    VoiceState,
)

from exceptions import ChannelNotFoundError, ChannelTypeError
from packages import InitedCog, RPMTWBot


class DynamicVoiceCog(InitedCog):
    def __init__(self, bot: "RPMTWBot") -> None:
        super().__init__(bot)

        self.voice_mapping: dict[int, VoiceChannel] = {}

    def get_voice_channel(self) -> VoiceChannel:
        if _ := self._maybe_none.get("channel_id"):
            return _

        if not (_ := self.bot.get_channel(channel_id := self.config["channel_id"])):
            raise ChannelNotFoundError(channel_id)

        if not isinstance(_, VoiceChannel):
            raise ChannelTypeError(channel_id, "VoiceChannel")

        self._maybe_none["channel_id"] = _
        return _

    @InitedCog.listener()
    async def on_voice_state_update(
        self,
        member: Member,
        before: VoiceState,
        after: VoiceState,
    ):
        if member.bot:
            return

        # leave/move from exclusive channel
        if (
            (channel := self.voice_mapping.get(member.id))
            and (_ := before.channel)
            and channel.id == _.id
        ):
            del self.voice_mapping[member.id]
            await channel.delete()
            self.log.info(f"{member} leave his/her exclusive channel(id={channel.id})")

        # join/move to main_channel
        if (channel := after.channel) and channel.id == self.get_voice_channel().id:
            overwrites = {
                member: PermissionOverwrite(manage_roles=True, manage_channels=True),
                member.guild.default_role: PermissionOverwrite(priority_speaker=True),
                self.bot.user: PermissionOverwrite(priority_speaker=False),
            }
            exclusive_channel = await channel.category.create_voice_channel(
                f"{member.name}的頻道", overwrites=overwrites
            )
            self.voice_mapping[member.id] = exclusive_channel
            await member.move_to(exclusive_channel)
            self.log.info(
                f"{member} create his/her exclusive channel(id={exclusive_channel.id})"
            )

    @InitedCog.listener()
    async def on_ready(self):  # clear empty voice channel after restart
        self.log.info("Try to clear empty dynamic voice channel")

        category: CategoryChannel = self.bot.get_channel(self.config["category_id"])
        if category:
            for sub_channel in category.voice_channels:
                if (
                    sub_channel.id != self.config["channel_id"]
                    and not sub_channel.members
                ):
                    await sub_channel.delete()


def setup(bot: "RPMTWBot"):
    bot.add_cog(DynamicVoiceCog(bot))
