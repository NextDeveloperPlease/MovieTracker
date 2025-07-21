import logging
from typing import List
from utils.showtime import Showtime
from utils.seat import Seat


class Movie():
    def __init__(self, title, id, showtimes:Showtime=None):
        self.title = title
        self.id = id
        self.showtimes = showtimes if showtimes else None

    def add_showtimes(self, showtimes: Showtime):
        if isinstance(showtimes, Showtime):
            self.showtimes = showtimes
        else:
            logging.warning("Invalid showtimes format. Expected a Showtime instance.")
    
    def add_seats(self,seats: List[Seat]):
        if not self.seats:
            self.seats = []
        if isinstance(seats, list) and all(isinstance(seat, Seat) for seat in seats):
            self.seats.extend(seats)
        else:
            logging.warning("Invalid seats format. Expected a list of Seat instances.")

    def __repr__(self):
        return f"Movie(title={self.title}, id={self.id}, showtimes={self.showtimes}, seats={self.seats})"

    def __str__(self):
        return f"{self.title} (ID: {self.id})"