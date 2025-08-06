import logging
from typing import Dict, List, Optional, Union
from utils.assets.button import Button
from utils.data_structures.movie import Movie
from settings.settings_utils import Settings
from utils.misc.generation_status import GenerationStatus
from utils.data_structures.button_spec import ButtonSpec
from utils.misc.utils import button_generation

class MovieManager:
    # TODO: Add logging info
    def __init__(self, movies:Dict[int, Movie]):
        ''' Initializes the MovieManager with a dictionary of movies.
            Args:
                movies (Dict[int, Movie]): A dictionary where keys are movie IDs and values are Movie objects.
        '''
        self.movie_button_specs: Dict[str, Union[List[ButtonSpec], Dict[str, type]]] = {}
        self.selected_movie: Movie = None
        self.movies: Dict[int, Movie] = movies
        self.settings = Settings()
        
        # TODO: Add error logic for this
        self.create_specs_list_for_movie_buttons()
    
    def create_specs_list_for_movie_buttons(self):
        '''Creates the buttons for the movies. Uses a singleton approach.
           Returns FAILURE if unchanged. SUCCESS if the buttons were updated.
        '''
        # TODO: Add creation validation

        movie_button_specs_data = []
        for movie in self.movies.values():
            button_spec = ButtonSpec(
                label=movie.title,
                color=self.settings.get('default_button_color'),
                action=lambda m=movie: self.select_movie(m)
            )
            movie_button_specs_data.append(button_spec)
            
        self.movie_button_specs = {
            'data': movie_button_specs_data,
            'metadata': {
                'obj_type': Movie
            }
        }
        return GenerationStatus.SUCCESS
                
    def update_movies(self, movies:Dict[int, Movie]):
        ''' Updates the movies in the manager.
            Args:
                movies (Dict[int, Movie]): A dictionary where keys are movie IDs and values are Movie objects.
            Returns:
                GenerationStatus: SUCCESS if the movies were updated, FAILURE if the movies are unchanged or incorrect format.
        '''
        if not isinstance(movies, dict) or not all(isinstance(k, int) and isinstance(v, Movie) for k, v in movies.items()):
            logging.error(f"Incorrect format. Expected Dict[int, Movie]")
            return GenerationStatus.FAILURE
        if movies == self.movies:
            logging.warning(f'Current movies are the same as the new movies.')
            return GenerationStatus.FAILURE
        
        backup_movies = self.movies #Used in case create_movie_buttons errors (Currently not useful)
        self.movies = movies
        
        # TODO: Add creation check to ensure the buttons were generated
        self.create_specs_list_for_movie_buttons()

    def get_button_specs(self) -> Dict[str, Union[List[ButtonSpec], Dict[str, type]]]:
        ''' Returns the button specifications for the movies.
            Returns:
                Dict[str, Union[List[ButtonSpec], Dict[str, type]]]: The button specifications for the movies.
        '''
        return self.movie_button_specs
    
    def get_current_movie_id(self) -> int:
        ''' Returns the ID of the currently selected movie.
            Returns:
                int: The ID of the currently selected movie, or None if no movie is selected.
        '''
        if not self.selected_movie:
            return None
        return self.selected_movie.id
    
    def get_selected_movie(self) -> Movie:
        ''' Returns the currently selected movie.
            Returns:
                Movie: The currently selected movie, or None if no movie is selected.
        '''
        return self.selected_movie

    def select_movie(self, movie:Movie):
        ''' Determines which movie you selected from the list of movies.
            Args:
                movie (Movie): The Movie object that was selected.
        '''
        logging.info(f'Selected: {movie}')
        self.selected_movie:Movie = movie
        logging.info(f'Available Showtimes:')
        #print(movie.showtimes)
        for showtime in movie.showtimes:
            logging.info(f"- {showtime.time} (ID: {showtime.movie_id})")
        return True # Tells the display manager that only one movie can be selected.

    def get_button_label(self, movie: Movie) -> str:
        ''' Returns the label for the movie button.
            Args:
                movie (Movie): The Movie object for which to get the label.
            Returns:
                str: The title of the movie.
            This was a prior implementation. Now I create a ButtonSpec that contains the label,
            this function is obsolete.
        '''
        return movie.title if movie else "No Movie Selected"
