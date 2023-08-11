from dataclasses import dataclass

from disnake import Member, PermissionOverwrite, StageChannel, VoiceChannel, VoiceState
from disnake.errors import HTTPException
from lux import GeneralCog, Lux


@dataclass(frozen=True)
class Config:
    channel_id: int


class DynamicVoice(GeneralCog):
    config: Config

    async def cog_load(self):
        await self.bot.wait_until_ready()

        if not (main_channel := self.bot.get_channel(self.config.channel_id)):
            return self.logger.error("Channel id invalid")
        if not isinstance(main_channel, VoiceChannel):
            return self.logger.error("Channel type incorrect")
        if not (category := main_channel.category):
            return self.logger.error("Main channel must in a category")

        self.main_channel = main_channel
        self.category = category
        self.logger.info("Deleting empty dynamic voice channel")

        for sub_channel in self.category.voice_channels:
            if sub_channel == self.main_channel:
                continue
            if not sub_channel.members:
                await sub_channel.delete()

        self.logger.info("Deleted empty dynamic voice channel")

    async def create_voice_channel(self, member: Member):
        exclusive_channel = await self.category.create_voice_channel(
            f"{member.name}的頻道",
            overwrites={
                member: PermissionOverwrite(manage_channels=True),
                member.guild.default_role: PermissionOverwrite(priority_speaker=True),
                self.bot.user: PermissionOverwrite(priority_speaker=False),
            },
            reason=self.qualified_name,
        )
        self.logger.info(f"Created voice channel(id={exclusive_channel.id}) for {member}(id={member.id})")
        return exclusive_channel

    async def delete_voice_channel(self, member: Member, channel: VoiceChannel | StageChannel):
        await channel.delete(reason=self.qualified_name)
        self.logger.info(f"Deleted voice channel(id={channel.id}) for {member}(id={member.id})")

    async def on_voice_join(self, member: Member, channel: "VoiceChannel | StageChannel"):
        if channel != self.main_channel:
            return

        exclusive_channel = await self.create_voice_channel(member)

        # Moves fail when members join and leave the main channel very quickly
        try:
            await member.move_to(exclusive_channel)
        except HTTPException:
            await self.delete_voice_channel(member, exclusive_channel)

    async def on_voice_leave(self, member: Member, channel: "VoiceChannel | StageChannel"):
        # bot offline -> member join main_channel -> bot online -> member leave main_channel
        # maybe won't fix
        if channel == self.main_channel:
            return

        if not (members := channel.members) or all(member.bot for member in members):
            await self.delete_voice_channel(member, channel)

    async def on_voice_move(
        self,
        member: Member,
        before: "VoiceChannel | StageChannel",
        after: "VoiceChannel | StageChannel",
    ):
        await self.on_voice_leave(member, before)
        await self.on_voice_join(member, after)

    @GeneralCog.listener()
    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState):
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


def setup(bot: Lux):
    bot.add_cog(DynamicVoice())
