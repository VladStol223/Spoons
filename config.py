# Spoons/config.py
import pygame
import os
from datetime import datetime
from colors import COLORS
for name, value in COLORS.items():
    globals()[name] = value
    
# Initialize pygame font
pygame.font.init()

screen_height = 540
screen_width = 960

total_content_height = 0
frame_buttons = []

font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen_height * 0.06))
big_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen_height * 0.067))
bigger_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen_height * 0.075))
small_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen_height * 0.047))
smaller_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen_height * 0.033))

#input buttons
input_active = False

# Date Variables
current_month = datetime.now().month
current_day = datetime.now().strftime('%d')
displayed_month = datetime.now().month
displayed_year = datetime.now().year

# Spoon Name
spoon_name = "Spoons"


import os
import pygame

# 0) Wherever you keep your images:
images_dir = "images"

# 1) Declare your categories exactly as you did before:
image_categories = {
    'avatarBackgrounds': {
        'background_image':        ('background.png', (210, 105)),
        'dark_background_image':   ('dark_background.png', (210, 105)),
        'window_one_image':        ('window1.png', (26, 31)),
        'window_flower_one_image': ('windowFlower1.png', (26, 31)),
        'light_image':             ('light.png', (80,80)),
        'bookshelf_image':         ('bookshelf.png', (45, 47)),
        'lamp_image':              ('lamp.png', (22,27)),
        'round_table_one_image':   ('roundTable1.png', (38,36)),
        'vlad_avatar_image':       ('vladavatar.png', (18, 43)),
    },
    'border': {
        'corner':          ('borderCorner.png',(12,12)),
        'edge1':           ('border1.png',(6,12)),
        'edge2':           ('border2.png',(6,12)),
        'tcorner':         ('borderTcorner.png',(14,12)),
        'calendar_border': ('borderCalendarLeft.png',(9,24)),
    },
    'hubIcons': {
        'add_spoons_icon':  ('addSpoonsIcon.png',(28,28)),
        'add_task_icon':    ('addTasksIcon.png',(28,28)),
        'manage_task_icon': ('manageTasksIcon.png',(28,28)),
        'inventory_icon':   ('inventoryIcon.png',(28,28)),
        'calendar_icon':    ('calendarIcon.png',(42,42)),
        'shop_icon':        ('shopIcon.png',(28,28)),
        'settings_icon':    ('settingsIcon.png',(28,28)),
    },
    'spoonIcons': {
        'spoon_image':        ('spoon.png',(33,33)),
        'battery_image':      ('greenBattery.png',(33,33)),
        'star_image':         ('star.png',(33,33)),
        'potion_image':       ('potion.png',(33,33)),
        'yourdidit_image':    ('yourdidit.png',(33,33)),
        'mike_image':         ('mike.png', (33,33)),
        'lightningface_image':('lightningface.png', (33,33)),
        'diamond_image' :     ('diamond.png', (33,33)),
        'starfruit_image':    ('starfruit.png', (33,33)),
        'strawberry_image':   ('strawberry.png', (33,33)),
        'terstar_image':      ('terstar.png', (33,33)),
        'hcheart_image':            ('hcheart.png', (33, 33)),
        'beer_image':               ('beer.png', (33,33)),
        'drpepper_image':           ('drpepper.png', (33,33)), 
    },
    'restIcons': {
        'short_rest_icon': ('shortRestIcon.png',(790,790)),
        'half_rest_icon':  ('halfRestIcon.png',(864,864)),
        'full_rest_icon':  ('fullRestIcon.png',(820,820)),
    },
    'hotbar': {
        'coin_image': ('coin.png',(15,17)),
        'xp_bar':     ('xpBar.png',(155,30)),
    },
    'manillaFolder': {
        'manilla_folder':('manillaFolder.png',(150,62)),
        'manilla_folder_open':('manillaFolderOpen.png',(150,62)),
        'manilla_folder_tab': ('manillaFolderTab.png',(48,7)),
        'manilla_folder_full':('manillaFolderFull.png',(150,83)),
    },
    'taskBorder': {
        'task_spoons_border':      ('taskSpoonsBorder.png',(750,50)),
        'progress_bar_spoon_siding':('progressBarSpoonSiding.png',(6,34)),
        'progress_bar_spoon_top':    ('progressBarSpoonTop.png',(10,2)),
        'remove_edit_icons':         ('removeEditIcons.png',(20,40)),
        'task_label_border_hover':       ('taskLabelBorderHover.png', (36, 36)),
        'task_label_border':       ('taskLabelBorder.png', (36, 36)),
        'task_label_border_hover_blank':       ('taskLabelBorderHoverBlank.png', (36, 36)),
        'task_label_border_blank':       ('taskLabelBorderBlank.png', (36, 36)),
        'drop_down_corner': ('dropDownCorner.png', (6, 6)),
        'drop_down_corner_sharp': ('dropDownCornerSharp.png', (4, 4)),
        'drop_down_top_edge': ('dropDownTopEdge.png', (8, 2)),
        'drop_down_border': ('dropDownBorder.png', (8, 5)),
        'drop_down_top_corners': ('dropDownTopCorners.png', (7, 2)),
        'label_border': ('labelBorder.png', (150, 34)),
        'label_new_border': ('labelNewBorder.png', (150, 34)),
        'label_favorite_border': ('labelFavoriteBorder.png', (109, 30)),
        'label_favorite_border_top': ('labelFavoriteBorderTop.png', (246, 12)),
        'label_favorite_border_side': ('labelFavoriteBorderSide.png', (6, 42)),
        'trashcan': ('trashcan.png', (16, 22)),

    },
    'scrollBar': {
        'scroll_bar_body':   ('scrollBarBody.png',(20,350)),
        'scroll_bar_slider': ('scrollBarSlider.png',(10,50)),
    },
    'calendarImages': {
        'magnifying_glass': ('magnifyingGlass.png',(20,20)),
    },
    'themeBackgroundsImages': {
        'background': ('background.png', (960, 520)),
    },
    'intro': {
        'spoonsLogo': ('spoonsLogo.png', (800, 128))
    },
    'inventoryIcons': {
        'icons': ('icons.png', (24, 24)),
        'folders': ('folders.png', (24, 24)),
        'themes': ('themes.png', (24, 24)),
        'borders': ('borders.png', (24, 24)),
        'extras': ('extras.png', (24, 24)),
    },
    'toggleButtons': {
        'recurringButton': ('recurringToggleButton.png', (40,40)),
        'timeButton': ('timeToggleButton.png', (40,40)),
    },
}

