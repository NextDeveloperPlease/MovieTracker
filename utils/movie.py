from __future__ import annotations
import logging
from typing import List
from .showtime import Showtime
from .seat import Seat

class Movie():
    def __init__(self, title, id, showtimes:Showtime=None):
        self.title = title
        self.id = id
        self.showtimes = showtimes if showtimes else None
        self.seats: List[Seat] = []  # Initialize seats as an empty list

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
    
    def __eq__(self, value:Movie) -> bool:
        if not isinstance(value, Movie):
            return False
        
        if len(value.showtimes) != len(self.showtimes):
            return False
        
        if value.title != self.title:
            return False
        
        if value.id != self.id:
            return False
        
        for v_showtime,s_showtime in zip(value.showtimes,self.showtimes):
            if v_showtime != s_showtime:
                return False
        
        return True
        

    def __repr__(self):
        return f"Movie(title={self.title}, id={self.id}, showtimes={self.showtimes}, seats={self.seats})"

    def __str__(self):
        return f"{self.title} (ID: {self.id})"
