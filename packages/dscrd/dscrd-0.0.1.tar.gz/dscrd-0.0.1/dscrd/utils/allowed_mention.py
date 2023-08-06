def create_allowed_mentions(parse: list = [], roles: list = [], users: list = [], replied_user: bool = False):
    """
    Create an allowed mention object.
    parse: list, list of allowed mentions types ("users", "roles" and "everyone" are the types)
    roles: list, list of role_ids to allow
    users: list, list of user_ids to allow
    replied_user: bool, whether mention the author of the message replied to (default: False)
    """
    allowed_mentions = {
        "parse": parse,
        "roles": roles,
        "users": users,
        "replied_user": replied_user
    }
    return allowed_mentions