# 2) First load *all* images into a nested dict:
loaded_images = {}
for category, files in image_categories.items():
    cat_path = os.path.join(images_dir, category)
    if not os.path.isdir(cat_path):
        print(f"Warning: missing folder {cat_path}")
        continue

    # detect subfolders
    subs = [d for d in os.listdir(cat_path) if os.path.isdir(os.path.join(cat_path, d))]
    if subs:
        # multi-theme
        loaded_images[category] = {}
        for theme in subs:
            theme_path = os.path.join(cat_path, theme)
            loaded_images[category][theme] = {}
            for var, (fname, size) in files.items():
                fp = os.path.join(theme_path, fname)
                try:
                    img = pygame.image.load(fp)
                    img = pygame.transform.scale(img, size)
                except pygame.error as e:
                    print(f"Error loading {fp}: {e}")
                    img = None
                loaded_images[category][theme][var] = img
    else:
        # single-theme
        loaded_images[category] = {}
        for var, (fname, size) in files.items():
            fp = os.path.join(cat_path, fname)
            try:
                img = pygame.image.load(fp)
                img = pygame.transform.scale(img, size)
            except pygame.error as e:
                print(f"Error loading {fp}: {e}")
                img = None
            loaded_images[category][var] = img

# 3) **Choose your themes** up front—variable names match the top-level folders:
avatarBackgrounds = "default"
avatarBackgrounds_name = "default"
border   = "default"   # selects images/border/metal/...
border_name = "default"
hubIcons = "default"
hubIcons_name = "default"
spoonIcons = ""
spoonIcons_name = ""
restIcons = ""
restIcons_name = ""
hotbar = ""
hotbar_name = ""
manillaFolder = "dark"
manillaFolder_name = "dark"
taskBorder = ""
taskBorder_name = ""
scrollBar = ""
scrollBar_name = ""
calendarImages = ""
calendarImages_name = ""
themeBackgroundsImages = "light_academia"
themeBackgroundsImages_name = "light_academia"
intro = ""
intro_name = ""
inventoryIcons = "default"
inventoryIcons_name = "default"
toggleButtons = "default"
toggleButtons_name = "default"

