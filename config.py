import pygame
import os
from datetime import datetime
from colors import COLORS
for name, value in COLORS.items():
    globals()[name] = value
    
# Initialize pygame font
pygame.font.init()

screen_height = 520
screen_width = 960

total_content_height = 0
frame_buttons = []

font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen_height * 0.06))
big_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen_height * 0.067))
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

# Images
base_dir = os.path.dirname(os.path.abspath(__file__))
images_dir = os.path.join(base_dir, "images")

image_files = {
    "spoons_logo": ["Spoons Logo 128p.png", (500, 80)],
    "spoon_image": ["spoon.png", (33, 33)],
    "battery_image": ["green battery.png", (33, 33)],
    "star_image": ["star.png", (33, 33)],
    "potion_image": ["potion.png", (33, 33)],
    "spoon_bracket_image": ["spoon_bracket.png", (33, 33)],
    "color_wheel": ["color_wheel.png", (200, 200)],
    "light_academia_background": ["light_academia_background.png", (800, 600)],
    "edit_toggle_icon": ["pencil.png", (20, 20)],
    "complete_toggle_icon": ["checkmark.png", (25, 25)],
    "remove_toggle_icon": ["cross.png", (20, 20)],
    "add_spoons_icon": ["addSpoonsIcon.png", (1024, 1024)],
    "add_task_icon": ["addTasksIcon.png", (1024, 1024)],
    "manage_task_icon": ["manageTasksIcon.png", (150, 83)],
    "study_icon": ["studyIcon.png", (1024, 1024)],
    "calendar_icon": ["calendarIcon.png", (1024, 1024)],
    "store_icon": ["storeIcon.png", (1024, 1024)],
    "settings_icon": ["settingsIcon.png", (1024, 1024)],
    "corner": ["borderCorner.png", (12, 12)],
    "edge1": ["Border1.png", (6, 12)],
    "edge2": ["Border2.png", (6, 12)],
    "connector": ["borderConnector.png", (15, 15)],
    "tcorner": ["borderTcorner.png", (14, 12)],
    "calendar_border": ["borderCalendarLeft.png", (9, 24)],
    "short_rest_icon": ["shortRestIcon.png", (790,790)],
    "half_rest_icon": ["halfRestIcon.png", (864,864)],
    "full_rest_icon": ["fullRestIcon.png", (820,820)],
    "coin_image": ["coin.png", (15, 17)],
    "xp_bar": ["xpBar.png", (155, 30)],
    "manilla_folder": ["manillaFolder.png", (150, 62)],
    "manilla_folder_open": ["manillaFolderOpen.png", (150, 62)],
    "manilla_folder_tab": ["manillaFolderTab.png", (48, 7)],
    "manilla_folder_full": ["manillaFolderFull.png", (150, 83)],
    "task_spoons_border": ["taskSpoonsBorder.png", (750, 50)],
    "progress_bar_spoon_siding": ["progressBarSpoonSiding.png", (6, 34)],
    "progress_bar_spoon_top": ["progressBarSpoonTop.png", (10, 2)],
    "scroll_bar_body": ["scrollBarBody.png", (20, 350)],
    "scroll_bar_slider": ["scrollBarSlider.png", (10, 50)],
    "remove_edit_icons": ["removeEditIcons.png", (20, 40)],
    "magnifying_glass": ["magnifyingGlass.png", (20, 20)],
}

# Load and transform images
loaded_images = {}
for var_name, file_data in image_files.items():
    try:
        file_name, size = file_data
        image_path = os.path.join(images_dir, file_name)
        image = pygame.image.load(image_path)
        image = pygame.transform.scale(image, size)
        loaded_images[var_name] = image
    except pygame.error as e:
        print(f"Error loading {file_name}: {e}")
        loaded_images[var_name] = None

