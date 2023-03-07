class IDNotFoundError(ValueError):
    """Base exception that is raised when a bot.get_xxx(eg: bot.get_channel) method return None"""

    def __init__(self, type_: str, id_: int) -> None:
        super().__init__(
            f"Cannot find {type_} with id `{id_}`, maybe {type_} not exist or bot isn't ready?"
        )


class ChannelNotFoundError(IDNotFoundError):
    def __init__(self, channel_id: int) -> None:
        super().__init__("channel", channel_id)


class ChannelTypeError(TypeError):
    def __init__(self, channel_id: int, channel_type: str) -> None:
        super().__init__(f"Channel with id `{channel_id}` is not a {channel_type}")


class HasNoWebhookError(ValueError):
    def __init__(self, channel_id: int) -> None:
        super().__init__(f"Channel with id `{channel_id}` has no webhook(s)")


class GuildNotFoundError(IDNotFoundError):
    def __init__(self, guild_id: int) -> None:
        super().__init__("guild", guild_id)
