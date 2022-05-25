import socket
import time
import keyboard
import os
from threading import Thread
from src.server.server_utils import MessageType

# class for communicating with the master server
class Server:
    def __init__(self, host, port):
        print("Connecting to master server...")
        self.connected = False
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.socket.setblocking(0)
            self.connected = True
            time.sleep(0.1)
            print("Connection established!")
        except ConnectionRefusedError:
            print("Could not establish connection to master server!")

        self.server_response = None

    # takes a string and converts it into bytes and sends to master server
    def _send_message(self, message):
        self.socket.send(str.encode(message))

    # converts the message content into it's actual type specified by the
    # data type in message header.
    def _message_to_data(self, type, message):
        if (type == "list"):
            return message.strip("][").replace("'", "").split(', ')

        elif (type == "str"):
            return str(message)

        elif (type == "bool"):
            if (message == "True"):
                return True
            elif (message == "False"):
                return False

    # constantly listen for messages from the master server
    def start_listening(self, lobby_message_callback):
        while True:
            try:
                # only proceed if there is data sent
                message = self.socket.recv(1024).decode('utf8')
                if not message: continue

                # split message into list of strings
                message = message.split("|")

                # get info from message
                message_type = message[0]
                data_type = message[1]
                content = message[2]

                # create actual message body from data type and content
                message_body = self._message_to_data(data_type, content)

                # handle data based on message type
                if (message_type == MessageType.SERVER):
                    self.server_response = message_body

                elif (message_type == MessageType.LOBBY):
                    lobby_message_callback(message_body)

            except BlockingIOError:
                pass

    # sends a message to master server and only proceed when it recieves
    # a server response.
    def wait_for_server_response(self, message):
        self._send_message(message)

        # create a while loop that will keep looping until self.server_response
        # has a value.
        while self.server_response is None:
            pass

        # return the response and clear response variable
        response = self.server_response
        self.server_response = None
        return response

    # attempts to get the list of all lobbies from master server
    def get_lobby_list(self):
        response = self.wait_for_server_response("lobby_list")
        return response

    # attempts to create a new lobby on the master server.
    # expects a boolean value indicating success
    def create_lobby(self, lobby_id):
        success = self.wait_for_server_response(f"create_lobby {lobby_id}")
        return success

    # attempts to join a lobby with the given id
    # returns a boolean value indicating success
    def join_lobby(self, lobby_id):
        success = self.wait_for_server_response(f"join_lobby {lobby_id}")
        return success

    # attempts to broadcast message to lobby
    # returns a boolean value indicating success
    def broadcast(self, message):
        success = self.wait_for_server_response(f"lobby_broadcast {message}")
        return success

# main class for program
class FlashTracker:
    def __init__(self):
        # attempts to connect to server
        self.server = Server("127.0.0.1", 8000)

        # only proceed if successfully connected
        if (self.server.connected):
            Thread(target=self.server.start_listening,
                   args=(self._on_lobby_message,)).start()

            self.main_loop()

    # main application loop
    def main_loop(self):
        pass

    # called by the server class when a message from the lobby is recieved.
    # while server messages is handled in server class, lobby messages are meant
    # for updating flash across clients.
    def _on_lobby_message(self, message):
        print(f"recieved lobby message: {message}")

    # used for testing functionality only
    def dev(self):
        command = input("\n> ").split(" ")
        if (command[0] == "lobby_list"):
            lobby_list = self.server.get_lobby_list()
            for lobby in lobby_list:
                print(lobby)

        elif (command[0] == "create_lobby"):
            success = self.server.create_lobby(command[1])
            if (success):
                print("Created lobby")
            else:
                print("could not create lobby")

        elif (command[0] == "join_lobby"):
            success = self.server.join_lobby(command[1])
            if (success):
                print("joined lobby")
            else:
                print("could not join lobby")

        elif (command[0] == "broadcast"):
            success = self.server.broadcast(command[1])
            if (success):
                print("broadcasted successfully")
            else:
                print("could not broadcast")

if __name__ == "__main__":
    FlashTracker()
