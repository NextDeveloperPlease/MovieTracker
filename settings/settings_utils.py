import json
import os
import logging
import pygame as pg

# Current implementation of storing settings. This will likely be changed in the future.
DEFAULT_SETTINGS = {
    "theme": "light",
    "fullscreen": False,
    "res_width": 800,
    "res_height": 600,
    "movie_col": 4,
    "showtime_col": 3,
    "seat_col": 16,
    "default_button_cols": 2,
    "seat_rect_dim": 50,
    "default_seat_color": (0, 255, 0),
    "default_seat_selected_color": (255, 255, 0),
    "default_seat_unavailable_color": (255, 0, 0),
    "default_button_color": (0, 0, 255),
    "default_button_hover_color": (0, 0, 200),
    "default_button_text_color": (255, 255, 255),
    "default_button_font_size": 36,
    "default_font": "Arial",
    "default_button_width": 180,
    "default_button_height": 80,
    "default_background_color": (0, 0, 0),
    "default_button_max_height": 550
}

class Settings:
    ''' Singleton class to manage application settings. 
        This class loads settings from a JSON file and provides methods to get and set settings.
    '''
    _instance = None
    def __new__(cls, path="Default Path"): # TODO: Change the default path
        ''' Creates a singleton instance of the Settings class.
            Args:
                path (str): The path to the settings file. Defaults to "Default Path".
            Returns:
                Settings: The singleton instance of the Settings class.
        '''
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._path = path
            cls._instance._settings = {}
            cls._instance._load()
        return cls._instance
    
    def _load(self):
        ''' Loads settings from the JSON file specified by the path.
            If the file does not exist, it initializes with default settings.
        '''
        if os.path.exists(self._path):
            try:
                with open(self._path, 'r') as f:
                    self._settings = json.load(f)
            except Exception as e:
                logging.error(f'Error loading settings: {e}')
                self._settings = DEFAULT_SETTINGS.copy()
        else:
            self._settings = DEFAULT_SETTINGS.copy()
            
    def save(self):
        ''' Saves the current settings to the JSON file specified by the path.
            If the file cannot be saved, it logs an error.
        '''
        try:
            with open(self._path, 'w') as f:
                json.dump(self._settings, f, indent=4)
        except Exception as e:
            logging.error(f'Error saving settings: {e}')
            
    def get(self, key, default=None):
        ''' Gets the value of a setting by key.
            Args:
                key (str): The key of the setting to retrieve.
                default: The default value to return if the key does not exist.
            Returns:
                The value of the setting or the default value if the key does not exist.
        '''
        return self._settings.get(key, default)
    
    def set(self, key, value):
        ''' Sets the value of a setting by key.
            Args:
                key (str): The key of the setting to set.
                value: The value to set for the setting.
            If the value is None, it does nothing.
        '''
        if not value:
            return
        
        if self._settings.get(key):
            self._settings[key] = value
            
    