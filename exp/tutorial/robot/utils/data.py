#!/usr/bin/env python3

"""
Author:     jmdm
Date:       2022-12-30
OS:         macOS 12.6 (Monterey)
Hardware:   M1 chip

This code is provided "As Is"
"""

# Standard libraries
from dataclasses import dataclass


@dataclass
class Palette:
    """Color palette for plots

    See:
        - Palette 1: https://coolors.co/3a86ff-ff006e-ff9f1c-8338ec-00b84d
        - Palette 1 Darker: https://coolors.co/0046b8-b80050-cc7700-5811bb-008f3c
        - Palette 1 Light: https://coolors.co/70a7ff-ff70ae-ffc370-b98ff5-5cffa0
        - Palette 2: https://coolors.co/f0cf65-8980f5-51d6ff-ff5a5f-394053
    """

    # Basics
    BLACK: str = "#000000"
    WHITE: str = "#FFFFFF"
    R: str = "#FF0000"
    G: str = "#00FF00"
    B: str = "#0000FF"

    # Palette 1
    BLUE: str = "#3A86FF"
    PINK: str = "#FF006E"
    ORANGE: str = "#FF9F1C"
    PURPLE: str = "#8338EC"
    GREEN: str = "#00B84D"

    # Palette 1 Darker
    DARK_BLUE: str = "#0046B8"
    DARK_PINK: str = "#B80050"
    DARK_ORANGE: str = "#CC7700"
    DARK_PURPLE: str = "#5811BB"
    DARK_GREEN: str = "#008F3C"

    # Palette 1 (light)
    LIGHT_BLUE: str = "#70A7FF"
    LIGHT_PINK: str = "#FF70AE"
    LIGHT_ORANGE: str = "#FFC370"
    LIGHT_PURPLE: str = "#B98FF5"
    LIGHT_GREEN: str = "#5CFFA0"

    # Palette 2
    YELLOW: str = "#F0CF65"
    LILAC: str = "#8980F5"
    CYAN: str = "#51D6FF"
    RED: str = "#FF5A5F"
    GRAY: str = "#394053"


@dataclass
class ShellColours:
    """Color palette for printing in the terminal.

    See:
        - https://stackoverflow.com/questions/4842424/list-of-ansi-color-escape-sequences
        - https://stackoverflow.com/questions/287871/how-to-print-colored-text-to-the-terminal
    """

    # Colours
    green: str = "\033[92m"
    red: str = "\033[91m"
    yellow: str = "\033[93m"
    end: str = "\033[0m"
    gray: str = "\033[90m"
    cyan: str = "\033[95m"

    # Colours bolded
    green_em: str = "\033[92m\033[1m"
    red_em: str = "\033[91m\033[1m"
    yellow_em: str = "\033[93m\033[1m"
    gray_em: str = "\033[90m\033[1m"
    cyan_em: str = "\033[95m\033[1m"

    # Styles
    em: str = "\033[1m"  # bold
    ul: str = "\033[4m"  # underline
