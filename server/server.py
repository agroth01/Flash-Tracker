import threading
import time
import argparse
import server_utils
from server_utils import NetworkMessage, Command, ServerCommands, MessageType
from datetime import datetime

# wrapper class for the socket module to easily interface with the created socket
class Socket:
    def __init__(self, host, port):
        import socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(1000)
        self.socket.setblocking(0)

    # create a separate thread to listen for connections.
    def accept_connections(self, connection_callback):
        self.accept_thread = threading.Thread(target=self._connection_listener,
                                              args=(connection_callback,)
                                              ).start()

    # listens for connections and returns new connection in callback
    def _connection_listener(self, callback):
        while True:
            try:
                c, a = self.socket.accept()
                if not c: continue
                callback(c, a)
            except BlockingIOError:
                pass

# class for keeping clients grouped together and only sending information to
# other clients in the same lobby.
class Lobby:
    def __init__(self, lobby_id, master_client, deletion_callback):
        self.id = lobby_id # identifier for lobby
        self.master_client = master_client # client that made lobby
        self.clients = [] # all clients currently in lobby
        self.deletion_callback = deletion_callback # function to be called when lobby is deleted

        # add master client to list of clients
        self.add_client(self.master_client)

    # adds the client to the lobby.
    # client_in_lobby() should already have been used to prevent duplicates
    def add_client(self, client):
        self.clients.append(client)
        client.current_lobby = self
        self.broadcast(client, f"{client.address} joined the lobby")

    # removes the client from client list.
    # will transfer ownership of lobby to next in list.
    # if there are no other clients in lobby to transfer ownership to,
    # lobby will close.
    def remove_client(self, client):
        self.clients.remove(client)

        # there are more clients in lobby
        if (len(self.clients) > 0):
            self.master_client = self.clients[0]

        # no other client in lobby
        else:
            self.deletion_callback(self)

    # sends a message to all the clients in the lobby except for the sender.
    def broadcast(self, sender, message):
        for client in self.clients:
            if (client != sender):
                client.send_message(MessageType.MESSAGE, message)

    # compares the client passed to method with all clients connected to this room.
    # return bool indicating whether client is found
    def client_in_lobby(self, client):
        if client in self.clients:
            return True
        return False

# class for interfacing with a connection
class Client:
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        self.current_lobby = None

    # starts a new loop to listen for messages from the client.
    # will trigger message callback when data is recieved.
    # calls disconnect_callback and exits loop when
    # encountering connection reset error.
    def start_listening(self, message_callback, disconnect_callback):
        while True:
            try:
                data = self.connection.recv(1024)
                if not data: continue
                message_callback(NetworkMessage(self, data))
            except ConnectionResetError:
                disconnect_callback(self)
                break
            except BlockingIOError:
                pass

    # sends a message to the client.
    # type of message distinguises from a server message and lobby message.
    # the data type of message content will also be send as prefix.
    # because message has different parts, using the char "|" in content will break server.
    def send_message(self, message_type, message_content):
        data_type = type(message_content).__name__
        message = str.encode(f"{message_type}|{data_type}|{message_content}")
        self.connection.send(message)

    # determines if the client is in a lobby and returns result as bool
    def in_lobby(self):
        if (self.current_lobby != None):
            return True
        return False

