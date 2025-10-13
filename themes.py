# themes.py

from colors import COLORS

APP_THEME_KEYS = [
    "background_color",
    "done_button_color"
]
ADD_TASKS_KEYS = [
    "add_tasks_choose_folder_color",
    "add_tasks_chosen_folder_color"
]
COMPLETE_TASKS_KEYS = [
    "complete_tasks_hub_folder_color",
    "complete_tasks_task_color"
]
REMOVE_TASKS_KEYS = [
    "remove_tasks_hub_folder_color",
    "remove_tasks_task_color"
]
HUB_BUTTON_COLOR_KEYS = [
    "add_spoons_color",
    "add_tasks_color",
    "manage_tasks_color",
    "inventory_color",
    "calendar_color",
    "social_color",
    "stats_color"
]
CALENDAR_COLOR_KEYS = [
    "calendar_current_day_color",
    "calendar_current_day_header_color",
    "calendar_previous_day_color",
    "calendar_previous_day_header_color",
    "calendar_next_day_color",
    "calendar_next_day_header_color",
    "calendar_month_color"
]
FOLDER_COLOR_KEYS = [
    "homework_fol_color",
    "chores_fol_color",
    "work_fol_color",
    "misc_fol_color"
]

THEME_APP = {            #background color        done button color
    "aquatic":          ["DEEP_AQUATIC_BLUE",    "MEDIUM_TURQUOISE"],
    "foresty":          ["DARK_OLIVE_GREEN",     "OLIVE_DRAB"],
    "girly_pop":        ["LIGHT_PINK",           "LAVENDER_BLUSH"],
    "vampire_goth":     ["MAROON",          "INDIGO"],
    "sunset_glow":      ["DARK_ORANGE",          "RED_ORANGE"],
    "light_academia":   ["BACKGROUND_IMAGE",     "MUTED_BROWN"],
    "retro":            ["CORAL",       "MUSTARD_YELLOW"],
    "minimalist":       ["WHITE",                "LIGHT_GRAY"],
    "cosmic":           ["DEEP_SPACE_PURPLE",    "SILVER_SAGE"],
    "autumn_harvest":   ["RUST",                 "DEEP_ORANGE"],
    "tropical_oasis":   ["TURQUOISE",            "VIBRANT_CORAL"],
    "pastel_dreams":    ["PALE_PINK",            "LAVENDER"],
    "steampunk":        ["BRASS",                "COPPER"],
    "cyberpunk":        ["NEBULA_PINK",            "ELECTRIC_BLUE"],
    "rustic_charm":     ["BROWN",           "OAK_WOOD"]
}
THEME_ADD_TASKS = {#add tasks choose folder color    add tasks chosen folder color
    "aquatic":        ["LIGHT_SEA_GREEN",   "DEEP_SKY_BLUE"],
    "foresty":        ["DARK_SEA_GREEN",    "SILVER_SAGE"],
    "girly_pop":      ["PALE_VIOLET_RED",   "LAVENDER"],
    "vampire_goth":   ["DARK_SLATE_GRAY",   "DIM_GRAY"],
    "sunset_glow":    ["ORANGE",            "TOMATO"],
    "light_academia": ["LIGHT_IVORY",       "SOFT_TAUPE"],
    "retro":          ["TEAL",              "TURQUOISE"],
    "minimalist":     ["SOFT_BLACK",        "WHITE"],
    "cosmic":         ["GALACTIC_BLUE",     "NEBULA_PINK"],
    "autumn_harvest": ["GOLD",     "BROWN"],
    "tropical_oasis": ["SUNFLOWER_YELLOW",   "GREEN"],
    "pastel_dreams":  ["PALE_MINT",         "BABY_BLUE"],
    "steampunk":      ["RUSTED_METAL",      "STEEL_GRAY"],
    "cyberpunk":      ["HACKER_GREEN",      "LIME_YELLOW"],
    "rustic_charm":   ["DEEP_GREEN",        "CREAM_WHITE"]
}

