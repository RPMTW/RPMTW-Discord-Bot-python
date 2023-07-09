class ChannelTypeError(TypeError):
    def __init__(self, channel_id: int, channel_type: str) -> None:
        super().__init__(f"Channel with id `{channel_id}` is not a {channel_type}")
