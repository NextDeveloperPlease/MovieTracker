import logging
from utils.showtime import Showtime


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

    def __repr__(self):
        return f"Movie(title={self.title}, id={self.id}, showtimes={self.showtimes})"

    def __str__(self):
        return f"{self.title} (ID: {self.id})"