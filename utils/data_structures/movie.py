from __future__ import annotations
import logging
from typing import List
from utils.data_structures.showtime import Showtime
from utils.data_structures.seat import Seat

class Movie():
    def __init__(self, title, id, showtimes:Showtime=None):
        ''' Initializes a Movie object.
            Args:
                title (str): The title of the movie.
                id (int): The unique identifier for the movie.
                showtimes (Showtime, optional): The showtimes for the movie. Defaults to None.
            Raises:
                ValueError: If title or id is not provided.
        '''
        self.title = title
        self.id = id
        self.showtimes = showtimes if showtimes else None
        self.seats: List[Seat] = []  # Initialize seats as an empty list

    def add_showtimes(self, showtimes: Showtime):
        ''' Adds showtimes to the movie.
            Args:
                showtimes (Showtime): The showtimes to add to the movie.
            Raises:
                ValueError: If showtimes is not provided or is not a Showtime instance.
        '''
        if isinstance(showtimes, Showtime):
            self.showtimes = showtimes
        else:
            logging.warning("Invalid showtimes format. Expected a Showtime instance.")
    
    def add_seats(self,seats: List[Seat]):
        ''' Adds seats to the movie.
            Args:
                seats (List[Seat]): The list of seats to add to the movie.
            Raises:
                ValueError: If seats is not provided or is not a list of Seat instances.
        '''
        if not self.seats:
            self.seats = []
        if isinstance(seats, list) and all(isinstance(seat, Seat) for seat in seats):
            self.seats.extend(seats)
        else:
            logging.warning("Invalid seats format. Expected a list of Seat instances.")
    
    def __eq__(self, value:Movie) -> bool:
        ''' Checks if two Movie objects are equal.
            Args:
                value (Movie): The Movie object to compare with.
            Returns:
                bool: True if the movies are equal, False otherwise.
        '''
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
        ''' Returns a string representation of the Movie object.'''
        return f"Movie(title={self.title}, id={self.id}, showtimes={self.showtimes}, seats={self.seats})"

    def __str__(self):
        ''' Returns a string representation of the Movie object.'''
        return f"{self.title} (ID: {self.id})"
