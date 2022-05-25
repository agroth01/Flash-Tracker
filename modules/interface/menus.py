#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =================================================================
# Created by  : Alexander Groth
# Created Date: Wed May 22
# =================================================================
"""
This file contains all the various menus that the interface uses to control
application
"""
# =================================================================
# Imports
# =================================================================
import os

# base class for all the menus that ui uses
class Menu:
    def __init__(self):
        self.current_line_index = 0
        self.lines = []
        self.last_line_index = self.current_line_index
        self.identifier = "base_menu"

    def increment_line(self):
        if (self.current_line_index < len(self.lines) - 1):
            self.current_line_index += 1

    def decrement_line(self):
        if (self.current_line_index > 0):
            self.current_line_index -= 1

    def draw(self):
        if (self.has_changed()):
            self._draw_lines()

    def has_changed(self):
        if (self.current_line_index != self.last_line_index):
            self.last_line_index = self.current_line_index
            return True
        return False

    def _draw_lines(self):
        for i, line in enumerate(self.lines):
            if (i == self.current_line_index):
                print(f"{line}    <---")
            else:
                print(line)

    def _clear_screen(self):
        os.system("cls")

    def _title_bar(self):
        print("Flash Tracker v1.0")
        print("==================\n")

# the first menu that user will be prompted to interact with upon entering
class MainMenu(Menu):
    def __init__(self):
        super().__init__()

        self.identifier = "main_menu"
        self.lines = [
            "Create a new lobby    ",
            "Join an existing lobby",
            "Settings              "
        ]

        self._clear_screen()
        self._title_bar()
        self._draw_lines()

    def draw(self):
        if (self.has_changed()):
            self._clear_screen()
            self._title_bar()
            self._draw_lines()



class CreateLobbyMenu(Menu):
    def __init__(self):
        super().__init__()

        self.identifier = "create_lobby_menu"
        self.lobby_name = ""

    def draw(self):
        self._clear_screen()
        self._title_bar()
        print("Name of the lobby:")
        self.lobby_name = input("> ")
