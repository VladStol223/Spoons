#Vladislav Stolbennikov
#8/7/2024
#Spoons App
#VS1.25

'''
Total pages:
1.) Add Spoons
2.) Add Tasks
3.) Manage Task Hub
4.) Complete Folder 1 Tasks
5.) Complete Folder 2 Tasks
6.) Complete Folder 3 Tasks
7.) Complete Folder 4 Tasks
8.) Edit Folder 1 Tasks
9.) Edit Folder 2 Tasks
10.) Edit Folder 3 Tasks
11.) Edit Folder 4 Tasks
12.) Remove Folder 1 Tasks
13.) Remove Folder 2 Tasks
14.) Remove Folder 3 Tasks
15.) Remove Folder 4 Tasks
16.) inventory
17.) Calendar
18.) shop
19.) Statistics

To do:
- Add the following sound effects:
    * Add spoons page:
        - hub button: spoon hitting floor
        - Add spoon sound effect
        - remove spoon sound effect

    - Task completed sound effect 
'''

import ctypes
import platform
from os import name
from datetime import datetime

from config import *
from colors import COLORS
for name, value in COLORS.items():
    globals()[name] = value

import pygame
import sys
import calendar

import subprocess
from copyparty_sync import (
    set_user_folder,
    download_data_json_if_present,
    verify_credentials_and_access,
    get_current_user,
)
import os

IS_WINDOWS = platform.system() == "Windows"
IS_LINUX   = platform.system() == "Linux"
IS_MAC     = platform.system() == "Darwin"

if IS_WINDOWS:
    ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))


pygame.init()
pygame.key.set_repeat(450, 50) 

button_widths = {}
hub_closing = False
UI_elements_initialized = False
clock = pygame.time.Clock()
icon_surface = pygame.image.load("icon.png")
pygame.display.set_icon(icon_surface)
pygame.display.set_caption("Spoons")
screen = pygame.display.set_mode(WINDOWED_SIZE)

SWP_NOSIZE   = 0x0001
SWP_NOZORDER = 0x0004
HWND_TOP     = 0

def move_window(x: int, y: int):
    """Move the Pygame window (Windows only)."""
    if IS_WINDOWS:
        hwnd = pygame.display.get_wm_info()["window"]
        ctypes.windll.user32.SetWindowPos(hwnd, HWND_TOP, x, y, 0, 0, SWP_NOSIZE | SWP_NOZORDER)

def get_true_screen_size():
    if IS_WINDOWS:
        user32 = ctypes.windll.user32
        return (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))
    else:
        # Cross-platform fallback: use Pygame's display info
        info = pygame.display.Info()
        return (info.current_w, info.current_h)

# Constant for “pixels per logical inch” on X-axis
LOGPIXELSX = 88

def get_scale_factor() -> float:
    if IS_WINDOWS:
        hwnd = pygame.display.get_wm_info()["window"]
        dpi = ctypes.windll.user32.GetDpiForWindow(hwnd)
        return dpi / 96.0
    else:
        return 0.5  # Default scaling on Linux/macOS

scale_factor = get_scale_factor()

####################################################################################################################################
def compute_spoons_needed_today(*task_lists):
    """Sum remaining spoons for tasks due today or overdue (across all folders)."""
    today = datetime.now().date()
    total_needed = 0
    for lst in task_lists:
        for t in lst:
            try:
                if isinstance(t, dict):
                    due = t.get("due_date")
                    if isinstance(due, str):
                        due_dt = datetime.fromisoformat(due.replace("Z", ""))
                    else:
                        due_dt = due
                    if hasattr(due_dt, "date"):
                        due_day = due_dt.date()
                        if due_day <= today:
                            need = int(t.get("spoons_needed", 0)) - int(t.get("done", 0))
                            if need > 0:
                                total_needed += need
                else:
                    # tuple/list: [name, spoons_needed, done, days_left, due_dt, ...]
                    due_dt = t[4]
                    due_day = due_dt.date() if hasattr(due_dt, "date") else due_dt
                    if due_day and due_day <= today:
                        need = int(t[1]) - int(t[2])
                        if need > 0:
                            total_needed += need
            except Exception:
                pass
    return total_needed

