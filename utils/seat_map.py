from bs4 import BeautifulSoup
from bs4.element import Tag
from enum import Enum
import logging
import pygame as pg
#from utils.button import Button
from .button import Button

SEAT_RECT_DIM = 50 # It is a square

class Seat:
    def __init__(self, seat_html:Tag):
        if not seat_html:
            raise ValueError("seat_html must be provided.")
        
        self.row,self.col,self.availability = self.parse_seat(seat_html)
        self.selected = False  # Default to not selected

    def parse_seat(self, seat_html:Tag):
        id = seat_html.get('id', '')
        if not id:
            raise ValueError("Seat HTML must contain an 'id' attribute.")
        # Assumes id format is like 'row0col0'
        row = from_int_to_letter(int(id[3])) # Row letter from 1 to 8 (A to H)
        col = id.split('col')[1] # Column is the seat number in the row
        availability = seat_html.get('available', '').lower() == 'true'
        return row,col,availability
    
    def __repr__(self):
        return f"Seat(row={self.row}, col={self.col}, is_available={self.availability})"
    
    def __str__(self):
        return f"Seat {self.seat_number} - {'Available' if self.is_available else 'Not Available'}"

def from_int_to_letter(num: int) -> str:
    """Convert a number to a letter (1 -> A, 2 -> B, etc.)."""
    if num < 1:
        raise ValueError("Number must be greater than 0.")
    if num > 8:
        raise ValueError("Maximum number is 8 (A to H).")
    return chr(ord('A') + num - 1) # 1-based index

def from_letter_to_int(letter: str) -> int:
    """Convert a letter to a number (A -> 1, B -> 2, etc.)."""
    if not letter.isalpha() or len(letter) != 1:
        raise ValueError("Input must be a single letter.")
    if letter.upper() < 'A' or letter.upper() > 'H':
        raise ValueError("Letter must be between A and H.")
    return ord(letter.upper()) - ord('A') + 1  # 1-based index

class SeatMap:
    def __init__(self, seat_html:BeautifulSoup):
        self.seats = {}
        for seat in seat_html.find_all('button'):
            seat_obj = Seat(seat)
            if not seat_obj:
                logging.warning("Invalid seat HTML. Skipping this seat.")
            if self.seats.get(seat_obj.row) is None:
                self.seats[seat_obj.row] = []
            self.seats[seat_obj.row].append(seat_obj)
            
    def create_seat_map(self):
        """Create the seat map buttons for displaying (should only be a singleton)."""
        self.buttons = {}
        y_offset = 0
        for row, seats in self.seats.items():
            self.buttons[row] = []
            y_offset += SEAT_RECT_DIM + 15
            x_offset = 50
            for seat in seats:
                seat_color = pg.Color('green') if seat.availability else pg.Color('red')
                button = Button(text=str(seat.col), x=x_offset, y=y_offset, width=SEAT_RECT_DIM, height=SEAT_RECT_DIM, color=seat_color, action=lambda s=seat: select_seat(s))
                self.buttons[row].append(button)
                x_offset += SEAT_RECT_DIM + 10
        

    def display(self, screen:pg.Surface, font:pg.font.Font = None):
        """Display the seat map on the given Pygame screen."""
        if font is None:
            font = pg.font.Font(None, 5)
        if not hasattr(self, 'buttons'):
            self.create_seat_map()
            
        for row in self.seats:
            seats = self.seats[row]
            buttons = self.buttons[row]
            for seat,button in zip(seats,buttons):
                if seat.availability:
                    color = pg.Color('yellow') if seat.selected else pg.Color('green')
                    button.update_color(color)
                button.draw(screen, font)
                if button.is_hovered(pg.mouse.get_pos()):
                    pg.draw.rect(screen, (255, 255, 0), button.rect, 2)

    def __repr__(self):
        return f"SeatMap(seats={self.seats})"

def select_seat(seat: Seat):
    """Handle seat selection logic."""
    logging.info(f"Seat {seat.row}{seat.col} clicked.")
    if seat.availability:
        logging.info(f"Seat {seat.row}{seat.col} selected.")
        seat.selected = not seat.selected
        # TODO: Add logic to handle saving the selected seat
    else:
        logging.warning(f"Seat {seat.row}{seat.col} is not available.")

if __name__ == '__main__':
    seat_html = BeautifulSoup('', 'html.parser')
    for i in range(1, 9):
        for j in range(1, 10):
            # Example seat HTML generation
            seat_html.append(Tag(name='button', attrs={'id': f'row{i}col{j}', 'available': 'true'}))
        seat_html.append(Tag(name='button', attrs={'id': f'row{i}col10', 'available': 'false'}))

    seat_map = SeatMap(seat_html=seat_html)
    running = True
    pg.init()
    screen = pg.display.set_mode((800, 600))
    font = pg.font.Font(None, 36)
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    for row,buttons in seat_map.buttons.items():
                        for button in buttons:
                            if button.is_hovered(pg.mouse.get_pos()):
                                button.action()

        screen.fill((255, 255, 255))  # Clear the screen with white
        seat_map.display(screen,font=font)  # Display the seat map
        pg.display.flip()