# 4) Now overwrite each category name with the actual image dict you want to use:
for category, data in loaded_images.items():
    # multi-theme if every value in data is itself a dict
    if data and all(isinstance(v, dict) for v in data.values()):
        theme_name = globals().get(category)
        if theme_name not in data:
            raise ValueError(f"Invalid theme '{theme_name}' for category '{category}'")
        globals()[category] = data[theme_name]
    else:
        # single-theme → just hand back the flat dict
        globals()[category] = data

#border previews
defaultEdgeOne = loaded_images['border']['default']['edge1']
darkOakWoodEdgeOne = loaded_images['border']['darkOakWood']['edge1']
oakWoodEdgeOne = loaded_images['border']['oakWood']['edge1']
birchWoodEdgeOne = loaded_images['border']['birchWood']['edge1']
metalEdgeOne   = loaded_images['border']['metal']['edge1']
grayWoodEdgeOne = loaded_images['border']['grayWood']['edge1']
spruceWoodEdgeOne = loaded_images['border']['spruceWood']['edge1']

#manilla folder previews
defaultManillaFolder = loaded_images['manillaFolder']['default']['manilla_folder_full']
darkManillaFolder = loaded_images['manillaFolder']['dark']['manilla_folder_full']
lightManillaFolder = loaded_images['manillaFolder']['light']['manilla_folder_full']
pinkManillaFolder = loaded_images['manillaFolder']['pink']['manilla_folder_full']
greenManillaFolder = loaded_images['manillaFolder']['green']['manilla_folder_full']
blueManillaFolder = loaded_images['manillaFolder']['blue']['manilla_folder_full']

# avatar background
avatar_background = avatarBackgrounds['background_image']
dark_avatar_background = avatarBackgrounds['dark_background_image']
avatar_window = avatarBackgrounds['window_one_image']
avatar_window_flower = avatarBackgrounds['window_flower_one_image']
avatar_light = avatarBackgrounds['light_image']
avatar_bookshelf = avatarBackgrounds['bookshelf_image']
avatar_lamp = avatarBackgrounds['lamp_image']
round_table_one = avatarBackgrounds['round_table_one_image']
vlavatar = avatarBackgrounds['vlad_avatar_image']

# — border pieces —
corner          = border['corner']
edge1           = border['edge1']
edge2           = border['edge2']
tcorner         = border['tcorner']
calendar_border = border['calendar_border']

# — hub icons —
add_spoons_icon   = hubIcons['add_spoons_icon']
add_task_icon     = hubIcons['add_task_icon']
manage_task_icon  = hubIcons['manage_task_icon']
inventory_icon    = hubIcons['inventory_icon']
calendar_icon     = hubIcons['calendar_icon']
shop_icon         = hubIcons['shop_icon']
settings_icon     = hubIcons['settings_icon']

# — spoon icons —
spoon_image           = spoonIcons['spoon_image']
battery_image         = spoonIcons['battery_image']
star_image            = spoonIcons['star_image']
potion_image          = spoonIcons['potion_image']
yourdidit_image       = spoonIcons['yourdidit_image']
mike_image            = spoonIcons['mike_image']
lightningface_image   = spoonIcons['lightningface_image']
diamond_image         = spoonIcons['diamond_image']
starfruit_image       = spoonIcons['starfruit_image']
strawberry_image      = spoonIcons['strawberry_image']
terstar_image            = spoonIcons['terstar_image']
hcheart_image            = spoonIcons['hcheart_image']
beer_image            = spoonIcons['beer_image']
drpepper_image            = spoonIcons['drpepper_image']

# — rest icons —
short_rest = restIcons['short_rest_icon']
half_rest  = restIcons['half_rest_icon']
full_rest  = restIcons['full_rest_icon']

# — hotbar icons —
coin_image = hotbar['coin_image']
xp_bar_image     = hotbar['xp_bar']

# — manilla folder icons —
manilla_folder = manillaFolder['manilla_folder']
manilla_folder_open = manillaFolder['manilla_folder_open']
manilla_folder_tab  = manillaFolder['manilla_folder_tab']
manilla_folder_full = manillaFolder['manilla_folder_full']

# — task border pieces —
task_spoons_border       =  taskBorder['task_spoons_border']
progress_bar_spoon_siding = taskBorder['progress_bar_spoon_siding']
progress_bar_spoon_top    = taskBorder['progress_bar_spoon_top']
remove_edit_icons         = taskBorder['remove_edit_icons']
task_label_border =         taskBorder['task_label_border']
task_label_border_hover =   taskBorder['task_label_border_hover']
task_label_border_blank =         taskBorder['task_label_border_blank']
task_label_border_hover_blank =   taskBorder['task_label_border_hover_blank']

