#Vladislav Stolbennikov
#8/7/2024
#Spoons App
#VS1.16

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
16.) Study
17.) Calendar
18.) Store
19.) Statistics

To do:
3.) -Add the following to the Calendar: 
-Visual streak tracking (e.g., fire symbol next to date) 
-Hover or click shows current streak length 
-Streak data stored and updated daily

4.) -Add the following core systems: 
-Streak System 
-Track daily completions by folder 
-Store current and longest streaks 
-Reset streak if no task is completed that day 
-Integrate "streak saver" item that prevents reset once 
-Goal System with Random Rewards 
-Allow users to define personal goals (e.g., 5 tasks/week) k
-Track goal progress 
-Upon completion, randomly award: 
-Themes 
-Icons 
-Icon names 
-Spoon bucks 
-Show progress and rewards in Manage Tasks Hub 
-Badge System 
-Unlock badges based on user actions (first task, streaks, spoons, etc.) 
-Track and store badges earned 
-Display badges in the Statistics page 
-Optional tiering system (bronze, silver, gold) 
-Spoon Bucks System 
-Track spoon buck balance 
-Award spoon bucks for task completions and goal rewards 
-Deduct spoon bucks in Store upon purchase 
-Display current balance consistently on UI

5.) -Add the following to the Store page: 
-Display available items (themes, icons, icon names, streak savers) 
-Show item previews and costs 
-Confirm purchase before deducting spoon bucks 
-Disable purchase if insufficient funds