def _decrement_days(lst, n_days):
    if not lst or n_days <= 0:
        return
    for task in lst:
        try:
            if task[3] > 0:
                task[3] = max(0, task[3] - n_days)
        except Exception:
            pass

def slot_key_for_page(p: str) -> str:
    return {
        "complete_homework_tasks": "folder_one",
        "complete_chores_tasks":   "folder_two",
        "complete_work_tasks":     "folder_three",
        "complete_misc_tasks":     "folder_four",
        "complete_exams_tasks":    "folder_five",
        "complete_projects_tasks": "folder_six",
    }.get(p, "folder_one")

def hub_buttons(event):
    global scroll_offset

    if event.type != pygame.MOUSEBUTTONDOWN:
        return None

    button_actions = {
        "input_spoons": hub_add_spoons,
        "input_tasks":  hub_add_task,
        "manage_tasks": hub_manage_task,
        "inventory":    hub_inventory,
        "calendar":     hub_calendar,
        "shop":         hub_shop,
        "stats":        hub_stats,
    }

    for page, rect in button_actions.items():
        if rect.collidepoint(event.pos):
            save_data(
            spoons, homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list,
            exams_tasks_list, projects_tasks_list, daily_spoons, theme, icon_image,
            spoon_name_input, folder_one, folder_two, folder_three, folder_four,
            folder_five, folder_six, streak_dates,
            border_name, hubIcons_name, spoonIcons_name, restIcons_name, hotbar_name, manillaFolder_name, taskBorder_name, 
            scrollBar_name, calendarImages_name, themeBackgroundsImages_name, intro_name, label_favorites, spoons_used_today)

            if page == "manage_tasks":
                scroll_offset = 0
            return page

    return None

def spawn_background_upload():
    """Fire-and-forget upload in a detached Python process (logs to file)."""
    try:
        py = sys.executable
        code = (
            "import copyparty_sync as cps, traceback, os\n"
            "with open('copyparty_upload.log','a',encoding='utf-8') as f:\n"
            "    print('[child] start', file=f)\n"
            "    try:\n"
            "        cps.upload_data_json()\n"
            "        print('[child] success', file=f)\n"
            "    except Exception:\n"
            "        traceback.print_exc(file=f)\n"
        )
        kwargs = {"close_fds": True, "cwd": os.getcwd()}
        if IS_WINDOWS:
            DETACHED_PROCESS = 0x00000008
            CREATE_NEW_PROCESS_GROUP = 0x00000200
            kwargs["creationflags"] = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
        else:
            kwargs["start_new_session"] = True
        subprocess.Popen([py, "-u", "-c", code], **kwargs)
        print("[copyparty] background uploader spawned")
    except Exception as e:
        print(f"[copyparty] failed to spawn background uploader: {e}")


#drawing / logic functions
from drawing_functions.draw_hub_buttons import draw_hub_buttons
from drawing_functions.draw_logic_input_spoons import draw_input_spoons, logic_input_spoons
from drawing_functions.draw_logic_input_tasks import draw_input_tasks, logic_input_tasks
from drawing_functions.draw_logic_manage_tasks_hub import draw_manage_tasks_hub, logic_manage_tasks_hub
from drawing_functions.draw_logic_manage_tasks import draw_complete_tasks, logic_complete_tasks, set_favorites_binding
from drawing_functions.draw_logic_calendar import draw_calendar, logic_calendar
from drawing_functions.draw_logic_shop import draw_shop, logic_shop, logic_change_image
from drawing_functions.logic_task_toggle import logic_task_toggle
from drawing_functions.draw_logic_inventory import draw_inventory, logic_inventory
from drawing_functions.draw_logic_stats import draw_stats, logic_stats
from drawing_functions.draw_border import draw_border
from drawing_functions.draw_hotbar import draw_hotbar
from drawing_functions.draw_logic_login import draw_login, logic_login

# Miscellanous Functions
from load_save import save_data, load_data
from switch_themes import switch_theme
from handle_scroll import handle_task_scroll

# remember last signed-in user (written by login screen)
active_user_folder = None
try:
    with open(os.path.join("spoons","active_user.txt"), "r", encoding="utf-8") as f:
        active_user_folder = (f.read().strip() or None)
