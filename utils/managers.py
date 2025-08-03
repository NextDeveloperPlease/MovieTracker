import re
from typing import List, Dict, Optional, Tuple
import requests
import logging
import time
import sys
import pygame as pg
from .display_mode import DisplayMode, update_display_mode
from .settings_utils import Settings
from .showtime_manager import ShowtimeManager
from .movie_manager import MovieManager
from .utils import is_list_objects

from bs4 import BeautifulSoup
# from utils.button import Button
# from utils.movie import Movie
# from utils.showtime import Showtime

from .button import Button
from .movie import Movie
from .showtime import Showtime

#from utils.seat import Seat
# from utils.display_mode import DisplayMode
from enum import Enum

import pygame as pg


class DisplayManager:
    '''
        Class containing logic for displaying buttons and switching display sections.
        # TODO: Write a more descriptive explanation
    '''
    WHITE = pg.Color('white')
    
    def __init__(self, buttons:List[Button]):
        self.settings = Settings()
        self.selected_movie:Movie = None
        self.selected_showtime:Showtime = None
        self.selected_seats = {}
        
        if is_list_objects(buttons, Button):
            self.display_buttons = buttons
        else:
            logging.error(f'Invalid Button Type: {buttons}')
    
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
            case DisplayMode.NOTIFYING:
                mode_text = "Notification:"
        
        date_surface = font.render(date_text, True, self.WHITE)
        mode_surface = font.render(mode_text, True, self.WHITE)
        
        screen.blit(date_surface, (50, 100))
        screen.blit(mode_surface, (50, 150))

    def update_header(self, selected_content:Tuple[Optional[Movie], Optional[Showtime]]):
        logging.info(f'Updating header with movie: {selected_content[0]}, showtime: {selected_content[1]}')
        logging.info(f'selected_movie variable type: {type(selected_content[0])}')
        logging.info(f'selected_showtime variable type: {type(selected_content[1])}')

        if isinstance(selected_content[0], Movie):
            self.selected_movie = selected_content[0]

        if isinstance(selected_content[1], Showtime):
            self.selected_showtime = selected_content[1]

        logging.info(f'Selected Movie: {self.selected_movie}')
        logging.info(f'Selected Showtime: {self.selected_showtime}')
        
    def update_buttons(self, buttons:List[Button]):
        if not is_list_objects(buttons, Button):
            logging.error(f'Invalid button type: {type(buttons)}')
            return
        self.display_buttons = buttons
        
    def display(self, screen:pg.Surface, display_mode:DisplayMode):
        if not isinstance(display_mode, DisplayMode):
            logging.error(f'Invalid display type: {display_mode}')
            return
        self.display_header(screen, display_mode)
        
        for button in self.display_buttons:
            button.draw(screen)
    
class ContentManager:
    '''
        Manager class that pulls the movie data.
        # TODO: Write a more descriptive explanation
    '''
    def __init__(self, base_url:str):
        self.BASE_URL:str = base_url
        movies: Optional[Dict[int, Movie]] = self.get_movie_data_from_webpage()
        if not movies:
            logging.error(f"No movies returned from the website.")
            return
        
        self.movie_manager: MovieManager = MovieManager(movies)
        self.showtime_manager: ShowtimeManager = ShowtimeManager(movies)
        self.display_mode = DisplayMode.MOVIE
        
        self.selected_movie = None
        self.selected_showtime = None
        self.display_buttons = None
    
    def get_movie_data_from_webpage(self, url = None) -> Optional[Dict[int, Movie]]:
        ''' Fetches movie data from the Cinemark webpage '''
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
        
    def check_button_pressed(self, current_pos:Tuple[int,int]) -> bool:
        for button in self.display_buttons:
            if button.is_hovered(current_pos):
                button.action()
                self.selected_movie = self.movie_manager.get_selected_movie()
                self.selected_showtime = self.showtime_manager.get_selected_showtime()
                self.display_mode = update_display_mode(self.display_mode)
                logging.info(f'New Display Mode: {self.display_mode}')
                self.update_buttons(self.display_mode)
                return True  # Only one action per click
        return False
        
    def check_button_selection(self, display:DisplayMode, current_pos:Tuple[int,int]):
        if not isinstance(display, DisplayMode):
            raise ValueError(f"Invalid display type: {display}")
        
        match(display):
            case DisplayMode.MOVIE:
                successfully_clicked = self.movie_manager.check_button_pressed(current_pos=current_pos)
                if successfully_clicked:
                    self.showtime_manager.create_showtimes_buttons(self.movie_manager.get_current_movie_id())
                    self.display_mode = DisplayMode.SHOWTIME
            case DisplayMode.SHOWTIME:
                successfully_clicked = self.showtime_manager.check_button_pressed(current_pos=current_pos)
                if successfully_clicked:
                    self.display_mode = DisplayMode.SEAT
    
    def update_buttons(self, display_mode:DisplayMode):
        if not isinstance(display_mode, DisplayMode):
            logging.warning(f'Invalid Display Type: {display_mode}')
            return
        display_buttons = []
        match(display_mode):
            case DisplayMode.MOVIE:
                display_buttons = list(self.movie_manager.get_buttons().values())
            case DisplayMode.SHOWTIME:
                self.showtime_manager.create_showtimes_buttons(self.movie_manager.get_current_movie_id())
                display_buttons = self.showtime_manager.get_buttons()
        self.display_buttons = display_buttons
        
    def get_buttons(self) -> List[Button]:
        if not self.display_buttons:
            logging.info('Generating buttons for the current display mode.')
            self.update_buttons(self.display_mode)
        if not self.display_buttons:
            logging.error('No buttons available for the current display mode.')
            return []
        return self.display_buttons
    
    def get_display_mode(self) -> DisplayMode:
        if not isinstance(self.display_mode, DisplayMode):
            logging.error(f'Invalid display mode: {self.display_mode}')
            return DisplayMode.MOVIE
        return self.display_mode
    
    def get_selections(self) -> Tuple[Optional[Movie], Optional[Showtime]]:
        ''' Returns the current selections of movie, showtime, and seats '''
        return self.movie_manager.selected_movie, self.showtime_manager.selected_showtime

def check_events():
    ''' Checks for events like quitting the application '''
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
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    pg.init()
    pg.display.set_caption("Movie Scraping Testing")
    screen = pg.display.set_mode((800, 600))

    main(screen)