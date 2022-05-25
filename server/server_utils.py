# Contains multiple methods and classes for the server that is too
# small or simply makes the main script more organized by keeping them here.

class NetworkMessage:
    def __init__(self, sender, content):
        from datetime import datetime

        self.sender = sender
        self.content = content.decode('utf-8')
        self.time_stamp = datetime.now().strftime("%H:%M:%S")

class Command:
    def __init__(self, content):
        content = content.split(" ")
        self.prefix = content[0]
        self.args = content[1:]

class ServerCommands:
    LOBBY_LIST = "lobby_list"
    CREATE_LOBBY = "create_lobby"
    JOIN_LOBBY = "join_lobby"
    LOBBY_BROADCAST = "lobby_broadcast"

class MessageType:
    RESPONSE = "response"
    MESSAGE = "message"
