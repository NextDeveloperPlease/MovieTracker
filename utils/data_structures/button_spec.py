import pygame as pg
from typing import Union, Callable, Optional
from utils.data_structures.movie import Movie
from utils.data_structures.showtime import Showtime
from utils.data_structures.seat import Seat

class ButtonSpec:
    def __init__(self,
                 label: str,
                 color: Optional[pg.Color] = None,
                 action: Optional[Callable] = None,
                 ):
        ''' Initializes a button specification.
            Args:
                label (str): The label for the button.
                color (Optional[pg.Color]): The color of the button. Defaults to None.
                action (Optional[Callable]): The action to perform when the button is clicked. Defaults to None.'''
        self.label = label
        self.color = color
        self.action = action