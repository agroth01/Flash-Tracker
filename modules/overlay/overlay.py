#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =================================================================
# Created by  : Alexander Groth
# Created Date: Wed May 23
# =================================================================
"""
This module allows for the creation of an overlay to display information in the
game.
"""
# =================================================================
# Imports
# =================================================================
import tkinter as tkr
import screens

class Overlay:
    """
    Creates an overlay using tkinter.
    To make sure the window is an overlay, we use "-topmost" property
    """
    def __init__(self):
        self.root = tkr.Tk()

        # create title lable to display over the champion icons
        self.title_label = tkr.Label(
            self.root,
            text='Flash Tracker v1.0',
            font=('Consolas', '14'),
            fg='green3',
            bg='grey19'
        )
        self.title_label.config(anchor='center')
        self.title_label.pack()

        # setup geometry of the overlay
        self.root.overrideredirect(True)
        self.root.configure(background='red')
        self.root.lift()
        self.root.wm_attributes("-topmost", True)
        #self.root.wm_attributes("-transparentcolor", 'red')

        screen_size = screens.get_primary_size()
        w = int(screen_size[0] / 6)
        h = int(screen_size[1] / 12)
        x = int((screen_size[0] / 2) - w / 2) + int((screen_size[0] / 100))
        y = int((screen_size[1] / 2) - h * 4.75)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        self.add_champion("Azir")
        self.add_champion("Azir")

    def add_champion(self, champion):
        """
        Create a new label that loads the corresponding champion icon as image
        and displays a text over it
        """

        box = tkr.Canvas(self.root, width=self.root.winfo_width() / 5, height=self.root.winfo_height() / 5)
        icon = tkr.PhotoImage("res/Aatrox.png")
        box.pack()
        box.create_image(50, 10, image=icon, anchor=tkr.NW)


    def run(self):
        self.root.mainloop()

Overlay().run()