THEME_COMPLETE_TASKS = { #complete tasks hub folder color    complete tasks task color
    "aquatic":        ["DARK_CYAN",         "AQUAMARINE"],
    "foresty":        ["MEDIUM_SEA_GREEN",  "PALE_GREEN"],
    "girly_pop":      ["PLUM",              "ANTIQUE_WHITE"],
    "vampire_goth":   ["MAROON",            "DARK_RED"],
    "sunset_glow":    ["CORAL",             "GOLD"],
    "light_academia": ["WARM_GRAY",         "SAGE_GREEN"],
    "retro":          ["PEACH",             "MINT_GREEN"],
    "minimalist":     ["DARK_GRAY",         "LIGHT_GRAY"],
    "cosmic":         ["BLACK_HOLE",        "STARFIRE_YELLOW"],
    "autumn_harvest": ["CRIMSON",           "BURNISHED_RED"],
    "tropical_oasis": ["DEEP_BLUE",         "CORAL"],
    "pastel_dreams":  ["PASTEL_YELLOW",     "PALE_PINK"],
    "steampunk":      ["GOLDEN_COG",        "BROWN"],
    "cyberpunk":      ["BLACK_HOLE",    "CYBER_ORANGE"],
    "rustic_charm":   ["BLACK_HOLE",          "SUNFLOWER_YELLOW"]
}

THEME_REMOVE_TASKS = { #remove tasks hub folder color    remove tasks task color
    "aquatic":        ["BLUE_LAGOON",       "TURQUOISE"],
    "foresty":        ["FOREST_GREEN",      "LAWN_GREEN"],
    "girly_pop":      ["LIGHT_SALMON",      "MISTY_ROSE"],
    "vampire_goth":   ["DARK_SLATE_BLUE",   "DARK_SLATE_GRAY"],
    "sunset_glow":    ["LIGHT_PINK",        "LIGHT_SALMON"],
    "light_academia": ["DARK_OLIVE",        "SAGE_GREEN"],
    "retro":          ["BROWN",             "TANGERINE"],
    "minimalist":     ["SOFT_BLACK",        "WHITE"],
    "cosmic":         ["RED",        "HACKER_GREEN"],
    "autumn_harvest": ["BURNISHED_ORANGE",  "TERRACOTTA"],
    "tropical_oasis": ["AQUA_BLUE",         "SEAFOAM_GREEN"],
    "pastel_dreams":  ["PALE_LAVENDER",     "MINT_GREEN"],
    "steampunk":      ["BURNISHED_COPPER",  "VINTAGE_GOLD"],
    "cyberpunk":      ["ELECTRIC_PURPLE",   "AQUA_BLUE"],
    "rustic_charm":   ["BURGUNDY_RED",      "TERRACOTTA"]
}

THEME_HUB_BUTTONS = { #add spoons color    add tasks color    complete tasks color    inventory color    calendar color    shop color    stats color
    "aquatic":        ["DEEP_SKY_BLUE", "DARK_CYAN",      "AQUAMARINE",
                       "LIGHT_SEA_GREEN", "BLUE_LAGOON", "DEEP_AQUATIC_BLUE", "LIGHT_SEA_GREEN"],
    "foresty":        ["OLIVE_DRAB",    "DARK_SEA_GREEN", "FOREST_GREEN",
                       "MEDIUM_SEA_GREEN", "LAWN_GREEN", "SEAFOAM_GREEN",     "MEDIUM_SEA_GREEN"],
    "girly_pop":      ["LAVENDER_BLUSH","PALE_VIOLET_RED","ANTIQUE_WHITE",
                       "LAVENDER",      "PLUM",        "LIGHT_PINK",       "LAVENDER"],
    "vampire_goth":   ["INDIGO",        "DARK_SLATE_GRAY","DARK_RED",
                       "DIM_GRAY",      "MAROON",      "CRIMSON",      "MAROON"],
    "sunset_glow":    ["TOMATO",        "ORANGE",       "CORAL",
                       "GOLD",          "DARK_ORANGE", "RED_ORANGE",       "ORANGE"],
    "light_academia": ["SOFT_TAUPE",    "WARM_GRAY",    "SAGE_GREEN",
                       "LIGHT_IVORY",   "WARM_GRAY",    "SOFT_BEIGE",       "SOFT_TAUPE"],
    "retro":          ["MUSTARD_YELLOW","PEACH",        "MINT_GREEN",
                       "CORAL","BROWN",        "TEAL",             "CORAL"],
    "minimalist":     ["DARK_GRAY",     "SOFT_BLACK",   "LIGHT_GRAY",
                       "LIGHT_GRAY",    "DARK_GRAY",    "WHITE",            "SOFT_BLACK"],
    "cosmic":         ["NEBULA_PINK",   "BLACK_HOLE",   "STARFIRE_YELLOW",
                       "GALACTIC_BLUE", "BLACK_HOLE",   "DEEP_SPACE_PURPLE","GALACTIC_BLUE"],
    "autumn_harvest": ["GOLD","CRIMSON",       "BURNISHED_RED",
                       "RUST",         "BROWN",         "RUST",            "BROWN"],
    "tropical_oasis": ["SUNFLOWER_YELLOW","DEEP_BLUE",   "CORAL",
                       "GREEN",    "AQUA_BLUE",   "TURQUOISE",       "VIBRANT_CORAL"],
    "pastel_dreams":  ["LAVENDER","PALE_MINT",   "PALE_PINK",
                       "PALE_PINK",     "PASTEL_YELLOW","PALE_PINK",       "LAVENDER"],
    "steampunk":      ["STEEL_GRAY",     "RUSTED_METAL","BROWN",
                       "BRASS",         "BURNISHED_COPPER","STEEL_GRAY",    "BRASS"],
    "cyberpunk":      ["LIME_YELLOW",    "BLACK_HOLE","CYBER_ORANGE",
                       "HACKER_GREEN",  "BLACK_HOLE","NEBULA_PINK",       "ELECTRIC_BLUE"],
    "rustic_charm":   ["CREAM_WHITE",    "DEEP_GREEN",   "SUNFLOWER_YELLOW",
                       "BROWN",    "BLACK_HOLE",     "BROWN",      "CREAM_WHITE"]
}

