import re
from typing import List, Dict, Optional, Tuple, Union
import requests
import logging
import time
import sys
import pygame as pg
from utils.managers.seat_manager import SeatManager
from utils.misc.display_mode import DisplayMode, update_display_mode
from settings.settings_utils import Settings
from utils.managers.showtime_manager import ShowtimeManager
from utils.managers.movie_manager import MovieManager
from utils.data_structures.button_spec import ButtonSpec
from utils.misc.utils import is_list_objects, validate_button_specs, convert_button_index_to_position, button_generation_from_specs

from bs4 import BeautifulSoup
# from utils.button import Button
# from utils.movie import Movie
# from utils.showtime import Showtime

from utils.assets.button import Button
from utils.data_structures.movie import Movie
from utils.data_structures.showtime import Showtime
from utils.data_structures.seat import Seat

#from utils.seat import Seat
# from utils.display_mode import DisplayMode
from enum import Enum

import pygame as pg

class DisplayObjectType(Enum):
    ''' Enum for different display object types. Used to determine the number of columns for button generation. '''
    
    MOVIE = "movie_col"
    SHOWTIME = "showtime_col"
    SEAT = "seat_col"

class DisplayManager:
    '''
        Manager class that handles the display of buttons and headers.
        It uses the button specifications to generate buttons and display them on the screen.
        It also handles the header display with current date and display mode.
    '''
    WHITE = pg.Color('white')
    
    def __init__(self, button_specs:Dict[str, Union[List[ButtonSpec], Dict[str, Union[type, int]]]]):
        ''' Initializes the DisplayManager with button specifications.
            Args:
                button_specs (Dict[str, Union[List[ButtonSpec], Dict[str, Union[type, int]]]]): The button specifications to be used for generating buttons.
        '''
        self.settings = Settings()
        self.default_color = self.settings.get('default_button_color')
        self.selected_seat_color = self.settings.get('default_seat_selected_color')
        self.hover_color = self.settings.get('default_button_hover_color')
        self.default_seat_color = self.settings.get('default_seat_color')
        self.default_unavailable_seat_color = self.settings.get('default_seat_unavailable_color')
        
        self.selected_movie:Movie = None
        self.selected_showtime:Showtime = None
        self.selected_seats = {}
        self.display_buttons: List[Button] = []
        self.switch_to_notifications = False
        self.continue_button = None
        
        if validate_button_specs(button_specs):
            self.update_buttons(button_specs)
        else:
            logging.error(f'Invalid ButtonSpec Type: {button_specs}')
    
    def display_header(self, screen: pg.Surface, display_mode: DisplayMode):
        ''' Displays the header with current date and display mode '''
        font = pg.font.Font(None, 36)
        date_text = time.strftime("%Y-%m-%d %H:%M:%S")
        mode_text = ""
        match display_mode:
            case DisplayMode.MOVIE:
                mode_text = "Movies:"
            case DisplayMode.SHOWTIME:
                if not self.selected_movie:
                    mode_text = "Showtimes:"
                    logging.error("No movie selected for showtimes.")
                    return
                movie_edited = f"{self.selected_movie.title}'s"
                mode_text = f'{movie_edited} Showtimes:'
            case DisplayMode.SEAT:
                mode_text = "Seats:"
                if not self.continue_button:
                    self.continue_button = Button(
                        text='Next',
                        x=520,
                        y=100,
                        width=80,
                        height=100,
                        color=pg.Color('green'), # TODO: Make this variable. Next should be greyed out if the user hasn't entered a seat selection
                        action=self.next_screen) # TODO: Change magic number to distance from right side of the screen.
            case DisplayMode.NOTIFYING:
                mode_text = "Notification:"
        
        date_surface = font.render(date_text, True, self.WHITE)
        mode_surface = font.render(mode_text, True, self.WHITE)
        
        screen.blit(date_surface, (50, 100))
        screen.blit(mode_surface, (50, 150))

    def update_selected_content(self, selected_content:Tuple[Optional[Movie], Optional[Showtime], Optional[Seat]]):
        ''' Updates the saved content with the selected movie, showtime, and seat.
            Args:
                selected_content (Tuple[Optional[Movie], Optional[Showtime], Optional[Seat]]): The selected movie, showtime, and seat.
        '''

        logging.info(f'Updating selected content with movie: {selected_content[0]}, showtime: {selected_content[1]}, seat: {selected_content[2]}')
        logging.info(f'selected_movie variable type: {type(selected_content[0])}')
        logging.info(f'selected_showtime variable type: {type(selected_content[1])}')
        logging.info(f'selected_seat variable type: {type(selected_content[2])}')

        if isinstance(selected_content[0], Movie):
            self.selected_movie = selected_content[0]

        if isinstance(selected_content[1], Showtime):
            self.selected_showtime = selected_content[1]
            
        if is_list_objects(selected_content[2], Seat):
            self.selected_seats = selected_content[2]

        logging.info(f'Selected Movie: {self.selected_movie}')
        logging.info(f'Selected Showtime: {self.selected_showtime}')
        logging.info(f'Selected Seats: {self.selected_seats}')

    def update_buttons(self, button_specs:Dict[str, Union[List[ButtonSpec], Dict[str, Union[type, int]]]]):
        ''' Updates the display buttons based on the provided button specifications.
            Args:
                button_specs (Dict[str, Union[List[ButtonSpec], Dict[str, Union[type, int]]]]): The button specifications to be used for generating buttons.
        '''
        if not validate_button_specs(button_specs):
            logging.error(f'Invalid button spec type: {type(button_specs)}')
            return
        self.display_buttons = self.generate_buttons(button_specs)

    def generate_buttons(self, button_specs:Dict[str, Union[List[ButtonSpec], Dict[str, Union[type, int]]]]) -> List[Button]:
        ''' Generates buttons based on the provided button specifications.
            Args:
                button_specs (Dict[str, Union[List[ButtonSpec], Dict[str, Union[type, int]]]]): The button specifications to be used for generating buttons.
            Returns:
                List[Button]: A list of generated buttons.
        '''
        if not button_specs:
            logging.warning("No button specifications provided for button generation.")
            return []
        
        if not validate_button_specs(button_specs):
            logging.error("Invalid button specifications format.")
            return []
        
        obj_type = button_specs['metadata']['obj_type']
        logging.info(f"Generating buttons for object type: {obj_type}")
        num_of_cols = self.settings.get('default_button_cols')
        width=self.settings.get('default_button_width')
        height=self.settings.get('default_button_height')
        max_height = 200 # Change this to get the screen height dynamically
        default_color=self.settings.get('default_button_color')
        
        if obj_type == Movie:
            num_of_cols = self.settings.get(DisplayObjectType.MOVIE.value)
        elif obj_type == Showtime:
            num_of_cols = self.settings.get(DisplayObjectType.SHOWTIME.value)
        elif obj_type == Seat:
            num_of_cols = button_specs['metadata']['num_cols']
            width = height = self.settings.get('seat_rect_dim')

        display_buttons = button_generation_from_specs(
            specs=button_specs['data'],
            num_of_cols=num_of_cols,
            width=width,
            height=height,
            button_max_height=max_height,
            default_color=default_color
        )
        
        return display_buttons
        
    def display(self, screen:pg.Surface, display_mode:DisplayMode):
        ''' Displays the buttons and header on the screen.
            Args:
                screen (pg.Surface): The Pygame surface to draw the buttons on.
                display_mode (DisplayMode): The current display mode to determine the header text.'''
        if not isinstance(display_mode, DisplayMode):
            logging.error(f'Invalid display type: {display_mode}')
            return
        self.display_header(screen, display_mode)
        if self.continue_button:
            self.continue_button.draw(screen)
        
        for button in self.display_buttons:
            button.draw(screen)
            
    # TODO: Add hovering functionality (should change the button color when hovered)
    def check_button_pressed(self, current_pos:Tuple[int,int]) -> bool:
        ''' Checks if any button is pressed at the current position.
            Args:
                current_pos (Tuple[int,int]): The current mouse position.
            Returns:
                bool: True if a button was pressed, False otherwise.'''
        for button in self.display_buttons:
            if button.is_hovered(current_pos):
                if button.get_color() == self.default_seat_color:
                    button.update_color(self.selected_seat_color)
                elif button.get_color() == self.selected_seat_color:
                    button.update_color(self.default_seat_color)
                return button.action() # Add a return type to the actions so that the actions define how many buttons can be pressed. Still should only be one action per click.
                # return True  # Only one action per click
        if self.continue_button and self.continue_button.is_hovered(current_pos):
            return self.continue_button.action()
        return False
    
    def next_screen(self):
        ''' Switch to the next screen. Should only be used during the seat selection process.'''
        if len(self.selected_seats) == 0:
            return False
        self.switch_to_notifications = True
        return True
        
