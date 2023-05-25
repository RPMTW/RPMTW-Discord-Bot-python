from typing import TYPE_CHECKING

from discord import Member, PermissionOverwrite, VoiceChannel, VoiceState
from exceptions import ChannelNotFoundError, ChannelTypeError
from packages.cog_data import *

if TYPE_CHECKING:
    from core.bot import RPMTWBot
    from discord import CategoryChannel, StageChannel


class DynamicVoiceCog(InitedCog):
    def __init__(self, bot: "RPMTWBot") -> None:
        super().__init__(bot)

        self.voice_mapping: "dict[int, VoiceChannel | StageChannel]" = {}
        self.main_channel = None  # type: ignore

    def get_main_voice_channel(self) -> VoiceChannel:
        if _ := self._maybe_none.get("channel_id"):
            return _

        if not (_ := self.bot.get_channel(channel_id := self.config["channel_id"])):
            raise ChannelNotFoundError(channel_id)

        if not isinstance(_, VoiceChannel):
            raise ChannelTypeError(channel_id, "VoiceChannel")

        self._maybe_none["channel_id"] = _
        return _

    def is_join_main(self, channel: "VoiceChannel | StageChannel"):
        """Is join main voice channel?

        ## Returns
        - True
            - When `channel` is the main voice channel
        - False
            - When `channel` is not the main voice channel
        """
        return channel.id == self.get_main_voice_channel().id

    def is_owner_leave(self, member: Member, channel: "VoiceChannel | StageChannel"):
        """Is owner leave from their exclusive voice channel?

        ## Returns
        - True
            - When `member` is the owner of `channel`
        - False
            - When `member` is not the owner of `channel`
        """
        if not (_ := self.voice_mapping.get(member.id)):
            return False
        return _.id == channel.id

    async def create_exclusive_voice_channel(self, member: Member):
        if not (category := self.get_main_voice_channel().category):
            raise ValueError("main voice channel must in a category")

        exclusive_channel = await category.create_voice_channel(
            f"{member.name}的頻道",
            overwrites={
                member: PermissionOverwrite(manage_roles=True, manage_channels=True),
                member.guild.default_role: PermissionOverwrite(priority_speaker=True),
                self.bot.user: PermissionOverwrite(priority_speaker=False),
            },
        )
        logging.info(
            f"Create exclusive channel(id={exclusive_channel.id}) for {member}(id={member.id})"
        )
        self.voice_mapping[member.id] = exclusive_channel

        return exclusive_channel

    async def delete_exclusive_voice_channel(
        self, member: Member, channel: "VoiceChannel | StageChannel"
    ):
        del self.voice_mapping[member.id]
        await channel.delete()
        logging.info(
            f"Delete exclusive channel(id={channel.id}) for {member}(id={member.id})"
        )

    async def on_voice_join(self, member: Member, channel: "VoiceChannel | StageChannel"):
        if self.is_join_main(channel):
            exclusive_channel = await self.create_exclusive_voice_channel(member)
            await member.move_to(exclusive_channel)

    async def on_voice_move(
        self,
        member: Member,
        before: "VoiceChannel | StageChannel",
        after: "VoiceChannel | StageChannel",
    ):
        if self.is_owner_leave(member, before) and self.is_join_main(after):
            await self.delete_exclusive_voice_channel(member, before)
            exclusive_channel = await self.create_exclusive_voice_channel(member)
            await member.move_to(exclusive_channel)

    async def on_voice_leave(
        self, member: Member, channel: "VoiceChannel | StageChannel"
    ):
        if self.is_owner_leave(member, channel):
            await self.delete_exclusive_voice_channel(member, channel)

    @InitedCog.listener()
    async def on_voice_state_update(
        self, member: Member, before: VoiceState, after: VoiceState
    ):
        if member.bot:
            return

        if not (before_channel := before.channel):
            assert (after_channel := after.channel)
            return await self.on_voice_join(member, after_channel)
        if not (after_channel := after.channel):
            return await self.on_voice_leave(member, before_channel)
        if before_channel.id != after_channel.id:
            return await self.on_voice_move(member, before_channel, after_channel)

        # other voice state update, such as deaf/undeaf/mute/unmute...
        # current nothing so just return None
        return None

    @InitedCog.listener()
    async def on_ready(self):  # clear empty voice channel after restart
        logging.info("Try to clear dynamic voice channel")
        category: CategoryChannel = self.bot.get_channel(self.config["category_id"])  # type: ignore
        if category:
            for sub_channel in category.voice_channels:
                if sub_channel.id != self.config["channel_id"]:
                    await sub_channel.delete()


def setup(bot: "RPMTWBot"):
    bot.add_cog(DynamicVoiceCog(bot))
