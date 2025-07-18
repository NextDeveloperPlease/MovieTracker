import pygame as pg

class Button:
    def __init__(self, text, x, y, width, height, action=None):
        self.text = text
        self.rect = pg.Rect(x, y, width, height)
        self.action = action

    def draw(self, screen):
        pg.draw.rect(screen, (0, 0, 255), self.rect)
        font = pg.font.Font(None, 36)
        text_surface = font.render(self.text, True, (255, 255, 255))
        screen.blit(text_surface, (self.rect.x + 10, self.rect.y + 10))
    
    def update_pos(self, pos:tuple[int, int]):
        x,y = pos
        self.rect = pg.Rect(x,y, self.rect.width, self.rect.height)

    def is_clicked(self, pos:tuple[int, int], mouse_clicked:bool=False):
        return self.rect.collidepoint(pos) and self.action is not None and mouse_clicked