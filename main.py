#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =================================================================
# Created by  : Alexander Groth
# Created Date: Wed May 20
# =================================================================
"""
This is the main entry point for the project and connects all the modules
into one coherent project that aims to synchronize flash cooldowns between
multiple clients in Leauge of Legends.
"""
# =================================================================
# Imports
# =================================================================
import time
import os
import modules.game.api as api
from modules.connection.server_connection import Server
from modules.overlay.overlay import Overlay

# =================================================================
# callbacks
# =================================================================
overlay = Overlay(1.5, 1, 50, 50)
all_enemies = []


def on_message(message):
    for enemy in all_enemies:
        if enemy.champion == message:
            enemy.flash_cooldown = 300

# create a connection to the master server and start listening for messages
server = Server("35.228.34.91", 3389)
server.start_listening(on_message)

#server.wait_for_server_response("join_lobby test_lobby")
# wait for the server to connect
while not server.connected:
    pass
print("Connected to master server!")

# wait for a league game to be active
while not api.live_game_active():
    pass
print("In a game")

# attempt to create a new lobby with all summoner names as id
lobby_id = ""
for player in api.get_all_players():
    lobby_id += player.replace(" ", "").replace("|", "")

create_success = server.wait_for_server_response(f"create_lobby {lobby_id}")

# if creation failed, someone else with the application already loaded into game
# join that lobby instead
if not (create_success):
    join = server.wait_for_server_response(f"join_lobby {lobby_id}")
    if (join):
        print("joined game lobby")
else:
    print("created new game lobby")


class Enemy:
    def __init__(self, champion):
        self.flash_cooldown = 0
        self.champion = champion

def on_click(event, arg):
    server.wait_for_server_response(f"lobby_broadcast {arg}")
    for enemy in all_enemies:
        if enemy.champion == arg:
            enemy.flash_cooldown = 300


for enemy in api.get_all_enemies():
    overlay.add_player(enemy["championName"], on_click)
    all_enemies.append(Enemy(enemy["championName"]))


# main loop
while True:
    start_time = time.time()
    overlay.root.update()

    # updating enemy
    for player in overlay.players:
        for enemy in all_enemies:
            if (enemy.champion == player.champion):
                player.set_text(int(enemy.flash_cooldown))

    # update flash cooldowns
    delta = time.time() - start_time
    for enemy in all_enemies:
        enemy.flash_cooldown -= delta
        if (enemy.flash_cooldown < 0):
            enemy.flash_cooldown = 0
