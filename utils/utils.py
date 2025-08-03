from typing import List

def is_list_objects(obj_list:List, expected_type: type) -> bool:
    return isinstance(obj_list, list) and all(isinstance(item, expected_type) for item in obj_list)       
 
def convert_button_index_to_position(i, num_of_cols:int):
    return 50 + (i % num_of_cols) * 200, 200 + (i // num_of_cols) * 100