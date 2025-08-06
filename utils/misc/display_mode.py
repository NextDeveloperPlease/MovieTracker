from enum import Enum

class DisplayMode(Enum):
    ''' Enum to represent the different display modes in the application.
        MOVIE: Display mode for movies.
        SHOWTIME: Display mode for showtimes.
        SEAT: Display mode for seat selection.
        NOTIFYING: Display mode for notifications.'''
    
    MOVIE = 1
    SHOWTIME = 2
    SEAT = 3
    NOTIFYING = 4
    
def update_display_mode(display_mode):
    ''' Updates the display mode based on the current mode.
        Args:
            display_mode (DisplayMode): The current display mode.
        Returns:
            DisplayMode: The updated display mode.
    '''
    if not isinstance(display_mode, DisplayMode):
        return display_mode
    
    match (display_mode):
        case DisplayMode.MOVIE:
            return DisplayMode.SHOWTIME
        case DisplayMode.SHOWTIME:
            return DisplayMode.SEAT
        case DisplayMode.SEAT:
            return DisplayMode.NOTIFYING
        case DisplayMode.NOTIFYING:
            return DisplayMode.MOVIE