class ContentManager:
    '''
        Manager class that handles the content of the application.
        It fetches movie data from the Cinemark webpage and manages the display of movies, showtimes, and seats.
        It uses the MovieManager, ShowtimeManager, and SeatManager to manage the respective content.
    '''
    def __init__(self, base_url:str):
        ''' Initializes the ContentManager with the base URL for fetching movie data.
            Args:
                base_url (str): The base URL of the Cinemark webpage to fetch movie data from.
        '''
        self.BASE_URL:str = base_url
        movies: Optional[Dict[int, Movie]] = self.get_movie_data_from_webpage()
        if not movies:
            logging.error(f"No movies returned from the website.")
            return
        
        self.movie_manager: MovieManager = MovieManager(movies)
        self.showtime_manager: ShowtimeManager = ShowtimeManager(movies)
        self.seat_manager: SeatManager = SeatManager()
        
        self.display_mode = DisplayMode.MOVIE
        
        self.selected_movie = None
        self.selected_showtime = None
        self.display_button_specs = None
    
    def get_movie_data_from_webpage(self, url = None) -> Optional[Dict[int, Movie]]:
        ''' Fetches movie data from the Cinemark webpage 
            Args:
                url (str, optional): The URL to fetch movie data from. Defaults to None, which uses the base URL.
            Returns:
                Optional[Dict[int, Movie]]: A dictionary of movies with their IDs as keys and Movie objects as values.
        '''
        if not url:
            url = self.BASE_URL + "/theatres/id-meridian/cinemark-majestic-cinemas?gad_source=1&gad_campaignid=21320863670&gclid=Cj0KCQjwpf7CBhCfARIsANIETVr9mT_YmFb_aVZQJhipsY3c2kmYckiYoG5dQLgUfU9ODgKkcIIqVD8aApW8EALw_wcB&showDate=2025-06-30"
        self.url = url
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
            response.raise_for_status()  # Check for HTTP errors
            soup = BeautifulSoup(response.text, 'html.parser')
            showtime_links = soup.find_all('a', href=re.compile(r"CinemarkMovieId=\d+"))
            showtime_links_arranged = {}
            
            for link in showtime_links:
                try:
                    showtime = Showtime(link_html=link)
                except ValueError as e:
                    logging.warning(f"Skipping invalid showtime link: {link}")
                    continue
                logging.info(f"Found showtime: {showtime.time} (ID: {showtime.movie_id})")
                showtime_links_arranged.setdefault(showtime.movie_id, []).append(showtime)
                
                # if showtime_links_arranged.get(showtime.movie_id):
                #     showtime_links_arranged[showtime.movie_id].append(showtime)
                # else:
                #     showtime_links_arranged[showtime.movie_id] = [showtime]
        
            # Get available movies
            movies = {}
            for h3 in soup.find_all('h3'):
                h3_id = h3.get('id',"")
                if not h3_id.isdigit() or not h3_id:
                    continue
                    
                movie_id = int(h3_id)
                movie = Movie(title=h3.get_text(strip=True), 
                        id=movie_id,
                        showtimes=showtime_links_arranged.get(movie_id, [])
                    )
                
                # If the movie id appears twice, there is an issue
                if movies.get(movie_id):
                    logging.error(f'Original movie: {movies[movie_id].title}')
                    logging.error(f'Current movie: {movie.title}')
                    logging.error(f'ID {movie_id} appears more than once.')
                    raise ValueError(f"The movie with ID {movie_id} has appeared more than once.") # TODO: Change this to a custom error and add retry logic
                    
                movies[movie_id] = movie
                    
            if not movies:
                logging.error("No movies found on the page.")
                return {}
            
            logging.info("Available Movies:")
            for movie_id,movie in movies.items():
                logging.info(f" - {movie.title} (ID: {movie_id})")
                logging.info(f" -- {movie.showtimes}")
            return movies
        
        except requests.Timeout:
            logging.error("Timeout while fetching movie data.")
            return
        except requests.RequestException as e:
            logging.error(f"Error fetching movie data: {e}")
            return
        
    def get_seat_map_from_showtime(self, showtime: Showtime):
        ''' Fetches the seat map for a specific showtime and updates the SeatManager with the seat map data.
            Args:
                showtime (Showtime): The showtime for which to fetch the seat map.
        '''
        if not showtime:
            logging.error("No showtime provided for seat map retrieval.")
            return
        link = self.BASE_URL + showtime.link
        try:
            response = requests.get(link, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
            response.raise_for_status()  # Check for HTTP errors
            seat_map_html = BeautifulSoup(response.text, 'html.parser')
            if not seat_map_html:
                logging.error("No seat map found in the HTML.")
                return
            logging.info(f"Seat map found for showtime: {showtime.time} (ID: {showtime.movie_id})")
            self.seat_manager.load_seat_map(seat_map_html)
            self.seat_manager.create_specs_list_for_seat_map_buttons()
            logging.info("Seat map loaded and button specifications created.")
        except requests.Timeout:
            logging.error("Timeout while fetching seat map data.")
            return
        except requests.RequestException as e:
            logging.error(f"Error fetching seat map data: {e}")
            return
    
    def update(self, switch_scene: bool = False):
        ''' Updates the content manager with the current selections of movie, showtime, and seats.
            This method is called to refresh the selections and update the display mode accordingly.
        '''
        self.selected_movie = self.movie_manager.get_selected_movie()
        self.selected_showtime = self.showtime_manager.get_selected_showtime()
        self.selected_seats = self.seat_manager.get_selected_seats()
        
        # Switch scene if a button was pressed and it isn't the seat display or if the switch_scene flag is triggered.
        if not self.display_mode == DisplayMode.SEAT or switch_scene:
            self.display_mode = update_display_mode(self.display_mode)
            logging.info(f'New Display Mode: {self.display_mode}')
            self.update_buttons_specs(self.display_mode)
            return True
        return False
    
    def update_buttons_specs(self, display_mode:DisplayMode):
        ''' Updates the button specifications based on the current display mode.
            Args:
                display_mode (DisplayMode): The current display mode to determine which button specifications to update.
        '''
        if not isinstance(display_mode, DisplayMode):
            logging.warning(f'Invalid Display Type: {display_mode}')
            return
        display_button_specs = {}
        match(display_mode):
            case DisplayMode.MOVIE:
                display_button_specs = self.movie_manager.get_button_specs()
            case DisplayMode.SHOWTIME:
                self.showtime_manager.create_specs_list_for_showtimes_buttons(self.movie_manager.get_current_movie_id())
                display_button_specs = self.showtime_manager.get_button_specs()
            case DisplayMode.SEAT:
                self.get_seat_map_from_showtime(self.showtime_manager.get_selected_showtime())
                display_button_specs = self.seat_manager.get_button_specs()
        self.display_button_specs = display_button_specs

    def get_buttons_specs(self) -> Dict[str, Union[List[ButtonSpec], Dict[str, Union[type, int]]]]:
        ''' Returns the current button specifications for the display mode.
            Returns:
                Dict[str, Union[List[ButtonSpec], Dict[str, Union[type, int]]]]: The current button specifications for the display mode.
        '''
        if not self.display_button_specs:
            logging.info('Generating buttons for the current display mode.')
            self.update_buttons_specs(self.display_mode)
        if not self.display_button_specs:
            logging.error('No buttons available for the current display mode.')
            return {}
        return self.display_button_specs

    def get_display_mode(self) -> DisplayMode:
        ''' Returns the current display mode.
            Returns:
                DisplayMode: The current display mode.
        '''
        if not isinstance(self.display_mode, DisplayMode):
            logging.error(f'Invalid display mode: {self.display_mode}')
            return DisplayMode.MOVIE
        return self.display_mode
    
    def get_selections(self) -> Tuple[Optional[Movie], Optional[Showtime], Optional[List[Seat]]]:
        ''' Returns the current selections of movie, showtime, and seats 
            Returns:
                Tuple[Optional[Movie], Optional[Showtime], Optional[List[Seat]]]: The current selections of movie, showtime, and seats.
        '''
        return self.movie_manager.selected_movie, self.showtime_manager.selected_showtime, self.seat_manager.get_selected_seats()

def check_events():
    ''' Checks for events like quitting the application 
        Only used during testing. Isn't accessed in the main application.
    '''
    global content_manager, display_mode, running
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                running = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            pos = pg.mouse.get_pos()
            content_manager.check_button_selection(display_mode, pos)
            

def main(screen:pg.Surface):
    ''' Main loop for the application. Handles events, updates content, and displays the screen.
        Args:
            screen (pg.Surface): The Pygame surface to draw the buttons on.
        This is the main function for testing this file.
    '''
    global running, content_manager, display_mode
    
    BASE_URL = "https://www.cinemark.com"
    running = True
    content_manager = ContentManager(BASE_URL)
    display_mode = DisplayMode.MOVIE
    
    while running:
        screen.fill(pg.Color('Black'))
        check_events()
        content_manager.display(screen)
        
        pg.display.flip()

if __name__ == "__main__":
    '''
        Entry point for the application.
        This is a test entry point.
    '''
    import os, sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    pg.init()
    pg.display.set_caption("Movie Scraping Testing")
    screen = pg.display.set_mode((800, 600))

    main(screen)