from aiohttp import ClientSession, ContentTypeError
from lux import AppCmdInter, GeneralCog, Lux, send_ephemeral, slash_command


class Tool(GeneralCog):
    def __init__(self) -> None:
        super().__init__()
        self.status_endpoint = "https://api.rpmtw.com:2096/universe-chat/info"

    async def cog_load(self) -> None:
        await self.bot.wait_until_ready()

        if not (siongsng := self.bot.get_user(645588343228334080)):
            return self.logger.error("Invalid user id")

        self.siongsng = siongsng

    @slash_command()
    async def check_uchat_status(self, inter: AppCmdInter):
        async with ClientSession() as session:
            async with session.get(self.status_endpoint) as response:
                try:
                    content = await response.json()
                except ContentTypeError:
                    content = None

        if content is None:
            return await inter.send(f"{self.siongsng.mention}！宇宙通訊伺服器掛了！")
        await send_ephemeral(content)


def setup(bot: Lux):
    bot.add_cog(Tool())
