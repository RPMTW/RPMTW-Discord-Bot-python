from typing import TYPE_CHECKING

from discord import Member, VoiceState
from packages.cog_data import *

if TYPE_CHECKING:
    from core.bot import RPMBot


class DynamicVoiceCog(InitedCog):
    def __init__(self, bot: "RPMBot") -> None:
        super().__init__(bot)

        self.voice_list: dict[str, int] = {}
        self.config = self.bot.config["constant.dynamic.voice"]
        self.main_channel = self.bot.get_channel(self.config["main_channel_id"])

    @InitedCog.listener()
    async def on_voice_state_update(
        self, member: Member, before: VoiceState, after: VoiceState
    ):
        """
        #? join
        1. a join main_channel
        2. create new_channel
        3. move a into new_channel

        #? leave
        1. a leave new_channel
        2. delete new_channel
        """
        ...


def setup(bot: "RPMBot"):
    bot.add_cog(DynamicVoiceCog(bot))