THEME_CALENDAR = { #urrent day color    current day header color    previous day color    cprevious day header color    next day color    next day header color   month color
    "aquatic":        ["DEEP_AQUATIC_BLUE","MEDIUM_TURQUOISE","LIGHT_SEA_GREEN","DEEP_SKY_BLUE",
                       "AQUAMARINE","DARK_CYAN","BLUE_LAGOON"],
    "foresty":        ["DARK_OLIVE_GREEN","OLIVE_DRAB","DARK_SEA_GREEN","MEDIUM_SEA_GREEN",
                       "PALE_GREEN","FOREST_GREEN","DARK_OLIVE_GREEN"],
    "girly_pop":      ["LIGHT_PINK","LAVENDER_BLUSH","PALE_VIOLET_RED","LAVENDER",
                       "PLUM","ANTIQUE_WHITE","LIGHT_PINK"],
    "vampire_goth":   ["CRIMSON","INDIGO","DARK_SLATE_GRAY","DIM_GRAY",
                       "MAROON","DARK_RED","CRIMSON"],
    "sunset_glow":    ["DARK_ORANGE","RED_ORANGE","ORANGE","TOMATO",
                       "CORAL","GOLD","DARK_ORANGE"],
    "light_academia": ["SOFT_BEIGE","MUTED_BROWN","LIGHT_IVORY","SOFT_TAUPE",
                       "SAGE_GREEN","WARM_GRAY","SAGE_GREEN"],
    "retro":          ["CORAL","MUSTARD_YELLOW","PEACH","MINT_GREEN",
                       "TURQUOISE","BROWN","TANGERINE"],
    "minimalist":     ["WHITE","LIGHT_GRAY","SOFT_BLACK","DARK_GRAY",
                       "LIGHT_GRAY","SOFT_BLACK","DARK_GRAY"],
    "cosmic":         ["DEEP_SPACE_PURPLE","SILVER_SAGE","GALACTIC_BLUE","NEBULA_PINK",
                       "STARFIRE_YELLOW","RED","HACKER_GREEN"],
    "autumn_harvest": ["RUST","DEEP_ORANGE","GOLD","BROWN",
                       "BURNISHED_RED","CRIMSON","TERRACOTTA"],
    "tropical_oasis": ["TURQUOISE","VIBRANT_CORAL","SUNFLOWER_YELLOW","GREEN",
                       "CORAL","DEEP_BLUE","SEAFOAM_GREEN"],
    "pastel_dreams":  ["PALE_PINK","LAVENDER","PALE_MINT","BABY_BLUE",
                       "PALE_PINK","PASTEL_YELLOW","MINT_GREEN"],
    "steampunk":      ["BRASS","COPPER","RUSTED_METAL","STEEL_GRAY",
                       "GOLDEN_COG","BROWN","VINTAGE_GOLD"],
    "cyberpunk":      ["NEBULA_PINK","ELECTRIC_BLUE","HACKER_GREEN","LIME_YELLOW",
                       "CYBER_ORANGE","ELECTRIC_PURPLE","AQUA_BLUE"],
    "rustic_charm":   ["BROWN","OAK_WOOD","DEEP_GREEN","CREAM_WHITE",
                       "SUNFLOWER_YELLOW","BURGUNDY_RED","TERRACOTTA"]
}

