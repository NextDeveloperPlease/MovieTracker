import logging
from typing import Dict, List
from .button import Button
from .showtime import Showtime
from .movie import Movie
from .settings_utils import Settings
from .generation_status import GenerationStatus
from .utils import convert_button_index_to_position

class ShowtimeManager:
    def __init__(self, movies:Dict[int, Movie]):
        self.showtime_buttons: List[Button] = []
        self.current_movie_id: int = None
        self.selected_showtime: Showtime = None
        self.movies: Dict[int, Movie] = movies
        self.settings = Settings()

    def create_showtimes_buttons(self,movie_id:int) -> GenerationStatus:
        '''Creates the buttons for a specific movie matching that movie_id. Uses a singleton approach.
        Returns FAILURE if unchanged. SUCCESS if the buttons were updated.'''
        if self.current_movie_id == movie_id:
            return GenerationStatus.FAILURE
        
        logging.info(f'Creating showtime buttons for movie ID: {movie_id}')
        
        current_movie:Movie = self.movies.get(movie_id)
        
        if current_movie is None:
            logging.error(f'No movie found for id: {movie_id}')
            return GenerationStatus.FAILURE
        
        self.current_movie_id:int = movie_id
        self.showtime_buttons = []
        
        for i, showtime in enumerate(current_movie.showtimes):
            x,y = convert_button_index_to_position(i, self.settings.get('showtime_col'))
            button = Button(text=showtime.time,
                            x=x,
                            y=y,
                            width=180,
                            height=80,
                            action=lambda st=showtime: self.select_showtime(st))
            self.showtime_buttons.append(button)
        return GenerationStatus.SUCCESS
                
    def select_showtime(self, showtime:Showtime):
        ''' Determines which showtime you selected from the list of showtimes '''
        logging.info(f'Selected: {showtime}')
        self.selected_showtime = showtime
        
    def check_button_pressed(self, current_pos) -> bool:
        for button in self.showtime_buttons:
            if button.is_hovered(current_pos):
                button.action()
                return True  # Only one action per click
        return False
    
    def get_buttons(self) -> List[Showtime]:
        return self.showtime_buttons

    def get_selected_showtime(self) -> Showtime:
        return self.selected_showtime