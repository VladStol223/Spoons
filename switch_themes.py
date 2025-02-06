from themes import THEMES, DROPDOWN_LISTS

def switch_theme(theme_name, globals_dict):
    global current_theme
    """
    Switches the theme by updating global variables based on the selected theme.
    
    Args:
        theme_name (str): The name of the theme to apply.
        globals_dict (dict): The globals() dictionary to update global variables.
    """
    if theme_name not in THEMES or theme_name not in THEMES:
        raise ValueError(f"Theme '{theme_name}' is not defined.")
    
    theme = THEMES[theme_name]

    # Update color variables
    for key, value in theme.items():
        if key in globals_dict:
            globals_dict[key] = value
        else:
            print(f"Warning: Global variable '{key}' is not defined in main.py.")

    current_theme = theme_name
    return current_theme