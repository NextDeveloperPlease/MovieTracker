import pygame as pg

class Button:
    def __init__(self, text, x, y, width, height, color=(0, 0, 255), action=None):
        self.text = text
        self.rect = pg.Rect(x, y, width, height)
        self.color = color
        self.action = action

    def draw(self, screen:pg.Surface, font:pg.font.Font = None):
        """Draw the button on the given Pygame screen."""
        if font is None:
            self.font = pg.font.Font(None, 36)
        else:
            self.font = font
        pg.draw.rect(screen, self.color, self.rect)
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        # Center the text on the button (text_surface is used to center the center of the text, not the top left corner)
        screen.blit(text_surface, (self.rect.x + self.rect.width/2 - text_surface.get_width()/2, self.rect.y + self.rect.height/2 - text_surface.get_height()/2))

    def update_color(self, color=None):
        if color:
            self.color = color
            
    def update_pos(self, pos:tuple[int, int]):
        x,y = pos
        self.rect = pg.Rect(x,y, self.rect.width, self.rect.height)

    def is_hovered(self, pos:tuple[int, int]):
        return self.rect.collidepoint(pos) and self.action is not None