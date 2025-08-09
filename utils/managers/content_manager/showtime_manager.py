import logging
from typing import Dict, List, Optional, Union
from utils.assets.button import Button
from utils.data_structures.showtime import Showtime
from utils.data_structures.movie import Movie
from settings.settings_utils import Settings
from utils.misc.generation_status import GenerationStatus
from utils.data_structures.button_spec import ButtonSpec
from utils.misc.utils import button_generation

class ShowtimeManager:
    def __init__(self, movies:Dict[int, Movie]):
        ''' Initializes the ShowtimeManager with a dictionary of movies.
            Args:
                movies (Dict[int, Movie]): A dictionary where keys are movie IDs and values are Movie objects.
        '''
        # TODO: Add movies verification process
        self.showtime_button_specs: Dict[str, Union[List[ButtonSpec], Dict[str, type]]] = {}
        self.current_movie_id: int = None
        self.selected_showtime: Showtime = None
        self.movies: Dict[int, Movie] = movies
        self.settings = Settings()

    def create_specs_list_for_showtimes_buttons(self,movie_id:int) -> GenerationStatus:
        '''Creates the buttons for the movies. Uses a singleton approach.
           Returns FAILURE if unchanged. SUCCESS if the buttons were updated.
        '''
        if self.current_movie_id == movie_id:
            return GenerationStatus.FAILURE
        
        logging.info(f'Creating showtime buttons for movie ID: {movie_id}')
        
        current_movie:Movie = self.movies.get(movie_id)
        
        if current_movie is None:
            logging.error(f'No movie found for id: {movie_id}')
            return GenerationStatus.FAILURE
        
        self.current_movie_id:int = movie_id
        #self.showtime_buttons = button_generation(current_movie.showtimes, self.settings.get('showtime_col'), self.select_showtime, self.get_button_label)
        showtime_button_specs_data = []
        for showtime in current_movie.showtimes:
            button_spec = ButtonSpec(
                label=showtime.time,
                color=self.settings.get('default_button_color'),
                action=lambda s=showtime: self.select_showtime(s)
            )
            showtime_button_specs_data.append(button_spec)

        self.showtime_button_specs = {
            'data': showtime_button_specs_data,
            'metadata': {
                'obj_type': Showtime
            }
        }

        return GenerationStatus.SUCCESS
                
    def select_showtime(self, showtime:Showtime):
        ''' Determines which showtime you selected from the list of showtimes.
            Args:
                showtime (Showtime): The Showtime object that was selected.
        '''
        logging.info(f'Selected: {showtime}')
        self.selected_showtime = showtime
        return True # Tells the display manager only one showtime can be selected.

    def get_button_specs(self) -> Dict[str, Union[List[ButtonSpec], Dict[str, type]]]:
        ''' Returns the button specifications for the showtimes.
            Returns:
                Dict[str, Union[List[ButtonSpec], Dict[str, type]]]: The button specifications for the showtimes.
        '''
        return self.showtime_button_specs

    def get_selected_showtime(self) -> Showtime:
        ''' Returns the currently selected showtime.
            Returns:
                Showtime: The currently selected showtime, or None if no showtime is selected.
        '''
        return self.selected_showtime

    def get_button_label(self, showtime: Showtime) -> str:
        ''' Returns the label for the showtime button.
            Args:
                showtime (Showtime): The Showtime object for which to get the label.
            Returns:
                str: The time for the showtime.
            This was a prior implementation. Now I create a ButtonSpec that contains the label,
            this function is obsolete.
        '''
        return showtime.time if showtime else "No Showtime Selected"
