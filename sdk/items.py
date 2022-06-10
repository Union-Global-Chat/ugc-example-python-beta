class Message:
    def __init__(self, data: dict):
        self.channel = Channel(data["channel"])
        self.author = User(data["author"])
        self.guild = Guild(data["guild"])
        self.content = data["message"]["content"]
        
    
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
        self.iconURL = data["iconURL"]
