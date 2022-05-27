#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =================================================================
# Created by  : Alexander Groth
# Created Date: Wed May 23
# =================================================================
"""
Create a window overlay to display information inside the game
"""
# =================================================================
# Imports
# =================================================================
import tkinter as tk
import modules.overlay.screens as screens
#import screens
from PIL import ImageTk, Image

def create_champion_image(champion, width, height):
    """
    Loads the correct image from resource folder based on champion name.
    Resizes it to the specified size and returns it as usable image for tkinter
    """
    # load image based on champion name
    champion = champion.capitalize()
    raw_image = Image.open(f"modules/overlay/res/{champion}.png")
    scaled_image = raw_image.resize((int(width), int(height)))

    # convert to tkinter format and return it
    image = ImageTk.PhotoImage(scaled_image)
    return image

class Overlay:
    """
    Creates a new window using tkinter.
    To make window stay on top of screen, we use "-topmost"
    """
    def __init__(self, width, height, x, y):
        # create main window
        self.root = tk.Tk()

        # calculate size of window based on screen size
        self.width = screens.width_unit() * width
        self.height = screens.height_unit() * height

        # configure the main window
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.configure(background='red')
        self.root.wm_attributes("-transparentcolor", 'red')
        self.root.lift()
        self.root.geometry(f"{int(self.width)}x{int(self.height)}+{x}+{y}")

        # create title lable to display over the champion icons
        self.title_label = tk.Label(
            self.root,
            text='Flash Tracker v1.0',
            font=('Consolas', '14'),
            fg='green3',
            bg='grey19'
        )
        #self.title_label.config(anchor='center')
        self.title_label.place(x=60, y=0)

        # add event listener for mouse clicks and move
        self.root.bind("<ButtonPress-1>", self.__on_grip_start)
        self.root.bind("<ButtonRelease-1>", self.__on_grip_stop)
        self.root.bind("<B1-Motion>", self.__on_grip_move)

        # initialize empty list of players to be added via main script
        self.players = []

    def start(self):
        self.root.mainloop()

    def add_player(self, champion, on_click):
        """
        Creates a new player object and adds it to list of players to be drawn.
        By default the box will be 1/6th of the main window width
        """
        # determine how many players have already been added, to calculate
        # positions of next window
        amount = len(self.players)
        desired_width = int(self.root.winfo_width() / 6)
        desired_height = int(self.root.winfo_height() / 6)
        x_increment = int(self.root.winfo_width() / 3.15)
        y_pos = int(self.root.winfo_height() / 3.5)
        desired_position = (x_increment * amount, y_pos)

        # if this is first to be added, set position to be 0
        if (amount == 0):
            desired_position = (0, desired_position[1])

        self.players.append(Player(self.root, desired_width, desired_height,
                                   desired_position[0], desired_position[1],
                                   champion, on_click))

    def __on_grip_start(self, event):
        "Called when the player presses mouse down on the main window"
        self.x = event.x
        self.y = event.y

    def __on_grip_stop(self, event):
        "Called when the player releases mouse over main window"
        self.x = None
        self.y = None

    def __on_grip_move(self, event):
        "Called when player is moving mouse around"
        dx = event.x - self.x
        dy = event.y - self.y
        x = self.root.winfo_x() + dx
        y = self.root.winfo_y() + dy
        self.root.geometry(f"+{x}+{y}")

class Player:
    """
    Canvas item to be added to the main overlay. Displays the champion icon
    with a number representing flash cooldown.
    """
    def __init__(self, window, width, height, x, y, champion, on_click):
        # create the actual canvas
        self.canvas = tk.Canvas(window, width=width, height=height)

        self.champion = champion

        # load image of champion based on name of champ
        self.canvas.configure(bg="black")
        self.image = create_champion_image(champion, width * 1.1, height * 1.1)
        self.canvas.create_image(18, 19, image=self.image)

        # create text label and set it to hidden by default
        self.cooldown = self.canvas.create_text(18, 19, text="0", fill="white", font=('Helvetica 15 bold'))

        # bind callback of clicking on icon
        self.canvas.bind("<Button-1>", lambda event, arg=champion: on_click(event, arg))

        # place the icon
        self.canvas.place(x=x, y=y)

    def set_text(self, time):
        self.canvas.itemconfig(self.cooldown, text=str(time))

def click(event, arg):
    print(arg)

if __name__ == "__main__":
    overlay = Overlay(1.5, 1, 50, 50)
    overlay.add_player("Aatrox", click)
    overlay.add_player("Aatrox", click)
    overlay.start()