except Exception:
    pass

if active_user_folder:
    set_user_folder(active_user_folder)

#loading save data
(spoons, homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list,  
exams_tasks_list, projects_tasks_list, daily_spoons, loaded_theme, icon_image,
spoon_name_input, folder_one, folder_two, folder_three, folder_four,
folder_five, folder_six, streak_dates,
border, hubIcons, spoonIcons, restIcons, hotbar, manillaFolder,
taskBorder, scrollBar, calendarImages, themeBackgroundsImages, intro,
border_name, hubIcons_name, spoonIcons_name, restIcons_name,
hotbar_name, manillaFolder_name, taskBorder_name, scrollBar_name,
calendarImages_name, themeBackgroundsImages_name, intro_name, label_favorites,
last_save_date ,spoons_used_today) = load_data()
current_theme = switch_theme(loaded_theme, globals())

# --- Startup daily spoons grant + per-day counter reset ---
try:
    # last_save_date is either "YYYY-MM-DD" or ["YYYY-MM-DD", spoons_used_today]
    if isinstance(last_save_date, list) and len(last_save_date) == 2:
        last_date_str = last_save_date[0]
        try:
            spoons_used_today = int(last_save_date[1])
        except Exception:
            spoons_used_today = 0
    else:
        last_date_str = last_save_date
    last_date = datetime.strptime(last_date_str, "%Y-%m-%d").date() if last_date_str else None
except Exception:
    last_date = None

today = datetime.now().date()
if (last_date is None) or (today > last_date):
    delta_days = (today - last_date).days if last_date else 1

    # grant today’s daily spoons
    current_weekday = today.strftime("%a")
    spoons = daily_spoons.get(current_weekday, spoons)

    # reset daily counter
    spoons_used_today = 0

    # decrement days_till_due_date by the gap
    streak_task_completed = False
    _decrement_days(homework_tasks_list,  delta_days)
    _decrement_days(chores_tasks_list,    delta_days)
    _decrement_days(work_tasks_list,      delta_days)
    _decrement_days(misc_tasks_list,      delta_days)
    _decrement_days(exams_tasks_list,     delta_days)
    _decrement_days(projects_tasks_list,  delta_days)

    # persist immediately with the pair
    save_data(
            spoons, homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list,
            exams_tasks_list, projects_tasks_list, daily_spoons, theme, icon_image,
            spoon_name_input, folder_one, folder_two, folder_three, folder_four,
            folder_five, folder_six, streak_dates,
            border_name, hubIcons_name, spoonIcons_name, restIcons_name, hotbar_name, manillaFolder_name, taskBorder_name, 
            scrollBar_name, calendarImages_name, themeBackgroundsImages_name, intro_name, label_favorites, spoons_used_today)
else:
    streak_task_completed = False

current_date_str = datetime.now().strftime("%Y-%m-%d")

# If creds are present and the user folder is reachable, skip login
if verify_credentials_and_access():
    u = get_current_user()
    set_user_folder(u)                 # make sure sync uses the same user
    download_data_json_if_present()    # pull /<u>/data.json if it exists
    page = "input_spoons"