THEME_FOLDERS = { #homework fol color    chores fol color    work fol color    misc fol color
    "aquatic":        ["DEEP_AQUATIC_BLUE","MEDIUM_TURQUOISE","DEEP_SKY_BLUE","TURQUOISE"],
    "foresty":        ["OLIVE_DRAB","DARK_SEA_GREEN","FOREST_GREEN","MEDIUM_SEA_GREEN"],
    "girly_pop":      ["PALE_VIOLET_RED","LAVENDER_BLUSH","PLUM","MISTY_ROSE"],
    "vampire_goth":   ["INDIGO","DARK_SLATE_GRAY","MAROON","DARK_SLATE_GRAY"],
    "sunset_glow":    ["RED_ORANGE","ORANGE","CORAL","LIGHT_SALMON"],
    "light_academia": ["SOFT_BEIGE","MUTED_BROWN","SOFT_TAUPE","SAGE_GREEN"],
    "retro":          ["CORAL","MUSTARD_YELLOW","TURQUOISE","TANGERINE"],
    "minimalist":     ["WHITE","LIGHT_GRAY","SOFT_BLACK","DARK_GRAY"],
    "cosmic":         ["DEEP_SPACE_PURPLE","SILVER_SAGE","NEBULA_PINK","RED"],
    "autumn_harvest": ["RUST","DEEP_ORANGE","BROWN","TERRACOTTA"],
    "tropical_oasis": ["TURQUOISE","VIBRANT_CORAL","GREEN","SEAFOAM_GREEN"],
    "pastel_dreams":  ["PALE_PINK","LAVENDER","BABY_BLUE","MINT_GREEN"],
    "steampunk":      ["BRASS","COPPER","STEEL_GRAY","BROWN"],
    "cyberpunk":      ["NEBULA_PINK","ELECTRIC_BLUE","LIME_YELLOW","CYBER_ORANGE"],
    "rustic_charm":   ["BROWN","OAK_WOOD","DEEP_GREEN","TERRACOTTA"]
}



THEMES = {}

theme_sources = [
    (APP_THEME_KEYS, THEME_APP),
    (ADD_TASKS_KEYS, THEME_ADD_TASKS),
    (COMPLETE_TASKS_KEYS, THEME_COMPLETE_TASKS),
    (REMOVE_TASKS_KEYS, THEME_REMOVE_TASKS),
    (HUB_BUTTON_COLOR_KEYS, THEME_HUB_BUTTONS),
    (CALENDAR_COLOR_KEYS, THEME_CALENDAR),
    (FOLDER_COLOR_KEYS, THEME_FOLDERS)
]

for theme_name in THEME_APP:  # Use any master theme list here
    THEMES[theme_name] = {}
    for keys, color_dict in theme_sources:
        for key, color_name in zip(keys, color_dict[theme_name]):
            THEMES[theme_name][key] = COLORS[color_name]