# drop down pieces
drop_down_corner = taskBorder['drop_down_corner']
drop_down_corner_sharp = taskBorder['drop_down_corner_sharp']
drop_down_top_edge = taskBorder['drop_down_top_edge']
drop_down_border = taskBorder['drop_down_border']
drop_down_top_corners = taskBorder['drop_down_top_corners']

#label pieces
label_border = taskBorder['label_border']
label_new_border = taskBorder['label_new_border']
label_favorite_border = taskBorder['label_favorite_border']
label_favorite_border_top = taskBorder['label_favorite_border_top']
label_favorite_border_side = taskBorder['label_favorite_border_side']
trashcan_image = taskBorder['trashcan']

# — scroll bar pieces —
scroll_bar   = scrollBar['scroll_bar_body']
scroll_bar_slider = scrollBar['scroll_bar_slider']

# — calendar misc icon —
magnifying_glass = calendarImages['magnifying_glass']

#custom backgrounds
light_academia_background = themeBackgroundsImages['background']

#intro
spoons_logo = intro['spoonsLogo']

#inventory
inventory_icons_icons = inventoryIcons['icons']
inventory_icons_folders = inventoryIcons['folders']
inventory_icons_themes = inventoryIcons['themes']
inventory_icons_borders = inventoryIcons['borders']
inventory_icons_extras = inventoryIcons['extras']

#toggle buttons
recurring_button = toggleButtons['recurringButton']
time_button = toggleButtons['timeButton']


def set_image(category: str, theme_name: str):
    """
    Swaps the global dict for a multi-theme category, and remembers its name.
    Example: set_image('border', 'metal')
      • globals()['border']      → loaded_images['border']['metal']
      • globals()['border_name'] → 'metal'
    """
    theme_name_new = theme_name
    if category not in loaded_images:
        raise KeyError(f"No such category {category!r}")
    data = loaded_images[category]

    # only multi‐theme categories need swapping
    if not (data and all(isinstance(v, dict) for v in data.values())):
        return

    if theme_name not in data:
        raise ValueError(f"Invalid theme {theme_name!r} for category {category!r}")

    # overwrite the image dict
    globals()[category] = data[theme_name]
    # also store the name
    globals()[f"{category}_name"] = theme_name

    return data[theme_name], theme_name_new


oakwood_preview_rect = pygame.Rect(370, 180, oakWoodEdgeOne.get_height()*3, oakWoodEdgeOne.get_width()*3)
darkoakwood_preview_rect = pygame.Rect(370, 220, darkOakWoodEdgeOne.get_height()*3, oakWoodEdgeOne.get_width()*3)
metal_preview_rect   = pygame.Rect(370, 260, metalEdgeOne.get_height()*3,   metalEdgeOne.get_width()*3)
default_preview_rect   = pygame.Rect(370, 300, metalEdgeOne.get_height()*3,   metalEdgeOne.get_width()*3)
birchwood_preview_rect   = pygame.Rect(370, 340, metalEdgeOne.get_height()*3,   metalEdgeOne.get_width()*3)
sprucewood_preview_rect   = pygame.Rect(370, 380, metalEdgeOne.get_height()*3,   metalEdgeOne.get_width()*3)
graywood_preview_rect   = pygame.Rect(370, 420, metalEdgeOne.get_height()*3,   metalEdgeOne.get_width()*3)



class_schedule = {
    "Monday": [
    ],
    "Tuesday": [
    ],
    "Wednesday": [
    ],
    "Thursday": [
    ],
    "Friday": [
    ]
}

months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

label_favorites = []

# Creating input boxes/ buttons
# Spoon input
spoon_amount_input_box = pygame.Rect(375, 90, 50, 50)
spoon_done_button = pygame.Rect(300, 175, 200, 50)
short_rest_button = pygame.Rect(40, 250, 220, 50)
half_rest_button = pygame.Rect(290, 250, 220, 50)
full_rest_button = pygame.Rect(540, 250, 220, 50)

