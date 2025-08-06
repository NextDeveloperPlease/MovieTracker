from typing import List, Dict, Optional, Callable, Tuple, Union
from typing import TypeVar as T
from utils.assets.button import Button
from utils.data_structures.showtime import Showtime
from utils.data_structures.movie import Movie
from utils.data_structures.button_spec import ButtonSpec
import logging
import pygame as pg

def is_list_objects(obj_list:List, expected_type: type) -> bool:
    ''' Checks if the provided list contains objects of the expected type.
        Args:
            obj_list (List): The list to check.
            expected_type (type): The type that each object in the list should be.
        Returns:
            bool: True if all objects in the list are of the expected type, False otherwise.'''
    return isinstance(obj_list, list) and all(isinstance(item, expected_type) for item in obj_list)   

def validate_button_specs(specs: Dict[str, Union[
    List[ButtonSpec],
    Dict[str, Union[type, int]]
]]) -> bool:
    ''' Validates the button specifications.
        Args:
            specs (Dict): The button specifications to validate.
        Returns:
            bool: True if the specifications are valid, False otherwise.
    '''
    if not isinstance(specs, dict):
        print('Not Dict')
        logging.error("Button specifications must be a dictionary.")
        return False
    if not specs: # This is weird, but I handle empty specs in the main logic already, so if it is empty, just return True.
        logging.error("Button specification is empty.")
        return True
    if 'data' not in specs or 'metadata' not in specs:
        print('No data or metadata')
        logging.error("Button specifications must contain 'data' and 'metadata' keys.")
        return False
    if not is_list_objects(specs['data'], ButtonSpec):
        print('Not list of ButtonSpec')
        logging.error("Button specifications data must be a list of ButtonSpec objects.")
        return False
    if not isinstance(specs['metadata'], dict) or 'obj_type' not in specs['metadata']:
        print('No obj_type in metadata')
        logging.error("Button specifications metadata must be a dictionary with an 'obj_type' key.")
        return False
    if 'num_cols' in specs['metadata'] and not isinstance(specs['metadata']['num_cols'], int):
        print('num_cols not int')
        logging.error("Button specifications metadata 'num_cols' must be an integer.")
        return False
    return True

def convert_button_index_to_position(i:int, num_of_cols:int, width:int = 180, height:int = 80, h_spacing:int = 5, v_spacing:int = 5, button_max_height:int = 550, screen_width:int = 800, screen_height:int = 600) -> Tuple[int, int]:
    """Converts a button index to its x, y position based on the number of columns.
    Args:
        i (int): The index of the button.
        num_of_cols (int): The number of columns in the layout.
        width (int): The width of each button.
        height (int): The height of each button.
        h_spacing (int): The horizontal spacing between buttons.
        v_spacing (int): The vertical spacing between buttons.
        button_max_height (int): The maximum height for the buttons.
        screen_width (int): The width of the screen.
        screen_height (int): The height of the screen.
    Returns:
        Tuple[int, int]: The x, y position of the button.
    This function needs to be updated. It doesn't display button positions correctly.
    """
    if num_of_cols <= 0:
        logging.error("Number of columns must be greater than 0.")
        return 0, 0
    if h_spacing < 0 or v_spacing < 0:
        logging.error("Horizontal and vertical spacing must be non-negative.")
        return 0, 0
    center_x = screen_width / 2
    center_y = screen_height / 2
    
    total_width = (width + h_spacing * 2) * num_of_cols - 2 * h_spacing
    
    width_center = total_width / 2
    
    top_left_x = center_x - width_center
    top_left_y = button_max_height
    
    x = top_left_x + ((i % num_of_cols) * (width + h_spacing))
    y = top_left_y + ((i // num_of_cols) * (height + v_spacing))
    
    return x,y
    #return 50 + (i % num_of_cols) * 200, 200 + (i // num_of_cols) * 100

def button_generation(items: List[T], 
                      num_of_cols:int, 
                      function: Optional[Callable[[T], None]] = None,
                      text_extractor: Optional[Callable[[T], str]] = None
                      ) -> List[Button]:
    '''Generates a list of buttons from the provided items.
        Args:
            items (List[T]): The items to generate buttons from.
            num_of_cols (int): The number of columns for the button layout.
            function (Optional[Callable[[T], None]]): The function to call when the button is clicked.
            text_extractor (Optional[Callable[[T], str]]): The function to extract text from the item for the button label.
        Returns:
            List[Button]: A list of generated buttons.
        If no items are provided, it returns an empty list.
        This function isn't used anymore.
    '''
    if not items:
        logging.warning("No items provided for button generation.")
        return []
    
    buttons = []
    
    for i, item in enumerate(items):
        x,y = convert_button_index_to_position(i, num_of_cols)
        button_text = text_extractor(item) if text_extractor else str(item)

        button = Button(text=button_text,
                        x=x,
                        y=y,
                        width=180,
                        height=80,
                        action=lambda it=item: function(it) if function else None)

        buttons.append(button)
            
    return buttons

def button_generation_from_specs(
    specs: List[ButtonSpec], 
    num_of_cols:int,
    width: int = 180,
    height: int = 80,
    h_spacing: int = 5,
    v_spacing: int = 5,
    screen_width: int = 800,
    screen_height: int = 600,
    button_max_height: int = 550,
    default_color: Optional[pg.Color] = None) -> List[Button]:
    '''Generates a list of buttons from the provided button specifications.
        Args:
            specs (List[ButtonSpec]): The button specifications to generate buttons from.
            num_of_cols (int): The number of columns for the button layout.
            width (int): The width of each button.
            height (int): The height of each button.
            h_spacing (int): The horizontal spacing between buttons.
            v_spacing (int): The vertical spacing between buttons.
            screen_width (int): The width of the screen.
            screen_height (int): The height of the screen.
            button_max_height (int): The maximum height for the buttons.
            default_color (Optional[pg.Color]): The default color for the buttons if not specified in the specs.
        Returns:
            List[Button]: A list of generated buttons.
        If no specifications are provided, it returns an empty list.
    '''
    
    if not specs:
        logging.warning("No button specifications provided for button generation.")
        return []
    
    buttons = []
    
    for i, spec in enumerate(specs):
        if spec.action is None:
            logging.error(f"Button specification at index {i} has no action defined.")
            return []
        x, y = convert_button_index_to_position(
            i=i, 
            num_of_cols=num_of_cols, 
            width=width, 
            height=height, 
            h_spacing=h_spacing, 
            v_spacing=v_spacing, 
            button_max_height=button_max_height, 
            screen_width=screen_width, 
            screen_height=screen_height)

        button = Button(text=spec.label,
                        x=x,
                        y=y,
                        width=width,
                        height=height,
                        color=spec.color if spec.color else default_color,
                        action=spec.action)

        buttons.append(button)
            
    return buttons