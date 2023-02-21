from datetime import datetime, timezone, timedelta

from discord import Message, Embed, Member, Color

from packages.cog_data import *


class LoggerCog(discord.Cog):
    def __init__(self, bot: Bot) -> None:
        super().__init__()
        self.bot: Bot = bot
        self.event_config = Config({
            "msg": {
                "channel": self.bot.get_channel(832849374395760660)
            }
        })
        self.embed_config = Config({
            "delete": {
                "name": "刪除",
                "color": Color.red()
            },
            "edit": {
                "name": "修改",
                "color": Color.green()
            }
        })
    
    async def send_msg_log_embed(self, type: str, msgs: list[Message]) -> Message:
        data = self.embed_config[type]
        embed = Embed(f'訊息{data.name}紀錄', 
                      description = f'{msgs[0].author.mention} 在 {msgs[0].channel.mention} {data.name}訊息',
                      color=data.color)
        embed.set_footer(datetime.now(tz=timezone(timedelta(hours=8))).strftime(r'%A'))
        match type:
            case 'delete':
                embed.add_field(name = f'{data.name}的訊息內文',
                                value = msgs[0].content)
            case 'edit':
                embed.add_field(name = '原始的訊息內文',
                                value = msgs[0].content)
                embed.add_field(name = f'{data.name}的訊息內文',
                                value = msgs[1].content)
        return await self.event_config.msg.send(embed=embed)
                
    
    @Cog.listener()
    async def on_message_delete(self, msg: Message):
        await self.send_msg_log_embed('delete', [msg])
        logging.info(f'{msg.author} delete message:\n'
                     f'\t{msg.content}')
    
    @Cog.listener()
    async def on_message_edit(self, before_msg: Message, after_msg: Message):
        await self.send_msg_log_embed('edit', [before_msg, after_msg])
        logging.info(f'{before_msg.author}\'s message have deleted\n'
                      'origin message:\n'
                     f'\t{before_msg.content}\n'
                      'edited message:\n'
                     f'\t{after_msg.content}')
    
    @Cog.listener()
    async def on_application_command(self, ctx: ApplicationContext):
        logging.info(f'{ctx.author} used {ctx.command.name}')


def setup(bot: Bot):
    bot.add_cog(LoggerCog(bot))