# hub buttons
hub_add_spoons    = pygame.Rect(0,   0, 250, 86)
hub_add_task      = pygame.Rect(0,  86, 250, 86)
hub_manage_task   = pygame.Rect(0, 172, 250, 86)
hub_inventory         = pygame.Rect(0, 258, 250, 86)
hub_calendar      = pygame.Rect(0, 344, 250, 85)
hub_shop         = pygame.Rect(0, 429, 250, 85)
hub_stats         = pygame.Rect(0, 514, 250, 86)

hub_toggle = pygame.Rect(0,0,5,600)
hub_menu1 = pygame.Rect(0,0,0,0) # Needs to be removed in all files
hub_menu2 = pygame.Rect(0,0,0,0) # Needs to be removed in all files
hub_menu2_open = pygame.Rect(0,0,0,0) # Needs to be removed in all files
hub_menu3 = pygame.Rect(0,0,0,0) # Needs to be removed in all files
hub_cover = pygame.Rect(0,0,250,600)
#tool tips
tool_tips_x_offset = 75
add_spoons_tool_tip_rect = pygame.Rect(250 + tool_tips_x_offset,30,300,200)
add_task_tool_tip_rect = pygame.Rect(250 + tool_tips_x_offset,100,300,200)
complete_task_tool_tip_rect = pygame.Rect(250 + tool_tips_x_offset,170,300,200)
remove_task_tool_tip_rect = pygame.Rect(250 + tool_tips_x_offset,240,300,200)
daily_schedule_tool_tip_rect = pygame.Rect(250 + tool_tips_x_offset,310,300,200)
calendar_tool_tip_rect = pygame.Rect(250 + tool_tips_x_offset,380,300,200)
settings_tool_tip_rect = pygame.Rect(250 + tool_tips_x_offset,380,300,200)
# manage task buttons
folder_rects = {}

# Complete/Edit/Remove toggle buttons
complete_tasks_toggle = pygame.Rect(650, 55,35,35)
edit_tasks_toggle = pygame.Rect(690,55,35,35)
remove_tasks_toggle = pygame.Rect(730,55,35,35)
task_toggle_cover = pygame.Rect(645,50,125,45)

#Edit task buttons
save_button = pygame.Rect(190, 400, 200, 45)
cancel_button = pygame.Rect(410, 400, 200, 45)
edit_task_spoon_input_box = pygame.Rect(100, 300, 300, 50)
edit_task_taskname_input_box = pygame.Rect(100, 205, 300, 50)
month_input_box_edit_task = pygame.Rect(480, 205, 160, 50)
month_up_button_edit_task = pygame.Rect(620, 210, 15, 15)
month_down_button_edit_task = pygame.Rect(620, 235, 15, 15)
day_input_box_edit_task = pygame.Rect(665, 205, 70, 50)
day_up_button_edit_task = pygame.Rect(715, 210, 15, 15)
day_down_button_edit_task = pygame.Rect(715, 235, 15, 15)
done_toggle_edit_task = pygame.Rect(480, 300, 250, 50)

#Scroll bar
scroll_bar_body = pygame.Rect(10,100,30,450)
scroll_bar_up_button = pygame.Rect(12,102,26,32)
scroll_bar_down_button = pygame.Rect(12,516,26,32)
#calendar page
previous_month_button = pygame.Rect(418,9,27,27)
next_month_button = pygame.Rect(600,9,27,27)

#Folder Input Boxes
folder_one = "Homework"
folder_two = "Chores"
folder_three = "Work"
folder_four = "Misc"
folder_five = ""
folder_six = ""

# daily schedule
daily_schedule_top_cover = pygame.Rect(0,0,800,40)
last_day_button = pygame.Rect(80,10,20,20)
next_day_button = pygame.Rect(720,10,20,20)


#initiating all colors
background_color = CAMEL# type: ignore
hub_background_color = CAMEL# type: ignore
done_button_color = LIME_GREEN# type: ignore
add_tasks_choose_folder_color = BLUE# type: ignore
add_tasks_chosen_folder_color = GOLD# type: ignore
complete_tasks_hub_folder_color = BLUE# type: ignore
complete_tasks_task_color = LIME_GREEN# type: ignore
remove_tasks_hub_folder_color = BLUE# type: ignore
remove_tasks_task_color = LIME_GREEN# type: ignore

add_spoons_color = GOLD# type: ignore
add_tasks_color = LIME_GREEN# type: ignore
manage_tasks_color = GREEN# type: ignore
inventory_color = RED# type: ignore
shop_color = LIGHT_BLUE# type: ignore
calendar_color = BLUE# type: ignore
stats_color = DARK_GRAY# type: ignore

