from enum import Enum

class DisplayMode(Enum):
    MOVIE = 1
    SHOWTIME = 2
    SEAT = 3
    NOTIFYING = 4
    
def update_display_mode(display_mode):
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