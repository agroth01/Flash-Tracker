#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =================================================================
# Created by  : Alexander Groth
# Created Date: Wed May 22
# =================================================================
"""
This module implements a basic UI interface for the client to interact with the
program.
"""
# =================================================================
# Imports
# =================================================================
import keyboard
import os
import time
from threading import Thread
from .menus import MainMenu, CreateLobbyMenu

class UI:
    def __init__(self):
        self.current_menu = MainMenu()

        # register callback functions
        self.lobby_creation_callback = None

        # start a new thread to run the main loop of the UI
        Thread(target=self._main_loop).start()

    def _main_loop(self):
        while True:
            self._gather_input()

            if (self.current_menu.identifier == "main_menu"):
                self.current_menu.draw()

            elif (self.current_menu.identifier == "create_lobby_menu"):
                self.current_menu.draw()

                # entered a valid name
                if (self.current_menu.lobby_name != ""):

                    self.lobby_creation_callback(self.current_menu.lobby_name)

    def _gather_input(self):
        """
        Listen for various keyboard presses and call events corresponding to key pressed
        """
        if (keyboard.is_pressed('w') or keyboard.is_pressed('up')):
            self._on_navigation_up()
            time.sleep(0.05)

        if (keyboard.is_pressed("s") or keyboard.is_pressed('down')):
            self._on_navigation_down()
            time.sleep(0.05)

        if (keyboard.is_pressed('space') or keyboard.is_pressed('enter')):
            self._on_selection()
            time.sleep(0.05)

    def _on_navigation_up(self):
        """
        Called when the user either pressed (W) or (UP ARROW)
        """
        self.current_menu.decrement_line()

    def _on_navigation_down(self):
        """
        Called when the user either pressed (S) or (DOWN ARROW)
        """
        self.current_menu.increment_line()

    def _on_selection(self):
        """
        Called when the user either pressed (SPACE) or (ENTER)
        """
        if (self.current_menu.identifier == "main_menu"):
            if (self.current_menu.current_line_index == 0):
                self.current_menu = CreateLobbyMenu()

# debugging
if __name__ == "__main__":
    UI()
