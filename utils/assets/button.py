from typing import Tuple
import pygame as pg

class Button:
    def __init__(self, text, x, y, width, height, color=(0, 0, 255), action=None): # TODO: Add a hover color
        '''Initializes a button with the given parameters.
            Args:
                text (str): The text to display on the button.
                x (int): The x-coordinate of the button.
                y (int): The y-coordinate of the button.
                width (int): The width of the button.
                height (int): The height of the button.
                color (tuple): The color of the button in RGB format. Defaults to blue.
                action (callable): The action to perform when the button is clicked. Defaults to None.
        '''
        self.text = text
        self.rect = pg.Rect(x, y, width, height)
        self.color = color
        self.action = action

    def draw(self, screen:pg.Surface, font:pg.font.Font = None):
        """Draw the button on the given Pygame screen.
            Args:
                screen (pg.Surface): The Pygame surface to draw the button on.
                font (pg.font.Font): The font to use for the button text. Defaults to None, which uses the default font.
        """
        if font is None:
            self.font = pg.font.Font(None, 36)
        else:
            self.font = font
        pg.draw.rect(screen, self.color, self.rect)
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        # Center the text on the button (text_surface is used to center the center of the text, not the top left corner)
        screen.blit(text_surface, (self.rect.x + self.rect.width/2 - text_surface.get_width()/2, self.rect.y + self.rect.height/2 - text_surface.get_height()/2))

    def update_color(self, color=None):
        ''' Updates the color of the button.
            Args:
                color (tuple): The new color of the button in RGB format. If None, it does not change the color.
        '''
        if color:
            self.color = color
    
    def get_color(self) -> Tuple[int,int,int]:
        return self.color
            
    def update_pos(self, pos:tuple[int, int]):
        ''' Updates the position of the button.
            Args:
                pos (tuple): The new position of the button as (x, y).
        '''
        x,y = pos
        self.rect = pg.Rect(x,y, self.rect.width, self.rect.height)

    def is_hovered(self, pos:tuple[int, int]): # TODO: Change the color if the button is hovered
        ''' Checks if the button is hovered by the mouse.
            Args:
                pos (tuple): The position of the mouse as (x, y).
            Returns:
                bool: True if the button is hovered, False otherwise.
        '''
        return self.rect.collidepoint(pos) and self.action is not None