calendar_current_day_color = CAMEL# type: ignore
calendar_current_day_header_color = GOLD# type: ignore
calendar_previous_day_color = LIGHT_BLUE# type: ignore
calendar_previous_day_header_color = BLUE# type: ignore
calendar_next_day_color = LIGHT_BLUE# type: ignore
calendar_next_day_header_color = BLUE# type: ignore
calendar_month_color = CAMEL# type: ignore
homework_fol_color = BLUE# type: ignore
chores_fol_color = GREEN# type: ignore
work_fol_color = RED# type: ignore
misc_fol_color = GOLD# type: ignore

current_task = ""
current_spoons = 0
task_buttons_homework = []
task_buttons_chores = []
task_buttons_work = []
task_buttons_misc = []
task_buttons_exams = []
task_buttons_projects = []
input_active = False
current_time = datetime.now()
previous_month = current_time.month
current_month = current_time.month
task_month = current_month
previous_day = current_time.strftime('%d')
current_day = current_time.strftime('%d')
displayed_month = datetime.now().month
displayed_year = datetime.now().year
task_day = current_day
hub_buttons_showing = False

dropdown_colors_open = False
dropdown_colors_hub_open = False
dropdown_colors_calendar_open = False
button_chosen = "background"
hub_button_chosen = ""
calendar_button_chosen = ""
spoon_name_input = ""

short_rest_amount = 2
half_rest_amount = 5
full_rest_amount = 10
tool_tips = False
icon_image = spoon_image
spoon_name = "Spoons"
page = "input_spoons"
folder = "homework"
running = True
time_toggle_on = False
recurring_toggle_on = False
start_time = [0, 0, 0, 0]  # Representing "00:00"
end_time = [0, 0, 0, 0]    # Representing "00:00"
scroll_offset = 0
scroll_last_update_time = 0
scroll_update_interval = 0.1
day_offset = 0

daily_spoons = {
    "Mon": 0,
    "Tue": 0,
    "Wed": 0,
    "Thu": 0,
    "Fri": 0,
    "Sat": 0,
    "Sun": 0
}

scroll_offset = 0

confetti_particles = []

task_how_often = 1
task_how_long = 1
task_repetitions_amount = 1

#inventory stuff
TIMER_MODES = {
    "Pomodoro (25/5)": (25, 5),
    "Extended (50/10)": (50, 10),
    "Deep Work (90/20)": (90, 20),
    "Custom": (0, 0)
}
inventory_timer = None
dropdown_open = False

#stats stuff
personal_stats = {
    "tasks_completed": 123,
    "spoons_earned": 320,
    "spoons_spent": 250,
    "current_streak": 7,
    "longest_streak": 14,
    "folder_breakdown": {
        "homework": 40,
        "chores": 30,
        "work": 25,
        "misc": 28
    }
}

global_leaderboard = [
    {"username": "Alice", "tasks": 150, "spoons": 400, "badges": 10},
    {"username": "Bob", "tasks": 120, "spoons": 320, "badges": 7},
    {"username": "You", "tasks": 123, "spoons": 320, "badges": 5},
]

#streaks stuff
streak_dates = []
streak_task_completed = False
coins = 0
level = 0

calendar_mode = "Month"            # or "week"
displayed_week_offset = 0

inventory_tab = "Icons"

day_range_index = 0


# will hold (outline_rect, icon_surface) for the “Icons” tab
inventory_icon_buttons = []
inventory_folder_buttons = []
inventory_border_buttons = []
inventory_themes_buttons = []
folders_dropdown_open = False

#fullscreen modes
is_maximized = False
WINDOWED_SIZE   = (960,  540)
last_windowed = WINDOWED_SIZE
FULLSCREEN_SIZE = (1536, 817)



# — sound setup — 
pygame.mixer.init()  # initialize the sound system

# load sounds from your Spoons/sounds folder
SOUNDS_DIR = os.path.join(os.path.dirname(__file__), "sounds", "hubButtons")

def load_sfx(name, ext="mp3"):
    path = os.path.join(SOUNDS_DIR, f"{name}.{ext}")
    try:
        return pygame.mixer.Sound(path)
    except pygame.error as e:
        print(f"Failed loading sound {path}: {e}")
        return None

# now load all your effects:
settings_button_click_sfx = load_sfx("settingsClick")

