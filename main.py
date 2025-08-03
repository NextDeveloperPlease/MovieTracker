from utils.managers import ContentManager, DisplayManager
import logging
import pygame as pg
from utils.settings_utils import Settings
from utils.display_mode import DisplayMode


def check_events():
    ''' Checks for events like quitting the application '''
    global running, display_mode, content_manager, display_manager
    button_was_pressed = False
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                running = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            pos = pg.mouse.get_pos()
            button_was_pressed = content_manager.check_button_pressed(pos)
    return button_was_pressed
                        
def main():
    global screen, running, content_manager, display_manager, display_mode
    while running:
        screen.fill(pg.Color('black'))
        button_was_pressed = check_events()
        if button_was_pressed:
            display_manager.update_header(content_manager.get_selections())
            display_manager.update_buttons(content_manager.get_buttons())
        display_manager.display(screen, content_manager.get_display_mode())
        pg.display.flip()
        

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    SETTINGS = Settings() #TODO: Add path logic here
    SCREEN_WIDTH = SETTINGS.get('res_width')
    SCREEN_HEIGHT = SETTINGS.get('res_height')
    BASE_URL = "https://www.cinemark.com"
    
    pg.init()
    pg.display.set_caption("Movie Seat Selection")
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    display_mode = DisplayMode.MOVIE
    running = True
    
    content_manager = ContentManager(BASE_URL)
    buttons = content_manager.get_buttons()
    display_manager = DisplayManager(buttons)

    main()