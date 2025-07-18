from bs4 import BeautifulSoup
from bs4.element import Tag

import re
import logging

class Showtime:
    def __init__(self, movie_id:str=None, time:str=None, link:str=None, link_html:Tag=None):
        if link_html:
            self.movie_id,self.time,self.link = self.parse_html(link_html)
        else:
            if not movie_id or not time or not link:
                raise ValueError("movie_id, time, and link must be provided if html is not given.")
            
            self.movie_id = movie_id
            self.time = time # Format: "HH:MM AM/PM"
            self.link = link

    def parse_html(self, html:Tag):
        href = html.get('href', '')
        if 'CinemarkMovieId=' not in href:
            logging.warning("Link does not contain a valid CinemarkMovieId.")
            return None, None, None
        movie_id = re.search(r'CinemarkMovieId=(\d+)', href)
        movie_time = html.get_text(strip=True)
        if not movie_id:
            logging.warning("No movie ID found in the link.")
            return None, None, None
        if not movie_time:
            logging.warning("No movie time found in the link.")
            return None, None, None
        movie_id_str = movie_id.group(1)
        if not movie_id_str.isdigit():
            logging.warning("No valid movie ID found in the link.")
            return None, None, None
        self.movie_id = movie_id_str
        self.time = movie_time.replace('pm', ' PM').replace('am', ' AM')  # Normalize time format
        self.link = html.get('href', '')
        return movie_id_str, movie_time, self.link
    
    
    def __repr__(self):
        return f"Showtime(movie_id={self.movie_id}, time={self.time}, link={self.link})"
    
    
    
    '''
    <a aria-label="Select 3:20 PM showtime for Sunday, July 13, 2025" class="showtime-link" 
    href="/TicketSeatMap/?TheaterId=1019&amp;ShowtimeId=177162&amp;CinemarkMovieId=101789&amp;
    Showtime=2025-07-13T15:20:00">3:20pm</a>
    '''