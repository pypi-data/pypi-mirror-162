def create_embed(title: str = "", type: str = "rich", description: str = "", url: str="", timestamp: str = "", color: int = 0, footer: dict = {}, image: dict = {}, thumbnail: dict = {}, video: dict = {}, provider: dict = {}, author: dict = {}, fields: list = []):
    """
    Create an embed object.
    title: str, title of the embed
    type: str, type of the embed (always "rich" for webhooks)
    description: str, description of the embed
    url: str, url of the embed
    timestamp: ISO8601 timestamp of the embed
    color: int, color code of the embed
    footer: embed footer object, footer information
    image: embed image object, image information
    thumbnail: embed thumbnail object, thumbnail information
    video: embed video object, video information
    provider: embed provider object, provider information
    author: embed author object, author information
    fields: list of embed field objects, fields information
    """
    embed = {
        "title": title,
        "type": type,
        "description": description,
        "url": url,
        "timestamp": timestamp,
        "color": color,
        "footer": footer,
        "image": image,
        "thumbnail": thumbnail,
        "video": video,
        "provider": provider,
        "author": author,
        "fields": fields
    }
    return embed


def create_embed_footer(text: str = "", icon_url: str = "", proxy_icon_url: str = ""):
    """
    Create a footer object.
    text: str, text of the footer
    icon_url: str, icon url of the footer (only http(s) and attachment(s))
    proxy_icon_url: str, proxy icon url of the footer
    """
    footer = {
        "text": text,
        "icon_url": icon_url,
        "proxy_icon_url": proxy_icon_url
    }
    return footer


def create_embed_image(url: str = "", proxy_url: str = "", height: int = 0, width: int = 0):
    """
    Create an image object.
    url: str, url of the image (only http(s) and attachment(s))
    proxy_url: str, proxy url of the image
    height: int, height of the image
    width: int, width of the image
    """
    image = {
        "url": url,
        "proxy_url": proxy_url,
        "height": height,
        "width": width
    }
    return image


def create_embed_thumbnail(url: str = "", proxy_url: str = "", height: int = 0, width: int = 0):
    """
    Create a thumbnail object.
    url: str, url of the thumbnail (only http(s) and attachment(s))
    proxy_url: str, proxy url of the thumbnail
    height: int, height of the thumbnail
    width: int, width of the thumbnail
    """
    thumbnail = {
        "url": url,
        "proxy_url": proxy_url,
        "height": height,
        "width": width
    }
    return thumbnail


def create_embed_video(url: str = "", proxy_url: str = "", height: int = 0, width: int = 0):
    """
    Create a video object.
    url: str, source url of the video
    proxy_url: str, proxy url of the video
    height: int, height of the video
    width: int, width of the video
    """
    video = {
        "url": url,
        "proxy_url": proxy_url,
        "height": height,
        "width": width
    }
    return video


def create_embed_provider(name: str = "", url: str = ""):
    """
    Create a provider object.
    name: str, name of the provider
    url: str, url of the provider
    """
    provider = {
        "name": name,
        "url": url
    }
    return provider


def create_embed_author(name: str = "", url: str = "", icon_url: str = "", proxy_icon_url: str = ""):
    """
    Create an author object.
    name: str, name of the author
    url: str, url of the author
    icon_url: str, icon url of the author (only http(s) and attachment(s))
    proxy_icon_url: str, proxy icon url of the author
    """
    author = {
        "name": name,
        "url": url,
        "icon_url": icon_url,
        "proxy_icon_url": proxy_icon_url
    }
    return author


def create_embed_field(name: str = "", value: str = str, inline: bool = True):
    """
    Create a field object.
    name: str, name of the field
    value: str, value of the field
    inline: bool, whether the field is inline or not
    """
    field = {
        "name": name,
        "value": value,
        "inline": inline
    }
    return field