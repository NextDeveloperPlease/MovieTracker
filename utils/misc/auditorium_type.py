from enum import Enum

# Currently unused, but will be used in the future to separate the showtimes into different show/auditorium types.

class ShowType(Enum):
    ''' Enum to represent the type of show.
        STANDARD: Standard show type.
        THREE_D: 3D show type.
    '''
    
    STANDARD = 0
    THREE_D = 1
    
class AuditoriumType(Enum):
    ''' Enum to represent the type of auditorium.
        REGULAR: Regular auditorium type.
        D_BOX: D-BOX auditorium type.
    '''
    
    REGULAR = 0
    D_BOX = 1