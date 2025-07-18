import logging


class Movie():
    def __init__(self, title, id, showtimes=None):
        self.title = title
        self.id = id
        self.showtimes = showtimes if showtimes is not None else {'link': '', 'time': ''}
    
    def add_showtimes(self, showtimes):
        if isinstance(showtimes, dict):
            self.showtimes = showtimes
        else:
            logging.warning("Invalid showtimes format. Expected a dictionary.")

    def __repr__(self):
        return f"Movie(title={self.title}, id={self.id}, showtimes={self.showtimes})"

    def __str__(self):
        return f"{self.title} (ID: {self.id})"