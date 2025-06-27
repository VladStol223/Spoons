from themes import THEMES

def switch_theme(theme_name, globals_dict):
    global current_theme
    if theme_name not in THEMES:
        print(f"Theme '{theme_name}' is not defined; falling back to foresty.")
        theme_name = "foresty"

    theme = THEMES[theme_name]

    for key, value in theme.items():
        if key in globals_dict:
            globals_dict[key] = value
        else:
            print(f"Warning: Global variable '{key}' is not defined.")

    current_theme = theme_name

    # *** new: keep the 'theme' var in sync so save_data() sees it ***
    if 'theme' in globals_dict:
        globals_dict['theme'] = theme_name

    return current_theme
