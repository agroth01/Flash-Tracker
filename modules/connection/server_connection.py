#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =================================================================
# Created by  : Alexander Groth
# Created Date: Wed May 21
# =================================================================
"""
This module provides access to the master server to both manage messages across
multiple clients and the creation and joining of new lobbies on the master server.
"""
# =================================================================
# Imports
# =================================================================
import sys
import socket
from threading import Thread
from server.server_utils import MessageType

# class for communicating with the master server
class Server:
    def __init__(self, host, port):
        self.connected = False
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.socket.setblocking(0)
            self.connected = True
        except ConnectionRefusedError:
            print("connection timed out")

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
    def _listen(self, message_callback):
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
                if (message_type == MessageType.RESPONSE):
                    self.server_response = message_body

                elif (message_type == MessageType.MESSAGE):
                    message_callback(message_body)

            except BlockingIOError:
                pass

    # start a thread for listening for incoming messages
    def start_listening(self, message_callback):
        Thread(target=self._listen, args=(message_callback,)).start()

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
