def create_message_reference(message_id: str = "", channel_id: str = "", guild_id: str = "", fail_if_not_exists: bool = True) -> dict:
    """
    Create a message reference.
    message_id: snowflake, the message ID of the originating message.
    channel_id: snowflake, the channel ID of the originating message.
    guild_id: snowflake, the guild ID of the originating message.
    fail_if_not_exists: bool, whether to error if the message doesn't exists or to send the message as normal (default: True).
    """
    message_reference = {
        "message_id": message_id,
        "channel_id": channel_id,
        "guild_id": guild_id,
        "fail_if_not_exists": fail_if_not_exists
    }
    return message_reference


