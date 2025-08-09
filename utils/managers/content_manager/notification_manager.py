from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Union
from utils.assets.button import Button
from settings.settings_utils import Settings
from utils.data_structures.button_spec import ButtonSpec
from utils.misc.generation_status import GenerationStatus
from utils.data_structures.seat import Seat
from utils.misc.utils import is_list_objects
import logging

class NotificationManager:
    def __init__(self, selected_seats: List[Seat] = None):
        ''' Initializes the SeatManager.
            Args:
                selected_seats (List[Seat]): Optional list of selected seats. Allows for seats to be saved and loaded on startup.
        '''
        self.settings = Settings()
        
        if is_list_objects(selected_seats, Seat):
            logging.info(f'Notification Manager initialized with seats.')
            self.selected_seats = selected_seats
        else:
            logging.info('Notification Manager initialized without seats.')
            self.selected_seats = []
        
        self.SEAT_RECT_DIM = self.settings.get('seat_rect_dim')
        self.seat_map_button_specs: Dict[str, Union[List[ButtonSpec], Dict[str, Union[type, int]]]] = {}
        self.seat_default_color = self.settings.get('default_seat_color')
        self.seat_selected_color = self.settings.get('default_seat_selected_color')
        self.seat_unavailable_color = self.settings.get('default_seat_unavailable_color')
        self.background_color = self.settings.get('default_background_color')

    def create_specs_list_for_seat_map_buttons(self) -> GenerationStatus:
        '''Creates the buttons for the seat map. Uses a singleton approach.
           Returns FAILURE if unchanged. SUCCESS if the buttons were updated.
        '''
        # TODO: Finish this method
        seat_specs_data = []
        # y_offset = 0

        #num_cols = list(self.seats.values())[-1][-1].col + 1
        '''In theory, the idea above would work since the back row will have the highest seat number possible.
        It doesn't work in practice and if this was extrapolated to another movie theater, I can't gaurantee that.'''
        num_cols = 0
        for seats in self.seats.values():
            if len(seats) > num_cols:
                # Update num_cols if the current row has more seats than the previous maximum
                num_cols = len(seats)
            
            for seat in seats:
                
                if seat.empty_seat_position:
                    seat_color = self.background_color
                elif not seat.availability:
                    seat_color = self.seat_unavailable_color
                elif seat.selected:
                    seat_color = self.seat_selected_color
                else:
                    seat_color = self.seat_default_color
                    
                button_spec = ButtonSpec(
                    label=str(seat.col) if seat.col else "",
                    color=seat_color,
                    action=lambda s=seat: self.select_seat(s)
                )
                seat_specs_data.append(button_spec)
                
        print(f'Number of columns for seats: {num_cols}')
        self.seat_map_button_specs = {
            'data': seat_specs_data,
            'metadata': {
                'obj_type': Seat,
                'num_cols': num_cols
            }
        }
                
        return GenerationStatus.SUCCESS
                
    def update_seats(self):
        '''
            Currently unimplemented, but in the future will allow for switching the seat map you are looking at.
        '''
        
    def get_button_specs(self) -> Dict[str, Union[List[ButtonSpec], Dict[str, Union[type, int]]]]:
        ''' Returns the button specifications for the seats.
            Returns:
                Dict[str, Union[List[ButtonSpec], Dict[str, type]]]: The button specifications for the seats.
        '''
        return self.seat_map_button_specs
        
    def get_selected_seats(self) -> List[Seat]:
        ''' Returns the currently selected seats.
            Returns:
                List[Seat]: The currently selected seats, or None if no seats are selected.
        '''
        return self.selected_seats
        
    def select_seat(self, seat: Seat) -> bool:
        ''' Determines which seat you selected from the list of seats.
            Args:
                seat (Seat): The Seat object that was selected.
        '''
        logging.info(f'Selected seat: {seat}')
        if seat.availability:
            seat.selected = not seat.selected
            if seat.selected:
                logging.info(f'Adding seat {seat.row}.{seat.col} to selected seats')
                self.selected_seats.append(seat)
                logging.info(f'Total number of selected seats: {len(self.selected_seats)}')
            elif seat in self.selected_seats:
                logging.info(f'Removing seat {seat.row}.{seat.col} from selected seats')
                self.selected_seats.remove(seat)
                
            logging.info(f'Seat {seat.row}.{seat.col} selected: {seat.selected}')
        else:
            logging.warning(f'Seat {seat.row}.{seat.col} is not available.')
            
        return True # Tells the display manager multiple seats can be selected. CHANGED FOR TESTING

    def nop(self):
        """A no-operation function that does nothing."""
        return lambda: None