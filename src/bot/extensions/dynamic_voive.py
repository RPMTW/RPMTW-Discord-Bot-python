from typing import TYPE_CHECKING

from discord import Member, PermissionOverwrite, VoiceChannel, VoiceState
from discord.errors import HTTPException
from exceptions import ChannelTypeError
from packages.cog_data import *
from packages.default_data import bot_logger

if TYPE_CHECKING:
    from core.bot import RPMTWBot
    from discord import StageChannel


class DynamicVoiceCog(InitedCog):
    async def cog_load(self):
        await self.bot.wait_until_ready()

        if not (_ := self.bot.get_channel(channel_id := self.config["channel_id"])):
            raise ValueError("Channel id invalid")
        if not isinstance(_, VoiceChannel):
            raise ChannelTypeError(channel_id, "VoiceChannel")
        if not (category := _.category):
            raise ValueError("main voice channel must in a category")

        self.main_channel = _
        self.category = category

        bot_logger.info("Delete empty dynamic voice channel")

        for sub_channel in self.category.voice_channels:
            if sub_channel == self.main_channel:
                continue
            if not sub_channel.members:
                await sub_channel.delete()

    async def create_exclusive_voice_channel(self, member: Member):
        exclusive_channel = await self.category.create_voice_channel(
            f"{member.name}的頻道",
            overwrites={
                member: PermissionOverwrite(manage_channels=True),
                member.guild.default_role: PermissionOverwrite(priority_speaker=True),
                self.bot.user: PermissionOverwrite(priority_speaker=False),
            },
        )
        bot_logger.info(
            f"Create exclusive channel(id={exclusive_channel.id}) for {member}(id={member.id})"
        )
        return exclusive_channel

    async def delete_exclusive_voice_channel(
        self, member: Member, channel: "VoiceChannel | StageChannel"
    ):
        await channel.delete()
        bot_logger.info(
            f"Delete exclusive channel(id={channel.id}) for {member}(id={member.id})"
        )

    async def on_voice_join(self, member: Member, channel: "VoiceChannel | StageChannel"):
        if channel != self.main_channel:
            return

        exclusive_channel = await self.create_exclusive_voice_channel(member)

        # Moves fail when members join and leave the main channel very quickly
        try:
            await member.move_to(exclusive_channel)
        except HTTPException:
            await self.delete_exclusive_voice_channel(member, exclusive_channel)

    async def on_voice_leave(
        self, member: Member, channel: "VoiceChannel | StageChannel"
    ):
        # bot offline -> member join main_channel -> bot online -> member leave main_channel
        # maybe won't fix
        if channel == self.main_channel:
            return

        if not (members := channel.members) or all(member.bot for member in members):
            await self.delete_exclusive_voice_channel(member, channel)

    async def on_voice_move(
        self,
        member: Member,
        before: "VoiceChannel | StageChannel",
        after: "VoiceChannel | StageChannel",
    ):
        await self.on_voice_leave(member, before)
        await self.on_voice_join(member, after)

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
        # current nothing to do here so just return None
        return None


def setup(bot: "RPMTWBot"):
    bot.add_cog(DynamicVoiceCog(bot))