make the UI look like the stardew valley interface. 
The top of the interface is going to be the inventory where the user will be able to see the their current spoons, spoonbucks, streak, and your little guy.
'''

from os import name
from datetime import datetime

from config import *
from colors import COLORS
for name, value in COLORS.items():
    globals()[name] = value

import pygame
import pygame_gui
import sys
import calendar

pygame.init()

screen_height = 520
screen_width = 960
manager = pygame_gui.UIManager((screen_width, screen_height), "themes/default.json")
button_widths = {}
hub_closing = False
UI_elements_initialized = False
clock = pygame.time.Clock()
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Spoons")

####################################################################################################################################
def hub_buttons(event):
    global scroll_offset

    if event.type != pygame.MOUSEBUTTONDOWN:
        return None

    button_actions = {
        "input_spoons": hub_add_spoons,
        "input_tasks": hub_add_task,
        "manage_tasks": hub_manage_task,
        "study": hub_study,
        "calendar": hub_calendar,
        "store": hub_store,
        "stats": hub_stats,
    }

    for page, rect in button_actions.items():
        if rect.collidepoint(event.pos):
            save_data(
                spoons, homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list, exams_tasks_list, projects_tasks_list,
                daily_spoons, current_theme, icon_image, spoon_name_input,
                folder_one, folder_two, folder_three, folder_four, folder_five, folder_six,
                streak_dates
            )
            if page == "manage_tasks":
                scroll_offset = 0
            return page

    return None

#drawing / logic functions
from drawing_functions.draw_hub_buttons import draw_hub_buttons
from drawing_functions.draw_logic_input_spoons import draw_input_spoons, logic_input_spoons
from drawing_functions.draw_logic_input_tasks import draw_input_tasks, logic_input_tasks
from drawing_functions.draw_logic_manage_tasks import draw_manage_tasks_hub, logic_manage_tasks_hub
from drawing_functions.draw_logic_complete_tasks import draw_complete_tasks, logic_complete_tasks, update_and_draw_confetti
from drawing_functions.draw_logic_remove_tasks import draw_remove_tasks, logic_remove_tasks
from drawing_functions.draw_daily_schedule import draw_daily_schedule, logic_daily_schedule, get_available_time_blocks, allocate_tasks_to_time_blocks, sort_tasks_by_priority_and_due_date
from drawing_functions.draw_logic_calendar import draw_calendar, logic_calendar
from drawing_functions.draw_logic_settings import draw_settings, logic_settings
from drawing_functions.draw_intro_sequence import draw_intro_sequence
from drawing_functions.draw_logic_task_toggle import draw_task_toggle, logic_task_toggle
from drawing_functions.draw_logic_edit_tasks import draw_edit_tasks, logic_edit_tasks
from drawing_functions.draw_logic_study import draw_study, logic_study, Timer
from drawing_functions.draw_logic_stats import draw_stats, logic_stats
from drawing_functions.draw_border import draw_border
from drawing_functions.draw_inventory import draw_inventory

# Miscellanous Functions
from load_save import save_data, load_data
from switch_themes import switch_theme
from handle_scroll import handle_task_scroll

draw_intro_sequence(screen, clock)
#loading save data
spoons, homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list, exams_tasks_list, projects_tasks_list, daily_spoons, loaded_theme, icon_image, spoon_name_input, folder_one, folder_two, folder_three, folder_four, folder_five, folder_six, streak_dates = load_data()
current_theme = switch_theme(loaded_theme, globals())

#timer init
study_timer = Timer()

# ----------------------------------------------------------------------------------------------------
# Main loop
# ----------------------------------------------------------------------------------------------------
while running:
    delta_time = clock.tick(60) / 1000.0
    max_days = calendar.monthrange(datetime.now().year, task_month)[1]
    mouse_pos = pygame.mouse.get_pos()
    current_month = datetime.now().month
    current_day = datetime.now().day
    if int(current_day) > int(previous_day) or int(current_month) > int(previous_month):
        current_weekday = datetime.now().strftime("%a")
        spoons = daily_spoons.get(current_weekday, spoons)
        streak_task_completed = False #reset streak task completion for new day
        if homework_tasks_list:
            for task in homework_tasks_list:
                if task[3] > 0:
                    task[3] -= 1
        if chores_tasks_list:
            for task in chores_tasks_list:
                if task[3] > 0:
                    task[3] -= 1
        if work_tasks_list:
            for task in work_tasks_list:
                if task[3] > 0:
                    task[3] -= 1
        if misc_tasks_list:
            for task in misc_tasks_list:
                if task[3] > 0:
                    task[3] -= 1
        previous_day = current_day
        previous_month = current_month
        print(f"Date changed: {current_month}/{current_day}. Days left updated and spoons reset to {spoons}.")

    if background_color == (-1,-1,-1):
        if current_theme == "light_academia":
            screen.blit(light_academia_background, (0,0))
    else:
        screen.fill(background_color)
        hub_background_color = background_color

    hub_icon_rects = draw_hub_buttons(screen, page, tool_tips, background_color,
                                  add_spoons_color, add_tasks_color,
                                  manage_tasks_color, study_color, calendar_color,
                                  store_color, stats_color, button_widths, hub_closing, delta_time)


    if page == "input_spoons":
        if not UI_elements_initialized:
            draw_input_spoons(screen, manager, False, daily_spoons, spoons, delta_time, icon_image)
            UI_elements_initialized = True
        else:
            draw_input_spoons(screen, manager, True, daily_spoons, spoons, delta_time, icon_image)
        
    elif page == "input_tasks":
        draw_input_tasks(screen, spoons, current_task, current_spoons, input_active, 
                         folder, task_month, task_day, time_toggle_on, recurring_toggle_on,  start_time, end_time,
                         done_button_color, add_tasks_choose_folder_color, add_tasks_chosen_folder_color, icon_image, spoon_name_input,
                         task_how_often, task_how_long, task_repetitions_amount,
                         folder_one, folder_two, folder_three, folder_four, folder_five, folder_six
                         , homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list, exams_tasks_list, projects_tasks_list)
        draw_inventory(screen, spoons, icon_image, spoon_name_input, streak_dates, coins, level)
        
    elif page == "manage_tasks":
        folder_rects = draw_manage_tasks_hub(screen, spoons,
                            homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list,
                            complete_tasks_hub_folder_color, icon_image, spoon_name_input,
                            folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
        
    elif page == "complete_homework_tasks":
        draw_complete_tasks(screen, "Homework", homework_tasks_list, task_buttons_homework, spoons,  scroll_offset,
                            complete_tasks_task_color, icon_image, spoon_name,
                            folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
        draw_task_toggle(screen, page)
        
    elif page == "complete_chores_tasks":
        draw_complete_tasks(screen,"Chores", chores_tasks_list, task_buttons_chores, spoons, scroll_offset,
                        complete_tasks_task_color, icon_image, spoon_name,
                            folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
        draw_task_toggle(screen, page)
        
    elif page == "complete_work_tasks":
        draw_complete_tasks(screen,"Work", work_tasks_list, task_buttons_work, spoons, scroll_offset,
                        complete_tasks_task_color, icon_image, spoon_name,
                            folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
        draw_task_toggle(screen, page)
        
    elif page == "complete_misc_tasks":
        draw_complete_tasks(screen,"Misc", misc_tasks_list, task_buttons_misc, spoons, scroll_offset,
                        complete_tasks_task_color, icon_image, spoon_name,
                            folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
        draw_task_toggle(screen, page)

    elif page == "complete_exams_tasks":
        draw_complete_tasks(screen,"Exams", exams_tasks_list, task_buttons_exams, spoons, scroll_offset,
                        complete_tasks_task_color, icon_image, spoon_name,
                            folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
        draw_task_toggle(screen, page)

    elif page == "complete_projects_tasks":
        draw_complete_tasks(screen,"Projects", projects_tasks_list, task_buttons_projects, spoons, scroll_offset,
                        complete_tasks_task_color, icon_image, spoon_name,
                            folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
        draw_task_toggle(screen, page)
        
    elif page == "edit_homework_tasks":
        draw_edit_tasks(screen, spoons, "Homework", homework_tasks_list, task_buttons_homework, input_active,
                                                 scroll_offset, complete_tasks_task_color, icon_image, spoon_name,
                                                 folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
        draw_task_toggle(screen, page)
        
    elif page == "edit_chores_tasks":
        draw_edit_tasks(screen, spoons, "Chores", chores_tasks_list, task_buttons_chores, input_active,
                                                 scroll_offset, complete_tasks_task_color, icon_image, spoon_name,
                                                 folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
        draw_task_toggle(screen, page)
        
    elif page == "edit_work_tasks":
        draw_edit_tasks(screen, spoons, "Work", work_tasks_list, task_buttons_work, input_active,
                                                 scroll_offset, complete_tasks_task_color, icon_image, spoon_name,
                                                 folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
        draw_task_toggle(screen, page)
        
    elif page == "edit_misc_tasks":
        draw_edit_tasks(screen, spoons, "Misc", misc_tasks_list, task_buttons_misc, input_active,
                                                 scroll_offset, complete_tasks_task_color, icon_image, spoon_name,
                                                 folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
        draw_task_toggle(screen, page)
        
    elif page == "remove_homework_tasks":
        draw_remove_tasks(screen, "Homework", homework_tasks_list, task_buttons_homework, spoons, scroll_offset,
                        remove_tasks_task_color, icon_image, spoon_name,
                        folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
        draw_task_toggle(screen, page)
        
    elif page == "remove_chores_tasks":
        draw_remove_tasks(screen, "Chores", chores_tasks_list, task_buttons_chores, spoons, scroll_offset,
                        remove_tasks_task_color, icon_image, spoon_name,
                        folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
        draw_task_toggle(screen, page)
        
    elif page == "remove_work_tasks":
        draw_remove_tasks(screen, "Work", work_tasks_list, task_buttons_work, spoons, scroll_offset,
                        remove_tasks_task_color, icon_image, spoon_name,
                        folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
        draw_task_toggle(screen, page)
        
    elif page == "remove_misc_tasks":
        draw_remove_tasks(screen, "Misc", misc_tasks_list, task_buttons_misc, spoons, scroll_offset,
                        remove_tasks_task_color, icon_image, spoon_name,
                        folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
        draw_task_toggle(screen, page)
        
    elif page == "study":
        draw_study(screen, study_timer, font, dropdown_open, list(TIMER_MODES.keys()))
        
    elif page == "calendar":
        draw_calendar(screen, spoon_name_input,
                  homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list,
                  displayed_month, displayed_year,
                  homework_fol_color, chores_fol_color, work_fol_color, misc_fol_color,calendar_month_color, 
                  calendar_previous_day_header_color, calendar_next_day_header_color, calendar_current_day_header_color,
                  calendar_previous_day_color, calendar_current_day_color, calendar_next_day_color,
                  folder_one, folder_two, folder_three, folder_four, folder_five, folder_six,
                  streak_dates)
        
    elif page == "store":
        draw_settings(screen, tool_tips, spoon_name_input, icon_image, input_active, hub_background_color,
                  folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
        
    elif page == "stats":
        draw_stats(screen, font, big_font, personal_stats, global_leaderboard)

    draw_border(screen, (0, 0, screen_width, screen_height), page)
        
    for event in pygame.event.get():
        manager.process_events(event)
        if event.type == pygame.QUIT:
            save_data(spoons, homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list, exams_tasks_list, projects_tasks_list,
              daily_spoons, current_theme, icon_image, spoon_name_input,
              folder_one, folder_two, folder_three, folder_four, folder_five, folder_six,
              streak_dates)
            running = False
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION):
            for page_key, icon_rect in hub_icon_rects.items():
                if icon_rect.collidepoint(event.pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        save_data(
                            spoons, homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list, exams_tasks_list, projects_tasks_list,
                            daily_spoons, current_theme, icon_image, spoon_name_input,
                            folder_one, folder_two, folder_three, folder_four, folder_five, folder_six,
                            streak_dates
                        )
                        if page_key == "manage_tasks":
                            scroll_offset = 0
                        page = page_key
                    break

        new_page = hub_buttons(event)
        if event.type == pygame.VIDEORESIZE:
            screen_width, screen_height = event.w, event.h
            screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
            manager.set_window_resolution((screen_width, screen_height))
            
            font = pygame.font.Font(None, int(screen_height * 0.06))
            big_font = pygame.font.Font(None, int(screen_height * 0.067))
            small_font = pygame.font.Font(None, int(screen_height * 0.047))
            smaller_font = pygame.font.Font(None, int(screen_height * 0.033))

            UI_elements_initialized = False

        page = logic_task_toggle(event, page) #handle clicks with task toggles

        if page == "input_spoons" and UI_elements_initialized:
            spoons, daily_spoons, page = logic_input_spoons(event, manager, short_rest_amount, half_rest_amount, full_rest_amount, 
                                                           daily_spoons, spoons)
            
        elif page == "input_tasks":
            input_active,page,folder,recurring_toggle_on,current_task,current_spoons,task_month,task_day,homework_tasks_list,chores_tasks_list,work_tasks_list,misc_tasks_list,exams_tasks_list,projects_tasks_list,task_how_often,task_how_long,task_repetitions_amount = logic_input_tasks(event,screen,current_task,current_spoons,folder,task_month,task_day,task_how_often,task_how_long,task_repetitions_amount,recurring_toggle_on,max_days,input_active,homework_tasks_list,chores_tasks_list,work_tasks_list,misc_tasks_list,exams_tasks_list,projects_tasks_list)
        elif page == "manage_tasks":
            page = logic_manage_tasks_hub(event, page, folder_rects)
        elif page == "complete_homework_tasks":
            scroll_limit = max(0, len(homework_tasks_list) - 8)
            scroll_offset = handle_task_scroll(event, scroll_offset, scroll_limit, scroll_multiplier=1)
            task_completed, spoons, confetti_particles, streak_dates = logic_complete_tasks(homework_tasks_list, task_buttons_homework, event, spoons, streak_dates, streak_task_completed)
        elif page == "complete_chores_tasks":
            scroll_limit = max(0, len(chores_tasks_list) - 8)
            scroll_offset = handle_task_scroll(event, scroll_offset, scroll_limit, scroll_multiplier=1)
            task_completed, spoons, confetti_particles, streak_dates = logic_complete_tasks(chores_tasks_list, task_buttons_chores, event, spoons, streak_dates, streak_task_completed)
        elif page == "complete_work_tasks":
            scroll_limit = max(0, len(work_tasks_list) - 8)
            scroll_offset = handle_task_scroll(event, scroll_offset, scroll_limit, scroll_multiplier=1)
            task_completed, spoons, confetti_particles, streak_dates = logic_complete_tasks(work_tasks_list, task_buttons_work, event, spoons, streak_dates, streak_task_completed)
        elif page == "complete_misc_tasks":
            scroll_limit = max(0, len(misc_tasks_list) - 8)
            scroll_offset = handle_task_scroll(event, scroll_offset, scroll_limit, scroll_multiplier=1)
            task_completed, spoons, confetti_particles, streak_dates = logic_complete_tasks(misc_tasks_list, task_buttons_misc, event, spoons, streak_dates, streak_task_completed)
        elif page == "complete_exams_tasks":
            scroll_limit = max(0, len(exams_tasks_list) - 8)
            scroll_offset = handle_task_scroll(event, scroll_offset, scroll_limit, scroll_multiplier=1)
            task_completed, spoons, confetti_particles, streak_dates = logic_complete_tasks(exams_tasks_list, task_buttons_exams, event, spoons, streak_dates, streak_task_completed)
        elif page == "complete_projects_tasks":
            scroll_limit = max(0, len(projects_tasks_list) - 8)
            scroll_offset = handle_task_scroll(event, scroll_offset, scroll_limit, scroll_multiplier=1)
            task_completed, spoons, confetti_particles, streak_dates = logic_complete_tasks(projects_tasks_list, task_buttons_projects, event, spoons, streak_dates, streak_task_completed)
        elif page == "edit_homework_tasks":
            scroll_limit = max(0, len(homework_tasks_list) - 8)
            scroll_offset = handle_task_scroll(event, scroll_offset, scroll_limit, scroll_multiplier=1)
            input_active, homework_tasks_list = logic_edit_tasks(event, input_active, mouse_pos, homework_tasks_list, task_buttons_homework, max_days)
        elif page == "edit_chores_tasks":
            scroll_limit = max(0, len(chores_tasks_list) - 8)
            scroll_offset = handle_task_scroll(event, scroll_offset, scroll_limit, scroll_multiplier=1)
            input_active, chores_tasks_list = logic_edit_tasks(event, input_active, mouse_pos, chores_tasks_list, task_buttons_chores, max_days)
        elif page == "edit_work_tasks":
            scroll_limit = max(0, len(work_tasks_list) - 8)
            scroll_offset = handle_task_scroll(event, scroll_offset, scroll_limit, scroll_multiplier=1)
            input_active, work_tasks_list = logic_edit_tasks(event, input_active, mouse_pos, work_tasks_list, task_buttons_work, max_days)
        elif page == "edit_misc_tasks":
            scroll_limit = max(0, len(misc_tasks_list) - 8)
            scroll_offset = handle_task_scroll(event, scroll_offset, scroll_limit, scroll_multiplier=1)
            input_active, misc_tasks_list = logic_edit_tasks(event, input_active, mouse_pos, misc_tasks_list, task_buttons_misc, max_days)
        elif page == "remove_homework_tasks":
            scroll_limit = max(0, len(homework_tasks_list) - 8)
            scroll_offset = handle_task_scroll(event, scroll_offset, scroll_limit, scroll_multiplier=1)
            logic_remove_tasks(homework_tasks_list, task_buttons_homework, event)
        elif page == "remove_chores_tasks":
            scroll_limit = max(0, len(chores_tasks_list) - 8)
            scroll_offset = handle_task_scroll(event, scroll_offset, scroll_limit, scroll_multiplier=1)
            logic_remove_tasks(chores_tasks_list, task_buttons_chores, event)
        elif page == "remove_work_tasks":
            scroll_limit = max(0, len(work_tasks_list) - 8)
            scroll_offset = handle_task_scroll(event, scroll_offset, scroll_limit, scroll_multiplier=1)
            logic_remove_tasks(work_tasks_list, task_buttons_work, event)
        elif page == "remove_misc_tasks":
            scroll_limit = max(0, len(misc_tasks_list) - 8)
            scroll_offset = handle_task_scroll(event, scroll_offset, scroll_limit, scroll_multiplier=1)
            logic_remove_tasks(misc_tasks_list, task_buttons_misc, event)
        elif page == "study":
            dropdown_open = logic_study(event, study_timer, dropdown_open, list(TIMER_MODES.keys()))
        elif page == "calendar": 
            displayed_month, displayed_year = logic_calendar(event, displayed_month, displayed_year)
        elif page == "store":
            tool_tips, spoon_name_input, input_active, current_theme, icon_image, folder_one, folder_two, folder_three, folder_four, folder_five, folder_six = logic_settings(event, tool_tips, spoon_name_input, input_active, current_theme, icon_image, folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
            switch_theme(current_theme, globals())
        elif page == "stats":
            logic_stats(event)
    update_and_draw_confetti(screen, confetti_particles)
    pygame.display.flip()
    manager.update(delta_time)
    manager.draw_ui(screen)

pygame.quit()
sys.exit()