# Expose individual images for import
spoons_logo = loaded_images.get("spoons_logo")
spoon_image = loaded_images.get("spoon_image")
battery_image = loaded_images.get("battery_image")
star_image = loaded_images.get("star_image")
potion_image = loaded_images.get("potion_image")
spoon_bracket_image = loaded_images.get("spoon_bracket_image")
color_wheel = loaded_images.get("color_wheel")
edit_toggle_icon = loaded_images.get("edit_toggle_icon")
complete_toggle_icon = loaded_images.get("complete_toggle_icon")
remove_toggle_icon = loaded_images.get("remove_toggle_icon")
add_spoons_icon = loaded_images.get("add_spoons_icon") # hub icons
add_task_icon = loaded_images.get("add_task_icon")
manage_task_icon = loaded_images.get("manage_task_icon")
study_icon = loaded_images.get("study_icon")
calendar_icon = loaded_images.get("calendar_icon")
store_icon = loaded_images.get("store_icon")
settings_icon = loaded_images.get("settings_icon")
corner = loaded_images.get("corner")
edge_one = loaded_images.get("edge1")
edge_two = loaded_images.get("edge2")
connector = loaded_images.get("connector")
tcorner = loaded_images.get("tcorner")
calendar_border = loaded_images.get("calendar_border")
short_rest = loaded_images.get("short_rest_icon")
half_rest = loaded_images.get("half_rest_icon")
full_rest = loaded_images.get("full_rest_icon")
coin_image = loaded_images.get("coin_image")
xp_bar_image = loaded_images.get("xp_bar")
manilla_folder = loaded_images.get("manilla_folder")
manilla_folder_open = loaded_images.get("manilla_folder_open")
manilla_folder_tab = loaded_images.get("manilla_folder_tab")
manilla_folder_full = loaded_images.get("manilla_folder_full")
task_spoons_border = loaded_images.get("task_spoons_border")
progress_bar_spoon_siding = loaded_images.get("progress_bar_spoon_siding")
progress_bar_spoon_top = loaded_images.get("progress_bar_spoon_top")
scroll_bar = loaded_images.get("scroll_bar_body")
scroll_bar_slider = loaded_images.get("scroll_bar_slider")
remove_edit_icons = loaded_images.get("remove_edit_icons")
magnifying_glass = loaded_images.get("magnifying_glass")

#background images
light_academia_background = loaded_images.get("light_academia_background")

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
hub_study         = pygame.Rect(0, 258, 250, 86)
hub_calendar      = pygame.Rect(0, 344, 250, 85)
hub_store         = pygame.Rect(0, 429, 250, 85)
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

#settings page
tool_tip_toggle = pygame.Rect(150, 550, 23, 23)
spoon_name_input_box = pygame.Rect(260, 15, 100, 40)
#themes
aquatic_theme = pygame.Rect(500, 110, 40, 40)
foresty_theme = pygame.Rect(500, 160, 40, 40)
girly_pop_theme = pygame.Rect(500, 210, 40, 40)
vampire_goth_theme = pygame.Rect(500, 260, 40, 40)
sunset_glow_theme = pygame.Rect(500, 310, 40, 40)
#extra themes
light_academia_theme = pygame.Rect(430, 110, 40, 40)
retro_theme = pygame.Rect(430, 160, 40, 40)
minimalist_theme = pygame.Rect(430, 210, 40, 40)
cosmic_theme = pygame.Rect(430, 260, 40, 40)
autumn_harvest_theme = pygame.Rect(430, 310, 40, 40)
tropical_oasis_theme = pygame.Rect(430, 360, 40, 40)
pastel_dreams_theme = pygame.Rect(430, 410, 40, 40)
steampunk_theme = pygame.Rect(430, 460, 40, 40)
#image outlines
spoon_image_outline = pygame.Rect(410,20,35,35)
battery_image_outline = pygame.Rect(460,20,35,35)
star_image_outline = pygame.Rect(510,20,35,35)
potion_image_outline = pygame.Rect(560,20,35,35)
#Folder Input Boxes
folder_one_name_input_box = pygame.Rect(260, 110, 140, 40)
folder_two_name_input_box = pygame.Rect(260, 160, 140, 40)
folder_three_name_input_box = pygame.Rect(260, 210, 140, 40)
folder_four_name_input_box = pygame.Rect(260, 260, 140, 40)
folder_five_name_input_box = pygame.Rect(260, 310, 140, 40)
folder_six_name_input_box = pygame.Rect(260, 360, 140, 40)
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
study_color = RED# type: ignore
store_color = LIGHT_BLUE# type: ignore
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

#study stuff
TIMER_MODES = {
    "Pomodoro (25/5)": (25, 5),
    "Extended (50/10)": (50, 10),
    "Deep Work (90/20)": (90, 20),
    "Custom": (0, 0)
}
study_timer = None
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
coins = 7
level = 2.66

calendar_mode = "month"            # or "week"
hovered_week_idx = None   # 0–5 for which row the mouse is over
selected_week_idx = None  # when the magnifier is clicked
