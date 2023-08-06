def create_partial_emoji(id: str = "", name: str = "", animated: bool = False):
    """
    Create a partial emoji.
    id: str, the id of the emoji
    name: str, the name of the emoji
    animated: bool, whether the emoji is animated or not
    """
    partial_emoji = {
        "id": id,
        "name": name,
        "animated": animated
    }
    return partial_emoji