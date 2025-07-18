import re
import requests
import logging
import time
import sys

from bs4 import BeautifulSoup
from utils.button import Button
from utils.movie import Movie
from utils.showtime import Showtime
#from utils.seat import Seat
from utils.display_mode import DisplayMode

import pygame as pg

# Constants for colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Column arrangement variables
MOVIE_COL = 2
SHOWTIME_COL = 3

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
fullscreen = False

running = True
reset = False

movie_buttons = []
selected_movie = None
showtime_buttons = []
selected_showtime = None
seat_buttons = []
selected_seats = []

display_mode = DisplayMode.MOVIE

BASE_URL = "https://www.cinemark.com"

def check_events():
    ''' Checks for events like quitting the application '''
    global running, display_mode
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                running = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            pos = pg.mouse.get_pos()
            match display_mode:
                case DisplayMode.MOVIE:
                    for button in movie_buttons:
                        if button.is_hovered(pos):
                            button.action()
                            continue  # Only one action per click
                case DisplayMode.SHOWTIME:
                    for button in showtime_buttons:
                        if button.is_hovered(pos):
                            button.action()
                            continue  # Only one action per click

def check_seat_availability(url, row_start, row_end, col):
    seat_availabilities = []
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        response.raise_for_status()  # Check for HTTP errors
        soup = BeautifulSoup(response.text, 'html.parser')

        for row in range(row_start, row_end + 1):
            seat_id = f"row{row}col{col}"
            
            # Example: Check for a specific element that indicates seat availability
            seat_button = soup.find('button', id=seat_id)
            if seat_button is None:
                print(f"Seat {seat_id} not found on the page.")
                seat_availabilities.append((row,col,False))
                continue
            
            availability = seat_button.get("available","").lower()
            if availability == "true":
                seat_availabilities.append((row,col,True))
            elif availability == "false":
                print(f"❌ Seat {seat_id} is NOT available.")
                seat_availabilities.append((row,col,False))
            else:
                print(f"⚠️ Seat {seat_id} has unknown availability: {availability}")
                seat_availabilities.append((row,col,False))
    except requests.Timeout:
        print(f"Timeout while fetching data for seat {seat_id}.")
        seat_availabilities.append((row,col,False))
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        seat_availabilities.append((row,col,False))
    return seat_availabilities

def get_movie_data_from_webpage(url = None):
    ''' Fetches movie data from the Cinemark webpage '''
    global BASE_URL
    if not url:
        url = BASE_URL + "/theatres/id-meridian/cinemark-majestic-cinemas?gad_source=1&gad_campaignid=21320863670&gclid=Cj0KCQjwpf7CBhCfARIsANIETVr9mT_YmFb_aVZQJhipsY3c2kmYckiYoG5dQLgUfU9ODgKkcIIqVD8aApW8EALw_wcB&showDate=2025-06-30"
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        response.raise_for_status()  # Check for HTTP errors
        soup = BeautifulSoup(response.text, 'html.parser')
        showtime_links = soup.find_all('a', href=re.compile(r"CinemarkMovieId=\d+"))
        showtime_links_arranged = {}
        
        for link in showtime_links:
            showtime = Showtime(link_html=link)
            if not showtime:
                logging.warning(f"Skipping invalid showtime link: {link}")
                continue
            logging.info(f"Found showtime: {showtime.time} (ID: {showtime.movie_id})")
            if showtime_links_arranged.get(showtime.movie_id):
                showtime_links_arranged[showtime.movie_id].append(showtime)
            else:
                showtime_links_arranged[showtime.movie_id] = [showtime]
        
        # Get available movies
        movies = []
        for h3 in soup.find_all('h3'):
            h3_id = h3.get('id',"")
            if h3_id.isdigit():
                movies.append(
                    Movie(title=h3.get_text(strip=True), 
                        id=int(h3_id),
                        showtimes=showtime_links_arranged.get(h3_id, [])
                    )
                )

        if not movies:
            logging.error("No movies found on the page.")
            return
        logging.info("Available Movies:")
        for movie in movies:
            logging.info(f" - {movie.title} (ID: {movie.id})")
        return movies
    except requests.Timeout:
        logging.error("Timeout while fetching movie data.")
        return
    except requests.RequestException as e:
        logging.error(f"Error fetching movie data: {e}")
        return

def display_header():
    ''' Displays the header with current date and display mode '''
    global screen, running, display_mode, selected_movie, selected_showtime, selected_seats
    font = pg.font.Font(None, 36)
    date_text = time.strftime("%Y-%m-%d %H:%M:%S")
    mode_text = ""
    match display_mode:
        case DisplayMode.MOVIE:
            mode_text = "Movies:"
        case DisplayMode.SHOWTIME:
            if not selected_movie:
                mode_text = "Showtimes:"
                logging.error("No movie selected for showtimes.")
                return
            movie_edited = f"{selected_movie.title}'s"
            mode_text = f'{movie_edited} Showtimes:'
        case DisplayMode.SEAT:
            mode_text = "Seats:"
        case DisplayMode.NOTIFYING:
            mode_text = "Notification:"
    
    date_surface = font.render(date_text, True, WHITE)
    mode_surface = font.render(mode_text, True, WHITE)
    
    screen.blit(date_surface, (50, 100))
    screen.blit(mode_surface, (50, 150))

