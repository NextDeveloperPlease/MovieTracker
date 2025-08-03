import logging
from typing import Dict
from .button import Button
from .movie import Movie
from .settings_utils import Settings
from .generation_status import GenerationStatus
from .utils import convert_button_index_to_position

class MovieManager:
    # TODO: Add logging info
    def __init__(self, movies:Dict[int, Movie]):
        self.movie_buttons: Dict[int, Button] = {}
        self.selected_movie: Movie = None
        self.movies: Dict[int, Movie] = movies
        self.settings = Settings()
        
        # TODO: Add error logic for this
        self.create_movie_buttons()
    
    def create_movie_buttons(self):
        '''Creates the movie buttons. Uses a singleton approach'''
        # TODO: Add creation validation
        self.movie_buttons.clear()
        for i, (movie_id,movie) in enumerate(self.movies.items()):
            x,y = convert_button_index_to_position(i, self.settings.get('movie_col'))
            button = Button(text=movie.title,
                            x=x,
                            y=y,
                            width=180,
                            height=80,
                            action=lambda m=movie: self.select_movie(m))
            self.movie_buttons[movie_id] = button
                
    def update_movies(self, movies:Dict[int, Movie]):
        if not isinstance(movies, dict) or not all(isinstance(k, int) and isinstance(v, Movie) for k, v in movies.items()):
            logging.error(f"Incorrect format. Expected Dict[int, Movie]")
            return GenerationStatus.FAILURE
        if movies == self.movies:
            logging.warning(f'Current movies are the same as the new movies.')
            return GenerationStatus.FAILURE
        
        backup_movies = self.movies #Used in case create_movie_buttons errors (Currently not useful)
        self.movies = movies
        
        # TODO: Add creation check to ensure the buttons were generated
        self.create_movie_buttons()
        
    def get_buttons(self) -> Dict[int, Button]:
        return self.movie_buttons
    
    def get_current_movie_id(self) -> int:
        if not self.selected_movie:
            return None
        return self.selected_movie.id
    
    def get_selected_movie(self) -> Movie:
        return self.selected_movie

    def select_movie(self, movie:Movie):
        '''Movie selection function for button action'''
        logging.info(f'Selected: {movie}')
        self.selected_movie:Movie = movie
        logging.info(f'Available Showtimes:')
        #print(movie.showtimes)
        for showtime in movie.showtimes:
            logging.info(f"- {showtime.time} (ID: {showtime.movie_id})")
    