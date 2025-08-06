from typing import Tuple
from bs4 import BeautifulSoup
from bs4.element import Tag
import re
import logging
    
class Seat:
    def __init__(self, seat_html:Tag):
        ''' Initializes a Seat object.
            Args:
                seat_html (Tag): The HTML tag containing the seat information.
            Raises:
                ValueError: If seat_html is not provided or does not contain a valid 'id' attribute.
        '''
        if not seat_html:
            raise ValueError("seat_html must be provided.")
        
        self.row,self.col,self.availability = self.parse_seat(seat_html)
        self.selected = False  # Default to not selected

    def parse_seat(self, seat_html:Tag) -> Tuple[int, int, bool]:
        ''' Parses the seat HTML to extract row, column, and availability.
            Args:
                seat_html (Tag): The HTML tag containing the seat information.
            Returns:
                Tuple[int, int, bool]: A tuple containing the row number, column number, and availability status.
            Raises:
                ValueError: If the seat HTML does not contain a valid 'id' attribute.
        '''
        row = col = availability = None
        
        self.empty_seat_position = True  # Default to empty position
        if seat_html.name == 'button':
            id = seat_html.get('id', '')
            if not id:
                logging.error("Seat HTML must contain an 'id' attribute.")
                # raise ValueError("Seat HTML must contain an 'id' attribute.")
            # Assumes id format is like 'row0col0'
            row = int(id[3])  # Row letter from 1 to 8 (A to H)
            col = int(id.split('col')[1])  # Column is the seat number in the row
            availability = seat_html.get('available', '').lower() == 'true'
            self.empty_seat_position = False
        return row,col,availability
    
            # Saving this for later, but might delete if not needed
            # info = seat_html.get('info', '').split(',')
            # row = from_letter_to_int(info[0])  # First character is the row letter
            # col = int(info[1])  # Second part is the column number
            # availability = None
    
    def __repr__(self):
        ''' Returns a string representation of the Seat object.'''
        return f"Seat(row={self.row}, col={self.col}, is_available={self.availability})"
    
    def __str__(self):
        ''' Returns a string representation of the Seat object.'''
        return f"Seat {self.row}.{self.col} - {'Available' if self.availability else 'Not Available'}"