def display_movies(movies):
    ''' Displays the list of movies in a grid format '''
    global screen
    if not movie_buttons:
        for i, movie in enumerate(movies):
            button = Button(movie.title, 50 + (i % MOVIE_COL) * 200, 200 + (i // MOVIE_COL) * 100, 180, 80, action=lambda m=movie: select_movie(m))
            movie_buttons.append(button)
    for button in movie_buttons:
        button.draw(screen)

def select_movie(movie):
    '''Movie selection function for button action'''
    global selected_movie, display_mode
    logging.info(f'Selected: {movie}')
    selected_movie = movie
    logging.info(f'Available Showtimes:')
    for showtime in movie.showtimes:
        logging.info(f"- {showtime.time} (ID: {showtime.movie_id})")

def display_showtimes(movie):
    ''' Displays the list of showtimes in a grid format'''
    global screen
    if not showtime_buttons:
        for i, showtime in enumerate(movie.showtimes):
            button = Button(showtime.time, 50 + (i % SHOWTIME_COL) * 200, 200 + (i // SHOWTIME_COL) * 100, 180, 80, action=lambda st=showtime: select_showtime(st))
            showtime_buttons.append(button)
    for button in showtime_buttons:
        button.draw(screen)

def select_showtime(showtime):
    ''' Determines which showtime you selected from the list of showtimes '''
    global selected_showtime, display_mode
    logging.info(f'Selected: {showtime}')
    selected_showtime = showtime

def get_seats(showtime):
    ''' Fetches available seats for a given showtime '''
    if not showtime:
        print("No showtime provided.")
        return None

    # pull seat map from the showtime
    
    # return the seat map
    
def display_seat_map(seat_map):
    ''' Displays the seat map in a grid format (allows for user selection)'''
    # TODO

def select_seat(seat_map):
    ''' Allows the user to select a seat from the seat map '''
    # TODO

def main():
    global running, display_mode
    logging.info("Starting Movie Seat Selection Application")
    
    movies = None
    seats = None
    
    while running:
        screen.fill(BLACK)  # Fill the screen with black
        check_events()  # Check for events (like quitting)
        
        display_header()  # Display the header with current date and mode

        match(display_mode):
            case DisplayMode.MOVIE:
                if not movies:
                    logging.info("Fetching movies...")
                    movies = get_movie_data_from_webpage()
                    if not movies:
                        logging.error("No movies available. Exiting.")
                        running = False
                        continue
                display_movies(movies)
                if selected_movie:
                    logging.info(f"Selected movie: {selected_movie}")
                    display_mode = DisplayMode.SHOWTIME

            case DisplayMode.SHOWTIME:
                display_showtimes(selected_movie)
                if selected_showtime:
                    logging.info(f"Selected showtime: {selected_showtime}")
                    display_mode = DisplayMode.SEAT

            case DisplayMode.SEAT:
                # TODO: Fix this section to display seats
                display_showtimes(selected_movie)
                '''if not seats:
                    logging.info(f"Fetching seats for showtime ID {selected_showtime.movie_id}...")
                    seats = get_seats(selected_showtime)
                    if not seats:
                        logging.error("No seats available for the selected showtime. Exiting.")
                        running = False
                        continue
                display_seat_map(seats)
                selected_seats_info = select_seat(seats)
                if selected_seats_info:
                    logging.info(f"Selected seats: {selected_seats_info}")'''
            
            case DisplayMode.NOTIFYING:
                # TODO: Fix this section to display notifications
                logging.info("Displaying notification for selected seats...")
                if selected_seats_info:
                    logging.info(f"Selected seats: {selected_seats_info}")
                    seat_availabilities = check_seat_availability(selected_seats_info['url'], 
                                                                  selected_seats_info['row_start'], 
                                                                  selected_seats_info['row_end'], 
                                                                  selected_seats_info['col'])
                    all_available = all(available for _, _, available in seat_availabilities)
                    if all_available:
                        logging.info("✅ All selected seats are available!")
                    else:
                        logging.error("❌ Some selected seats are NOT available.")
                    #display_notification(all_available, seat_availabilities)
                    if reset:
                        display_mode = DisplayMode.MOVIE
                        reset = False
                else:
                    logging.error("No selected seats information available.")
                    display_mode = DisplayMode.MOVIE  # Reset to movie selection after notifying
        pg.display.flip()  # Update the display
        
    # movies = get_movies()
    # movie_id = None
    # while not movie_id:
    #     movie_id = select_movie(movies)
    # showtime = None
    # while not showtime:
    #     showtime = select_showtime(movie_id)
    # col, row_start, row_end = None, None, None
    # while not (col and row_start and row_end):
    #     col, row_start, row_end = select_seat(showtime)
    # seat_availabilities = check_seat_availability(showtime, row_start, row_end, col)
    # all_available = True
    # for row, col, available in seat_availabilities:
    #     if not available:
    #         print(f"❌ Seat at Row {row}, Column {col} is NOT available.")
    #         all_available = False
    # if all_available:
    #     print("✅ All selected seats are available!")
    

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    pg.init()
    pg.display.set_caption("Movie Seat Selection")
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    main()