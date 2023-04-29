class Message:

    def __init__(self, data: dict, from_: str):
        self.data = data
        self.content = data["message"]["content"]
        self.source = from_
        self.channel = Channel(data["channel"])
        self.author = User(data["author"])
        self.guild = Guild(data["guild"])

        self.attachments: list[Attachments] = []
        for a in data["message"]["attachments"]:
            self.attachments.append(Attachments(a))


class Attachments:

    def __init__(self, data: dict):
        self.url = data["url"]
        self.name = data["name"]
        self.width = data["width"]
        self.height = data["height"]
        self.content_type = data["content_type"]


class Channel:

    def __init__(self, data: dict):
        self.id = data["id"]
        self.name = data["name"]


class User:

    def __init__(self, data: dict):
        self.name = data["username"]
        self.id = data["id"]
        self.discriminator = data["discriminator"]
        self.avatar_url = data["avatarURL"]
        self.bot = data["bot"]


class Guild:

    def __init__(self, data: dict):
        self.id = data["id"]
        self.name = data["name"]
        self.icon_url = data["iconURL"]