DROPDOWN_LISTS = {
    "aquatic": {
        "dropdown_colors_list": [
            ["background", COLORS["DEEP_AQUATIC_BLUE"]],
            ["done button", COLORS["MEDIUM_TURQUOISE"]],
            ["folder choices", COLORS["LIGHT_SEA_GREEN"]],
            ["chosen folder", COLORS["DEEP_SKY_BLUE"]],
            ["choose folder C", COLORS["DARK_CYAN"]],
            ["complete task", COLORS["AQUAMARINE"]],
            ["choose folder R", COLORS["BLUE_LAGOON"]],
            ["remove task", COLORS["TURQUOISE"]],
        ],
        "dropdown_hub_colors_list": [
            ["add spoons", COLORS["DEEP_SKY_BLUE"]],
            ["add tasks", COLORS["DARK_CYAN"]],
            ["complete tasks", COLORS["AQUAMARINE"]],
            ["remove tasks", COLORS["TURQUOISE"]],
            ["daily schedule", COLORS["LIGHT_SEA_GREEN"]],
            ["calendar", COLORS["BLUE_LAGOON"]],
            ["shop", COLORS["DEEP_AQUATIC_BLUE"]],
        ],
        "dropdown_calendar_colors_list": [
            ["current day", COLORS["DEEP_AQUATIC_BLUE"]],
            ["cur day header", COLORS["MEDIUM_TURQUOISE"]],
            ["previous day", COLORS["LIGHT_SEA_GREEN"]],
            ["pre day header", COLORS["DEEP_SKY_BLUE"]],
            ["next day", COLORS["AQUAMARINE"]],
            ["next day header", COLORS["DARK_CYAN"]],
            ["month pre/next", COLORS["BLUE_LAGOON"]],
            ["homework fol", COLORS["DEEP_AQUATIC_BLUE"]],
            ["chores fol", COLORS["MEDIUM_TURQUOISE"]],
            ["work fol", COLORS["DEEP_SKY_BLUE"]],
            ["misc fol", COLORS["TURQUOISE"]],
        ],
    },
    "foresty": {
        "dropdown_colors_list": [
            ["background", COLORS["DARK_OLIVE_GREEN"]],
            ["done button", COLORS["OLIVE_DRAB"]],
            ["folder choices", COLORS["DARK_SEA_GREEN"]],
            ["chosen folder", COLORS["SILVER_SAGE"]],
            ["choose folder C", COLORS["MEDIUM_SEA_GREEN"]],
            ["complete task", COLORS["PALE_GREEN"]],
            ["choose folder R", COLORS["FOREST_GREEN"]],
            ["remove task", COLORS["LAWN_GREEN"]],
        ],
        "dropdown_hub_colors_list": [
            ["add spoons", COLORS["OLIVE_DRAB"]],
            ["add tasks", COLORS["DARK_SEA_GREEN"]],
            ["complete tasks", COLORS["PALE_GREEN"]],
            ["remove tasks", COLORS["FOREST_GREEN"]],
            ["daily schedule", COLORS["MEDIUM_SEA_GREEN"]],
            ["calendar", COLORS["LAWN_GREEN"]],
            ["shop", COLORS["DARK_OLIVE_GREEN"]],
        ],
        "dropdown_calendar_colors_list": [
            ["current day", COLORS["DARK_OLIVE_GREEN"]],
            ["cur day header", COLORS["OLIVE_DRAB"]],
            ["previous day", COLORS["DARK_SEA_GREEN"]],
            ["pre day header", COLORS["MEDIUM_SEA_GREEN"]],
            ["next day", COLORS["PALE_GREEN"]],
            ["next day header", COLORS["FOREST_GREEN"]],
            ["month pre/next", COLORS["DARK_OLIVE_GREEN"]],
            ["homework fol", COLORS["OLIVE_DRAB"]],
            ["chores fol", COLORS["DARK_SEA_GREEN"]],
            ["work fol", COLORS["FOREST_GREEN"]],
            ["misc fol", COLORS["MEDIUM_SEA_GREEN"]],
        ],
    },
    "girly_pop": {
        "dropdown_colors_list": [
            ["background", COLORS["LIGHT_PINK"]],
            ["done button", COLORS["LAVENDER_BLUSH"]],
            ["folder choices", COLORS["PALE_VIOLET_RED"]],
            ["chosen folder", COLORS["LAVENDER"]],
            ["choose folder C", COLORS["PLUM"]],
            ["complete task", COLORS["ANTIQUE_WHITE"]],
            ["choose folder R", COLORS["LIGHT_SALMON"]],
            ["remove task", COLORS["MISTY_ROSE"]],
        ],
        "dropdown_hub_colors_list": [
            ["add spoons", COLORS["LAVENDER_BLUSH"]],
            ["add tasks", COLORS["PALE_VIOLET_RED"]],
            ["complete tasks", COLORS["ANTIQUE_WHITE"]],
            ["remove tasks", COLORS["LIGHT_SALMON"]],
            ["daily schedule", COLORS["LAVENDER"]],
            ["calendar", COLORS["PLUM"]],
            ["shop", COLORS["LIGHT_PINK"]],
        ],
        "dropdown_calendar_colors_list": [
            ["current day", COLORS["LIGHT_PINK"]],
            ["cur day header", COLORS["LAVENDER_BLUSH"]],
            ["previous day", COLORS["PALE_VIOLET_RED"]],
            ["pre day header", COLORS["LAVENDER"]],
            ["next day", COLORS["PLUM"]],
            ["next day header", COLORS["ANTIQUE_WHITE"]],
            ["month pre/next", COLORS["LIGHT_PINK"]],
            ["homework fol", COLORS["PALE_VIOLET_RED"]],
            ["chores fol", COLORS["LAVENDER_BLUSH"]],
            ["work fol", COLORS["PLUM"]],
            ["misc fol", COLORS["MISTY_ROSE"]],
        ],
    },
    "vampire_goth": {
        "dropdown_colors_list": [
            ["background", COLORS["CRIMSON"]],
            ["done button", COLORS["INDIGO"]],
            ["folder choices", COLORS["DARK_SLATE_GRAY"]],
            ["chosen folder", COLORS["DIM_GRAY"]],
            ["choose folder C", COLORS["MAROON"]],
            ["complete task", COLORS["DARK_RED"]],
            ["choose folder R", COLORS["DARK_SLATE_BLUE"]],
            ["remove task", COLORS["DARK_SLATE_GRAY"]],
        ],
        "dropdown_hub_colors_list": [
            ["add spoons", COLORS["INDIGO"]],
            ["add tasks", COLORS["DARK_SLATE_GRAY"]],
            ["complete tasks", COLORS["DARK_RED"]],
            ["remove tasks", COLORS["DARK_SLATE_BLUE"]],
            ["daily schedule", COLORS["DIM_GRAY"]],
            ["calendar", COLORS["MAROON"]],
            ["shop", COLORS["CRIMSON"]],
        ],
        "dropdown_calendar_colors_list": [
            ["current day", COLORS["CRIMSON"]],
            ["cur day header", COLORS["INDIGO"]],
            ["previous day", COLORS["DARK_SLATE_GRAY"]],
            ["pre day header", COLORS["DIM_GRAY"]],
            ["next day", COLORS["MAROON"]],
            ["next day header", COLORS["DARK_RED"]],
            ["month pre/next", COLORS["CRIMSON"]],
            ["homework fol", COLORS["INDIGO"]],
            ["chores fol", COLORS["DARK_SLATE_GRAY"]],
            ["work fol", COLORS["MAROON"]],
            ["misc fol", COLORS["DARK_SLATE_GRAY"]],
        ],
    },
    "sunset_glow": {
        "dropdown_colors_list": [
            ["background", COLORS["DARK_ORANGE"]],
            ["done button", COLORS["RED_ORANGE"]],
            ["folder choices", COLORS["ORANGE"]],
            ["chosen folder", COLORS["TOMATO"]],
            ["choose folder C", COLORS["CORAL"]],
            ["complete task", COLORS["GOLD"]],
            ["choose folder R", COLORS["LIGHT_PINK"]],
            ["remove task", COLORS["LIGHT_SALMON"]],
        ],
        "dropdown_hub_colors_list": [
            ["add spoons", COLORS["TOMATO"]],
            ["add tasks", COLORS["ORANGE"]],
            ["complete tasks", COLORS["CORAL"]],
            ["remove tasks", COLORS["LIGHT_SALMON"]],
            ["daily schedule", COLORS["GOLD"]],
            ["calendar", COLORS["DARK_ORANGE"]],
            ["shop", COLORS["RED_ORANGE"]],
        ],
        "dropdown_calendar_colors_list": [
            ["current day", COLORS["DARK_ORANGE"]],
            ["cur day header", COLORS["RED_ORANGE"]],
            ["previous day", COLORS["ORANGE"]],
            ["pre day header", COLORS["TOMATO"]],
            ["next day", COLORS["CORAL"]],
            ["next day header", COLORS["GOLD"]],
            ["month pre/next", COLORS["DARK_ORANGE"]],
            ["homework fol", COLORS["RED_ORANGE"]],
            ["chores fol", COLORS["ORANGE"]],
            ["work fol", COLORS["CORAL"]],
            ["misc fol", COLORS["LIGHT_SALMON"]],
        ],
    },
}