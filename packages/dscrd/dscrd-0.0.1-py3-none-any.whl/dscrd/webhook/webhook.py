import requests

class Webhook:
    def __init__(self, id: str, token: str):
        self.url = "https://discord.com/api/webhooks/"
        self.id = id
        self.token = token

    def send_message(self, message: str, username: str = None, avatar_url: str = None, tts: bool = False, embeds: list = None, allowed_mentions: dict = None, components: list = None):
        """
        Send a message to a webhook.
        message: str, the message to send (up to 2000 characters).
        username: str, the username override of the webhook.
        avatar_url: str, the avatar URL override of the webhook.
        tts: bool, whether the message is a text-to-speech message or not.
        embeds: list, list of embeds to send.
        allowed_mentions: dict, the allowed mentions of the message.
        components: list, list of components to send, requires an application-owned webhook.
        """
        data = {
            "content": message,
            "username": username,
            "avatar_url": avatar_url,
            "tts": tts,
            "embeds": embeds,
            "allowed_mentions": allowed_mentions,
            "components": components
        }
        return requests.post(self.url + self.id + "/" + self.token, json=data)
    