# main class for the server
class Server:
    def __init__(self, host, port, is_verbose=False):
        # set extra info flag
        self.verbose = is_verbose

        # create socket and start listening for connections
        self.socket = Socket(host, port)
        self.socket.accept_connections(self._on_new_connection)
        self._log(f"Created a socket on {(host, port)}")

        # create master list of all clients connected to the server
        self.client_list = []

        # create a list of all the lobbies currently active
        self.lobby_list = []

    # callback when a new connection is established to the socket
    # will create a new client object and start listening for messages on a new thread
    # stores the client in the master list
    def _on_new_connection(self, connection, address):
        self._log(f"Got a new connection from {address}")
        new_client = Client(connection, address)
        self.client_list.append(new_client)
        threading.Thread(target=new_client.start_listening,
                         args=(self._on_message, self._on_disconnect)).start()

    # called when a client has sent a message to the server.
    # all messages to be recieved from a client will be in the form of a command.
    # commands are in the format: COMMAND OPT_ARG1, OPT_ARG2, ...
    def _on_message(self, message):
        command = Command(message.content)

        # LOBBY LIST
        if (command.prefix == ServerCommands.LOBBY_LIST):
            self._log(f"{message.sender.address} requested lobby list")
            lobbies = []
            for lobby in self.lobby_list:
                lobbies.append(lobby.id)
            message.sender.send_message(MessageType.RESPONSE, lobbies)

        # LOBBY CREATION
        elif (command.prefix == ServerCommands.CREATE_LOBBY):
                lobby_id = command.args[0]
                if not (self._is_lobby(lobby_id)):
                    new_lobby = Lobby(lobby_id, message.sender, self._on_lobby_deletion)
                    self.lobby_list.append(new_lobby)
                    self._log(f"{message.sender.address} created lobby with id: {lobby_id}")
                    message.sender.send_message(MessageType.RESPONSE, True)

                # lobby already exists
                else:
                    error_message = f"{message.sender.address} failed to create lobby with id: {lobby_id}"
                    self._log(error_message)
                    message.sender.send_message(MessageType.RESPONSE, False)

        # LOBBY JOINING
        elif (command.prefix == ServerCommands.JOIN_LOBBY):
            lobby_id = command.args[0]
            if (self._is_lobby(lobby_id)):
                desired_lobby = self._get_lobby_by_id(lobby_id)

                # check that client is not already in the lobby
                if not (desired_lobby.client_in_lobby(message.sender)):
                    desired_lobby.add_client(message.sender)
                    self._log(f"{message.sender.address} joined lobby {lobby_id}")
                    message.sender.send_message(MessageType.RESPONSE, True)

                # client is already in the lobby
                else:
                    self._log(f"{message.sender.address} attempted to join lobby it's already in ({lobby_id})")
                    message.sender.send_message(MessageType.RESPONSE, False)

            # lobby does not exist
            else:
                self._log(f"{message.sender.address} attempted to join lobby that does not exist ({lobby_id})")
                message.sender.send_message(MessageType.RESPONSE, False)

        # LOBBY BROADCAST
        elif (command.prefix == ServerCommands.LOBBY_BROADCAST):
            msg = command.args[0]
            # make sure client is in a lobby
            if (message.sender.in_lobby()):
                message.sender.current_lobby.broadcast(message.sender, msg)
                self._log(f"{message.sender.address} broadcasted {msg} to lobby {message.sender.current_lobby.id}")
                message.sender.send_message(MessageType.RESPONSE, True)

            # client not in lobby
            else:
                self._log(f"{message.sender.address} tried to broadcast while not in lobby")
                message.sender.send_message(MessageType.RESPONSE, False)

        # UNKNOWN COMMAND
        else:
            message.sender.send_message(MessageType.RESPONSE, "unknown_command")
            self._log(f"{message.sender.address} requested unknown command: {command.prefix}")

    # called when a client has disconnected from server
    def _on_disconnect(self, client):
        self._log(f"{client.address} disconnected from server")

        # remove client from lobby if in one
        if (client.in_lobby()):
            client.current_lobby.remove_client(client)

        # remove client from master client list
        self.client_list.remove(client)

    # called when a lobby has no more clients in it
    def _on_lobby_deletion(self, lobby):
        self.lobby_list.remove(lobby)
        self._log(f'Lobby "{lobby.id}" has been deleted due to no clients in it')

    # prints the message to console if verbose is enabled.
    # stores log in output file on shutdown
    def _log(self, message):
        if (self.verbose):
            time = datetime.now().strftime("%H:%M:%S")
            print(f"[{time}]: {message}")

    # looks through all the active lobbies and determines if anyone has a
    # corresponding id.
    def _is_lobby(self, lobby_id):
        for lobby in self.lobby_list:
            if (lobby.id == lobby_id):
                return True
        return False

    # returns a reference to the lobby with the given id
    def _get_lobby_by_id(self, lobby_id):
        for lobby in self.lobby_list:
            if (lobby.id == lobby_id):
                return lobby

if __name__ == '__main__':
    # argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument('host', type=str, help="The address to listen on")
    parser.add_argument('port', type=int, help="The port to listen on")
    parser.add_argument('--verbal', action='store_true', help="Server logs more information")
    arguments = parser.parse_args()

    Server(arguments.host, arguments.port, arguments.verbal)
