class Message:
    def __init__(self, data: dict):
        self.channel = Channel(data["channel"])
        
    
class Channel:
    def __init__(self, data: dict):
        self.id = data["id"]
        self.name = data["name"]
        
class User:
    def __init__(self, data: dict):
        self.name = data["username"]
        self.id = data["id"]
