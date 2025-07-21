from bs4 import BeautifulSoup
import re

class Seat:
    def __init__(self, seat_html:BeautifulSoup = None):
        if not seat_html:
            raise ValueError("seat_html must be provided.")
        for seat in seat_html.get('button', []):
            id = seat.get('id', '')
            availability = seat.get('available', '').lower() == 'true'
            #a = 'row0col0'
            row = id.charAt(3)
            col = id.charAt(7)
            self.seat_number = f"{row}{col}"
            
            
    def __repr__(self):
        return f"Seat(seat_number={self.seat_number}, is_available={self.is_available})"

    def __str__(self):
        return f"Seat {self.seat_number} - {'Available' if self.is_available else 'Not Available'}"