#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =================================================================
# Created by  : Alexander Groth
# Created Date: Wed May 25
# =================================================================
"""
This module interfaces with the League of Legends live game API.
"""
# =================================================================
# Imports
# =================================================================
import requests
import urllib3

# =================================================================
# Constants
# =================================================================
API_URL = "https://127.0.0.1:2999/liveclientdata/allgamedata"
ICON_URL = "http://ddragon.leagueoflegends.com/cdn/12.10.1/img/champion/"
DEFAULT_TIMEOUT = 2

# =================================================================
# Public methods
# =================================================================
def live_game_active():
    """
    Makes an api request and look for the "GameStart" event in response.
    If the request times out or the event does not exist, return false.
    If event exists, return true
    """
    try:
        response = call_api(0.1)
        if (response.json()["events"]["Events"][0]["EventName"] == "GameStart"):
            return True
        else:
            return False
    except Exception as e:
        return False

def get_all_game_data():
    """
    Returns all the live data from the api in the json format.
    Live_game_active() should be called to verify that there is a game before using
    this method.
    """
    response = call_api()
    return response.json()

def get_all_players():
    """
    Returns all the players that is in the same live game as client
    """
    response = call_api().json()
    players = response["allPlayers"]
    player_list = []
    for player in players:
        player_list.append(player["summonerName"])
    return player_list

def get_all_enemies():
    """
    Returns all the players that is on the other team of the local player
    """
    response = call_api().json()
    summonerName = response["activePlayer"]["summonerName"]

    # load all teams
    blue_team = []
    red_team = []
    local_player = None
    for player in response["allPlayers"]:
        if (player["team"] == "ORDER"):
            blue_team.append(player)
        elif (player["team"] == "CHAOS"):
            red_team.append(player)

        if (player["summonerName"] == summonerName):
            local_player = player

    # determine enemy team based on what team has local player
    if (local_player in blue_team):
        return red_team
    elif (local_player in red_team):
        return blue_team


# =================================================================
# Private methods
# =================================================================
def call_api(timeout=DEFAULT_TIMEOUT):
    """
    Makes a request to the API and return the result as raw result.
    Return value should be converted into json by method calling this
    """
    response = requests.get(API_URL, verify=False, timeout=timeout)
    return response

# disable insecure warnings when calling the api without a certificate
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
