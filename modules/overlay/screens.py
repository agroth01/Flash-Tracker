#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =================================================================
# Created by  : Alexander Groth
# Created Date: Wed May 23
# =================================================================
"""
Handling of variying screen size and amounts
"""
# =================================================================
# Imports
# =================================================================
import screeninfo

# =================================================================
# Public methods
# =================================================================
def get_primary_monitor():
    """
    Uses the screeninfo module to get all screens available and returns
    the one marked as primary monitor
    """
    for monitor in screeninfo.get_monitors():
        if (monitor.is_primary):
            return monitor

def get_primary_size():
    """
    Returns the size of the primary monitor as a touple in the format
    (width, height)
    """
    primary = get_primary_monitor()
    return (primary.width, primary.height)

def width_unit():
    """
    Returns the width of the screen divided by 10, so the scales used when
    settings size of the overlay is consistent with the size of screen
    """
    primary_width = int(get_primary_monitor().width / 10)
    return primary_width

def height_unit():
    """
    Returns the height of the screen divided by 10, so the scales used when
    settings size of the overlay is consistent with the size of screen
    """
    primary_height = int(get_primary_monitor().height / 10)
    return primary_height
