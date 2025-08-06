from enum import Enum

class GenerationStatus(Enum):
    ''' Enum to represent the status of a generation process.
        SUCCESS: The generation was successful.
        FAILURE: The generation failed.'''
    
    SUCCESS = True
    FAILURE = False