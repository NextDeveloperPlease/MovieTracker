import json
import os
import logging

DEFAULT_SETTINGS = {
    "theme": "light",
    "fullscreen": False,
    "res_width": 800,
    "res_height": 600,
    "movie_col": 2,
    "showtime_col": 3
}

class Settings:
    _instance = None
    def __new__(cls, path="Default Path"): # TODO: Change the dafault path
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._path = path
            cls._instance._settings = {}
            cls._instance._load()
        return cls._instance
    
    def _load(self):
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
        try:
            with open(self._path, 'w') as f:
                json.dump(self._settings, f, indent=4)
        except Exception as e:
            logging.error(f'Error saving settings: {e}')
            
    def get(self, key, default=None):
        return self._settings.get(key, default)
    
    def set(self, key, value):
        if not value:
            return
        
        if self._settings.get(key):
            self._settings[key] = value
            
    