# ----------------------------------------------------------------------------------------------------
# Main loop
# ----------------------------------------------------------------------------------------------------
while running:
    screen_width, screen_height = screen.get_size()
    font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen_height * 0.06))
    big_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen_height * 0.067))
    bigger_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen_height * 0.075))
    small_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen_height * 0.047))
    smaller_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen_height * 0.033))
    delta_time = clock.tick(60) / 1000.0
    max_days = calendar.monthrange(datetime.now().year, task_month)[1]
    mouse_pos = pygame.mouse.get_pos()

    # ---- live midnight rollover ----
    new_date_str = datetime.now().strftime("%Y-%m-%d")
    if new_date_str != current_date_str:
        current_date_str = new_date_str

        # grant today’s daily spoons
        today = datetime.now().date()
        current_weekday = today.strftime("%a")
        spoons = daily_spoons.get(current_weekday, spoons)

        # reset per-day counter
        spoons_used_today = 0

        # decrement days by 1
        _decrement_days(homework_tasks_list,  1)
        _decrement_days(chores_tasks_list,    1)
        _decrement_days(work_tasks_list,      1)
        _decrement_days(misc_tasks_list,      1)
        _decrement_days(exams_tasks_list,     1)
        _decrement_days(projects_tasks_list,  1)

        save_data(
            spoons, homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list,
            exams_tasks_list, projects_tasks_list, daily_spoons, theme, icon_image,
            spoon_name_input, folder_one, folder_two, folder_three, folder_four,
            folder_five, folder_six, streak_dates,
            border_name, hubIcons_name, spoonIcons_name, restIcons_name, hotbar_name, manillaFolder_name, taskBorder_name, 
            scrollBar_name, calendarImages_name, themeBackgroundsImages_name, intro_name, label_favorites, spoons_used_today)

    spoons_needed_today = compute_spoons_needed_today(homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list, exams_tasks_list, projects_tasks_list)

    if background_color == (-1,-1,-1):
            screen.blit(light_academia_background, (0,0))
    else:
        screen.fill(background_color)
        hub_background_color = background_color

    hub_icon_rects = draw_hub_buttons(screen, page, tool_tips, background_color,
                                  add_spoons_color, add_tasks_color,
                                  manage_tasks_color, inventory_color, calendar_color,
                                  shop_color, stats_color, button_widths, hub_closing, delta_time, is_maximized, scale_factor)
    
    if page == "login":
        login_mode, login_username, login_password, login_input_active = draw_login(screen, login_mode, login_username, login_password, login_input_active, background_color)

    elif page == "input_spoons":
        if not UI_elements_initialized:
            draw_input_spoons(screen, daily_spoons, spoons, delta_time, icon_image, input_active, background_color, x_offset=40)
            UI_elements_initialized = True
        else:
            draw_input_spoons(screen, daily_spoons, spoons, delta_time, icon_image, input_active, background_color, x_offset=40)
        
    elif page == "input_tasks":
        draw_input_tasks(screen, spoons, current_task, current_spoons, input_active, 
                         folder, task_month, task_day, time_toggle_on, recurring_toggle_on,  start_time, end_time,
                         done_button_color, background_color, add_tasks_choose_folder_color, add_tasks_chosen_folder_color, icon_image, spoon_name_input,
                         task_how_often, task_how_long, task_repetitions_amount,
                         folder_one, folder_two, folder_three, folder_four, folder_five, folder_six
                         , homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list, exams_tasks_list, projects_tasks_list, manillaFolder)
        
    elif page == "manage_tasks":
        folder_rects = draw_manage_tasks_hub(screen, spoons,
                            homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list,exams_tasks_list, projects_tasks_list,
                            complete_tasks_hub_folder_color, icon_image, spoon_name_input,
                            folder_one, folder_two, folder_three, folder_four, folder_five, folder_six, manillaFolder)
        
    elif page == "complete_homework_tasks":
        set_favorites_binding(label_favorites.get(slot_key_for_page(page), []))
        scroll_offset, total_content_height = draw_complete_tasks(screen, "Homework", homework_tasks_list, task_buttons_homework, spoons,  scroll_offset,
                            background_color, icon_image, spoon_name,
                            folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
        
    elif page == "complete_chores_tasks":
        set_favorites_binding(label_favorites.get(slot_key_for_page(page), []))
        scroll_offset, total_content_height = draw_complete_tasks(screen, "Chores", chores_tasks_list, task_buttons_chores, spoons,  scroll_offset,
                            background_color, icon_image, spoon_name,
                            folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
        
    elif page == "complete_work_tasks":
        set_favorites_binding(label_favorites.get(slot_key_for_page(page), []))
        scroll_offset, total_content_height = draw_complete_tasks(screen, "Work", work_tasks_list, task_buttons_work, spoons,  scroll_offset,
                            background_color, icon_image, spoon_name,
                            folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
        
    elif page == "complete_misc_tasks":
        set_favorites_binding(label_favorites.get(slot_key_for_page(page), []))
        scroll_offset, total_content_height = draw_complete_tasks(screen, "Misc", misc_tasks_list, task_buttons_misc, spoons,  scroll_offset,
                            background_color, icon_image, spoon_name,
                            folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)

    elif page == "complete_exams_tasks":
        set_favorites_binding(label_favorites.get(slot_key_for_page(page), []))
        scroll_offset, total_content_height = draw_complete_tasks(screen, "Exams", exams_tasks_list, task_buttons_exams, spoons,  scroll_offset,
                            background_color, icon_image, spoon_name,
                            folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)

    elif page == "complete_projects_tasks":
        set_favorites_binding(label_favorites.get(slot_key_for_page(page), []))
        scroll_offset, total_content_height = draw_complete_tasks(screen, "Projects", projects_tasks_list, task_buttons_projects, spoons,  scroll_offset,
                            background_color, icon_image, spoon_name,
                            folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
        
    elif page == "inventory":
        draw_inventory(screen, spoon_name_input, inventory_tab, background_color, input_active, folder_one, folder_two, folder_three, folder_four, folder_five, folder_six, folders_dropdown_open)
        
    elif page == "calendar":
        draw_border(screen, (0, 0, screen_width, screen_height), page, background_color, border, is_maximized, scale_factor)
        draw_calendar(screen, spoon_name_input, displayed_week_offset, day_range_index, 
                  homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list, exams_tasks_list, projects_tasks_list,
                  displayed_month, displayed_year, background_color,
                  homework_fol_color, chores_fol_color, work_fol_color, misc_fol_color,calendar_month_color, 
                  calendar_previous_day_header_color, calendar_next_day_header_color, calendar_current_day_header_color,
                  calendar_previous_day_color, calendar_current_day_color, calendar_next_day_color,
                  folder_one, folder_two, folder_three, folder_four, folder_five, folder_six,
                  streak_dates)
        
    elif page == "shop":
        draw_shop(screen, tool_tips, spoon_name_input, icon_image, input_active, hub_background_color,
                  folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
        
    elif page == "stats":
        draw_stats(screen, font, big_font, personal_stats, global_leaderboard)
        draw_border(screen, (0, 0, screen_width, screen_height), page, background_color, border, is_maximized, scale_factor)

    if page not in ("calendar", "stats"):
        draw_hotbar(screen, spoons, icon_image, spoon_name_input, streak_dates, coins, level, page, spoons_needed_today, spoons_used_today)
        draw_border(screen, (0, 0, screen_width, screen_height), page, background_color, border, is_maximized, scale_factor)
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_data(
            spoons, homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list,
            exams_tasks_list, projects_tasks_list, daily_spoons, theme, icon_image,
            spoon_name_input, folder_one, folder_two, folder_three, folder_four,
            folder_five, folder_six, streak_dates,
            border_name, hubIcons_name, spoonIcons_name, restIcons_name, hotbar_name, manillaFolder_name, taskBorder_name, 
            scrollBar_name, calendarImages_name, themeBackgroundsImages_name, intro_name, label_favorites, spoons_used_today)

            # make the window vanish instantly
            try:
                pygame.display.quit()
            except Exception:
                pass

            # kick off the uploader in the background (fire-and-forget)
            spawn_background_upload()

            running = False
                
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION):
            for page_key, icon_rect in hub_icon_rects.items():
                if icon_rect.collidepoint(event.pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if page_key == "stats" and page != "stats" and settings_button_click_sfx: #####play the hub sounds
                            settings_button_click_sfx.play()

                        save_data(
                        spoons, homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list,
                        exams_tasks_list, projects_tasks_list, daily_spoons, theme, icon_image,
                        spoon_name_input, folder_one, folder_two, folder_three, folder_four,
                        folder_five, folder_six, streak_dates,
                        border_name, hubIcons_name, spoonIcons_name, restIcons_name, hotbar_name, manillaFolder_name, taskBorder_name, 
                        scrollBar_name, calendarImages_name, themeBackgroundsImages_name, intro_name, label_favorites, spoons_used_today)
                        prev_page = page
                        if page_key == "manage_tasks":
                            scroll_offset = 0
                        if page_key == "input_tasks" and prev_page != "input_tasks":
                            now = datetime.now()
                            task_month = now.month
                            task_day = now.day
                            max_days = calendar.monthrange(now.year, task_month)[1]
                            input_active = False

                        page = page_key
                    break

        elif event.type == pygame.KEYDOWN:
            # --- F11 toggle fullscreen ---
            if event.key == pygame.K_F11:
                scale_factor = get_scale_factor()
                if not is_maximized:
                    if IS_WINDOWS:
                        screen = pygame.display.set_mode(get_true_screen_size(), pygame.NOFRAME)
                        move_window(0, 0)
                    else:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    is_maximized = True
                else:
                    screen = pygame.display.set_mode(WINDOWED_SIZE)
                    if IS_WINDOWS:
                        move_window(0, 5)
                    is_maximized = False
                UI_elements_initialized = False
                scale = max(3, (6 / scale_factor)) if is_maximized else 3
                print(f"Scale factor: {scale_factor} - Border scale: {scale} - Maximized: {is_maximized}")
            # --- 1–7 quick navigation: 1=Calendar, 2=Inventory, 3=Manage, 4=Add Tasks, 5=Add Spoons, 6=Shop, 7=Stats ---
            else:
                ctrl_held = bool(event.mod & (pygame.KMOD_CTRL | pygame.KMOD_LCTRL | pygame.KMOD_RCTRL))
                if ctrl_held:
                    key_to_page = {
                        pygame.K_1: "calendar",
                        pygame.K_2: "input_spoons",
                        pygame.K_3: "input_tasks",
                        pygame.K_4: "manage_tasks",
                        pygame.K_5: "inventory",
                        pygame.K_6: "shop",
                        pygame.K_7: "stats",
                    }
                    new_page_key = key_to_page.get(event.key)
                    if new_page_key:
                        if new_page_key == "stats" and page != "stats" and settings_button_click_sfx:
                            settings_button_click_sfx.play()
                        save_data(spoons, homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list, exams_tasks_list, projects_tasks_list, daily_spoons, theme, icon_image, spoon_name_input, folder_one, folder_two, folder_three, folder_four, folder_five, folder_six, streak_dates, border_name, hubIcons_name, spoonIcons_name, restIcons_name, hotbar_name, manillaFolder_name, taskBorder_name, scrollBar_name, calendarImages_name, themeBackgroundsImages_name, intro_name, label_favorites, spoons_used_today)
                        prev_page = page
                        if new_page_key == "manage_tasks":
                            scroll_offset = 0
                        if new_page_key == "input_tasks" and prev_page != "input_tasks":
                            now = datetime.now()
                            task_month = now.month
                            task_day = now.day
                            max_days = calendar.monthrange(now.year, task_month)[1]
                            input_active = False
                        page = new_page_key
        new_page = hub_buttons(event)

        page = logic_task_toggle(event, page) #handle clicks with task toggles

        if page == "login":
            login_mode, login_username, login_password, login_input_active, page = logic_login(event, login_mode, login_username, login_password, login_input_active)

        elif page == "input_spoons" and UI_elements_initialized:
            spoons, daily_spoons, page, input_active = logic_input_spoons(event, daily_spoons, spoons, input_active)
            
        elif page == "input_tasks":
            input_active,page,folder,time_toggle_on, recurring_toggle_on,current_task,current_spoons,task_month,task_day,homework_tasks_list,chores_tasks_list,work_tasks_list,misc_tasks_list,exams_tasks_list,projects_tasks_list,task_how_often,task_how_long,task_repetitions_amount, start_time = logic_input_tasks(event,screen,current_task,current_spoons,folder,task_month,task_day,task_how_often,task_how_long,task_repetitions_amount,time_toggle_on,recurring_toggle_on,max_days,input_active,homework_tasks_list,chores_tasks_list,work_tasks_list,misc_tasks_list,exams_tasks_list,projects_tasks_list, start_time)
        elif page == "manage_tasks":
            page = logic_manage_tasks_hub(event, page, folder_rects)
        elif page == "complete_homework_tasks":
            scroll_offset = handle_task_scroll(event, scroll_offset, total_content_height, scroll_multiplier=17)
            task_completed, spoons, confetti_particles, streak_dates, level, spoons_used_today = logic_complete_tasks(homework_tasks_list, task_buttons_homework, event, spoons, streak_dates, streak_task_completed, level, spoons_used_today)
        elif page == "complete_chores_tasks":
            scroll_limit = max(0, len(chores_tasks_list) - 8)
            scroll_offset = handle_task_scroll(event, scroll_offset, scroll_limit, scroll_multiplier=1)
            task_completed, spoons, confetti_particles, streak_dates, level, spoons_used_today = logic_complete_tasks(chores_tasks_list, task_buttons_chores, event, spoons, streak_dates, streak_task_completed, level, spoons_used_today)
        elif page == "complete_work_tasks":
            scroll_limit = max(0, len(work_tasks_list) - 8)
            scroll_offset = handle_task_scroll(event, scroll_offset, scroll_limit, scroll_multiplier=1)
            task_completed, spoons, confetti_particles, streak_dates, level, spoons_used_today = logic_complete_tasks(work_tasks_list, task_buttons_work, event, spoons, streak_dates, streak_task_completed, level, spoons_used_today)
        elif page == "complete_misc_tasks":
            scroll_limit = max(0, len(misc_tasks_list) - 8)
            scroll_offset = handle_task_scroll(event, scroll_offset, scroll_limit, scroll_multiplier=1)
            task_completed, spoons, confetti_particles, streak_dates, level, spoons_used_today = logic_complete_tasks(misc_tasks_list, task_buttons_misc, event, spoons, streak_dates, streak_task_completed, level, spoons_used_today)
        elif page == "complete_exams_tasks":
            scroll_limit = max(0, len(exams_tasks_list) - 8)
            scroll_offset = handle_task_scroll(event, scroll_offset, scroll_limit, scroll_multiplier=1)
            task_completed, spoons, confetti_particles, streak_dates, level, spoons_used_today = logic_complete_tasks(exams_tasks_list, task_buttons_exams, event, spoons, streak_dates, streak_task_completed, level, spoons_used_today)
        elif page == "complete_projects_tasks":
            scroll_limit = max(0, len(projects_tasks_list) - 8)
            scroll_offset = handle_task_scroll(event, scroll_offset, scroll_limit, scroll_multiplier=1)
            task_completed, spoons, confetti_particles, streak_dates, level, spoons_used_today = logic_complete_tasks(projects_tasks_list, task_buttons_projects, event, spoons, streak_dates, streak_task_completed, level, spoons_used_today)
        elif page == "inventory":
            (inventory_tab, spoon_name_input, input_active, icon_image, 
             folder_one, folder_two, folder_three, folder_four, folder_five, folder_six, folders_dropdown_open,
            border, border_name, manillaFolder, manillaFolder_name, current_theme) = logic_inventory(event, tool_tips, inventory_tab, spoon_name_input, input_active, icon_image, 
                                                   folder_one, folder_two, folder_three, folder_four, folder_five, folder_six, folders_dropdown_open, border, border_name, manillaFolder, manillaFolder_name, current_theme)
            switch_theme(current_theme, globals())
        elif page == "calendar": 
            day_range_index, displayed_week_offset, displayed_month, displayed_year = logic_calendar(event, day_range_index, displayed_week_offset, displayed_month, displayed_year)
        elif page == "shop":
            tool_tips, spoon_name_input, input_active, current_theme, icon_image, folder_one, folder_two, folder_three, folder_four, folder_five, folder_six = logic_shop(event, tool_tips, spoon_name_input, input_active, current_theme, icon_image, folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
            border, hubIcons, spoonIcons, restIcons, hotbar, manillaFolder, taskBorder, scrollBar, calendarImages, themeBackgroundsImages, intro, border_name, hubIcons_name, spoonIcons_name, restIcons_name, hotbar_name, manillaFolder_name, taskBorder_name, scrollBar_name, calendarImages_name, themeBackgroundsImages_name, intro_name = logic_change_image(event, border, hubIcons, spoonIcons, restIcons, hotbar, manillaFolder, taskBorder, scrollBar, calendarImages, themeBackgroundsImages, intro, border_name, hubIcons_name, spoonIcons_name, restIcons_name, hotbar_name, manillaFolder_name, taskBorder_name, scrollBar_name, calendarImages_name, themeBackgroundsImages_name, intro_name)
            switch_theme(current_theme, globals())
        elif page == "stats":
            page = logic_stats(event, page)
    pygame.display.flip()

pygame.quit()
sys.exit()
