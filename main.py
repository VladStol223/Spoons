#Vladislav Stolbennikov
#8/7/2024
#Spoons App
#VS1.12

'''
Total pages:
1.) Add Spoons
2.) Add Tasks
3.) Complete Task
4.) Remove Tasks
5.) Calendar
6.) daily schedule
7.) Settings

To do:
 -Make the app look better:
    - Make all of the buttons slide in more than once. also add sliding back out.

 -Fix Daily Schedule:
    - Make atleast 5 days fit on the screen by making the time font smaller and the boxes smaller as well.
    - Change the colors.
    - Add a line under the Dates, and make sure the user knows when 'today' is. 
    - Fix scrolling
    - allow user to input their weekly schedule
    - Allow user to move tasks between time blocks
    - Allow user to remove tasks from time blocks
    - Allow user to add tasks to time blocks
    - Allow user to view all tasks in a week
    - Once they have set up their schedule how they like it, allow the user to save the schedule. This is going to suck ass.

 -Allow user to edit created tasks in their respective folders. In the Complete Folders section, add an "edit" mode where you can:
    - Allow user to change the names of the tasks
    - Allow user to change the number of spoons
    - Allow user to "uncomplete" the task
    - Allow user to partially complete the task

 -Allow user to change the number of task folders available to them (up to six) using folders one-six

 -Fix how it looks.......
    - Add Themes:
    - Frutiger Aero
    - Castelevania
    - Horror Jumpscares

 -Port to better language such as c++
'''

from os import name
from datetime import datetime

from config import *
from colors import COLORS
for name, value in COLORS.items():
    globals()[name] = value

import pygame
import sys
import calendar

pygame.init()

screen_height = 600
screen_width = 800
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Spoons")

####################################################################################################################################

# Drawing and Hub Functions
def hub_buttons_show():
    global hub_buttons_showing
    # Display hub buttons if toggle is on
    if hub_toggle.collidepoint(mouse_pos):
        hub_buttons_showing = True
        draw_hub_buttons(screen, page, tool_tips, hub_background_color, add_spoons_color, add_tasks_color, complete_tasks_color, remove_tasks_color, daily_schedule_color, calendar_color, settings_color)
    if hub_buttons_showing:
        draw_hub_buttons(screen, page, tool_tips, hub_background_color, add_spoons_color, add_tasks_color, complete_tasks_color, remove_tasks_color, daily_schedule_color, calendar_color, settings_color)
    if not hub_toggle.collidepoint(mouse_pos) and not hub_cover.collidepoint(mouse_pos):
        hub_buttons_showing = False
def hub_buttons(event): 
    global scroll_offset
    if not hub_buttons_showing:
        return None
    if event.type == pygame.MOUSEBUTTONDOWN:
        if hub_add_spoons.collidepoint(event.pos):
            save_data(spoons, homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list, 
              daily_spoons, current_theme, icon_image, spoon_name_input,
              folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
            return "input_spoons"
        elif hub_add_task.collidepoint(event.pos):
            save_data(spoons, homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list, 
              daily_spoons, current_theme, icon_image, spoon_name_input,
              folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
            return "input_tasks"
        elif hub_complete_task.collidepoint(event.pos):
            save_data(spoons, homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list, 
              daily_spoons, current_theme, icon_image, spoon_name_input,
              folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
            scroll_offset = 0
            return "complete_tasks"
        elif hub_remove_task.collidepoint(event.pos):
            save_data(spoons, homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list, 
              daily_spoons, current_theme, icon_image, spoon_name_input,
              folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
            scroll_offset = 0
            return "remove_tasks"
        elif hub_daily_schedule.collidepoint(event.pos):
            save_data(spoons, homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list, 
              daily_spoons, current_theme, icon_image, spoon_name_input,
              folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
            return "daily_schedule"
        elif hub_calendar.collidepoint(event.pos):
            save_data(spoons, homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list, 
              daily_spoons, current_theme, icon_image, spoon_name_input,
              folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
            return "calendar"
        elif hub_settings.collidepoint(event.pos):
            save_data(spoons, homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list, 
              daily_spoons, current_theme, icon_image, spoon_name_input,
              folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
            return "settings"
    return None 
from drawing_functions.draw_hub_buttons import draw_hub_buttons
from drawing_functions.draw_logic_input_spoons import draw_input_spoons, logic_input_spoons
from drawing_functions.draw_logic_input_tasks import draw_input_tasks, logic_input_tasks
from drawing_functions.draw_complete_tasks_hub import draw_complete_tasks_hub
from drawing_functions.draw_logic_complete_tasks import draw_complete_tasks, logic_complete_tasks, update_and_draw_confetti
from drawing_functions.draw_logic_remove_tasks import draw_remove_tasks, logic_remove_tasks
from drawing_functions.draw_remove_tasks_hub import draw_remove_tasks_hub
from drawing_functions.draw_daily_schedule import draw_daily_schedule, logic_daily_schedule, get_available_time_blocks, allocate_tasks_to_time_blocks, sort_tasks_by_priority_and_due_date
from drawing_functions.draw_logic_calendar import draw_calendar, logic_calendar
from drawing_functions.draw_logic_settings import draw_settings, logic_settings

# Miscellanous Functions
from load_save import save_data, load_data
from switch_themes import switch_theme
from handle_scroll import handle_task_scroll

spoons, homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list, daily_spoons, loaded_theme, icon_image, spoon_name_input, folder_one, folder_two, folder_three, folder_four, folder_five, folder_six = load_data()
current_theme = switch_theme(loaded_theme, globals())

# ----------------------------------------------------------------------------------------------------
# Main loop
# ----------------------------------------------------------------------------------------------------

while running:
    max_days = calendar.monthrange(datetime.now().year, task_month)[1]
    mouse_pos = pygame.mouse.get_pos()
    current_month = datetime.now().month
    current_day = datetime.now().day
    if int(current_day) > int(previous_day) or int(current_month) > int(previous_month):
        current_weekday = datetime.now().strftime("%a")
        spoons = daily_spoons.get(current_weekday, spoons)
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

    if page == "input_spoons":
        draw_input_spoons(screen, daily_spoons, spoons, done_button_color, input_active)
        hub_buttons_show()
    elif page == "input_tasks":
        draw_input_tasks(screen, spoons, current_task, current_spoons, input_active, 
                         folder, task_month, task_day, time_toggle_on, recurring_toggle_on,  start_time, end_time,
                         done_button_color, add_tasks_choose_folder_color, add_tasks_chosen_folder_color, icon_image, spoon_name_input,
                         task_how_often, task_how_long, task_repetitions_amount,
                         folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
        hub_buttons_show()
    elif page == "complete_tasks":
        draw_complete_tasks_hub(screen, spoons,
                            homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list,
                            complete_tasks_hub_folder_color, icon_image, spoon_name_input,
                            folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
        hub_buttons_show()
    elif page == "complete_homework_tasks":
        draw_complete_tasks(screen, "Homework", homework_tasks_list, task_buttons_homework, spoons,  scroll_offset,
                            complete_tasks_task_color, icon_image, spoon_name,
                            folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
        hub_buttons_show()
    elif page == "complete_chores_tasks":
        draw_complete_tasks(screen,"Chores", chores_tasks_list, task_buttons_chores, spoons, scroll_offset,
                        complete_tasks_task_color, icon_image, spoon_name,
                            folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
        hub_buttons_show()
    elif page == "complete_work_tasks":
        draw_complete_tasks(screen,"Work", work_tasks_list, task_buttons_work, spoons, scroll_offset,
                        complete_tasks_task_color, icon_image, spoon_name,
                            folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
        hub_buttons_show()
    elif page == "complete_misc_tasks":
        draw_complete_tasks(screen,"Misc", misc_tasks_list, task_buttons_misc, spoons, scroll_offset,
                        complete_tasks_task_color, icon_image, spoon_name,
                            folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
        hub_buttons_show()
    elif page == "remove_tasks":
        draw_remove_tasks_hub(screen, spoons,
                            homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list,
                            remove_tasks_hub_folder_color, icon_image, spoon_name_input,
                            folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
        hub_buttons_show()
    elif page == "remove_homework_tasks":
        draw_remove_tasks(screen, "Homework", homework_tasks_list, task_buttons_homework, spoons, scroll_offset,
                        remove_tasks_task_color, icon_image, spoon_name,
                        folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
        hub_buttons_show()
    elif page == "remove_chores_tasks":
        draw_remove_tasks(screen, "Chores", chores_tasks_list, task_buttons_chores, spoons, scroll_offset,
                        remove_tasks_task_color, icon_image, spoon_name,
                        folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
        hub_buttons_show()
    elif page == "remove_work_tasks":
        draw_remove_tasks(screen, "Work", work_tasks_list, task_buttons_work, spoons, scroll_offset,
                        remove_tasks_task_color, icon_image, spoon_name,
                        folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
        hub_buttons_show()
    elif page == "remove_misc_tasks":
        draw_remove_tasks(screen, "Misc", misc_tasks_list, task_buttons_misc, spoons, scroll_offset,
                        remove_tasks_task_color, icon_image, spoon_name,
                        folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
        hub_buttons_show()
    elif page == "daily_schedule":
        available_blocks_by_date, task_schedule = get_available_time_blocks(class_schedule, homework_tasks_list, work_tasks_list, chores_tasks_list, misc_tasks_list)
        draw_daily_schedule(screen, allocate_tasks_to_time_blocks(available_blocks_by_date, sort_tasks_by_priority_and_due_date(homework_tasks_list, work_tasks_list, chores_tasks_list, misc_tasks_list)),
                        homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list, day_offset,
                        homework_fol_color, chores_fol_color, work_fol_color, misc_fol_color, background_color, calendar_previous_day_header_color, calendar_next_day_header_color)
        hub_buttons_show()
    elif page == "calendar":
        draw_calendar(screen, spoon_name_input,
                  homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list,
                  displayed_month, displayed_year,
                  homework_fol_color, chores_fol_color, work_fol_color, misc_fol_color,calendar_month_color, 
                  calendar_previous_day_header_color, calendar_next_day_header_color, calendar_current_day_header_color,
                  calendar_previous_day_color, calendar_current_day_color, calendar_next_day_color,
                  folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
        hub_buttons_show()
    elif page == "settings":
        draw_settings(screen, tool_tips, spoon_name_input, icon_image, input_active, hub_background_color,
                  folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
        hub_buttons_show()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_data(spoons, homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list, 
              daily_spoons, current_theme, icon_image, spoon_name_input,
              folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
            running = False
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION):
            if hub_buttons_showing and hub_cover.collidepoint(event.pos):
                new_page = hub_buttons(event)
                if new_page:
                    page = new_page
                continue
        new_page = hub_buttons(event)
        if event.type == pygame.VIDEORESIZE:
            # Scale font sizes based on screen height
            big_font = pygame.font.Font(None, int(screen_height * 0.067))   # ~6.7% of screen height
            font = pygame.font.Font(None, int(screen_height * 0.06))        # ~6% of screen height
            small_font = pygame.font.Font(None, int(screen_height * 0.047)) # ~4.7% of screen height
            smaller_font = pygame.font.Font(None, int(screen_height * 0.033)) # ~3.3% of screen height

        if page == "input_spoons":
           spoons, daily_spoons, input_active, page = logic_input_spoons(event, short_rest_amount, half_rest_amount, full_rest_amount, 
                                                           daily_spoons, spoons, draw_input_spoons(screen, daily_spoons, spoons, done_button_color, input_active), input_active)
        elif page == "input_tasks":
            input_active, page, folder, time_toggle_on, recurring_toggle_on, current_task, current_spoons, task_month, task_day, start_time, end_time, homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list, task_how_often, task_how_long, task_repetitions_amount = logic_input_tasks(event, current_task, current_spoons, folder, task_month, task_day, task_how_often, task_how_long, task_repetitions_amount,
                      time_toggle_on, recurring_toggle_on, start_time, end_time, max_days, input_active, 
                      homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list)
        elif page == "complete_tasks":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if complete_homework_tasks.collidepoint(event.pos):
                    page = "complete_homework_tasks"
                elif complete_chores_tasks.collidepoint(event.pos):
                    page = "complete_chores_tasks"
                elif complete_work_tasks.collidepoint(event.pos):
                    page = "complete_work_tasks"
                elif complete_misc_tasks.collidepoint(event.pos):
                    page = "complete_misc_tasks"
        elif page == "complete_homework_tasks":
            scroll_limit = max(0, len(misc_tasks_list) - 8)
            scroll_offset = handle_task_scroll(event, scroll_offset, scroll_limit, scroll_multiplier=1)
            task_completed, spoons, confetti_particles = logic_complete_tasks(homework_tasks_list, task_buttons_homework, event, spoons)
        elif page == "complete_chores_tasks":
            scroll_limit = max(0, len(misc_tasks_list) - 8)
            scroll_offset = handle_task_scroll(event, scroll_offset, scroll_limit, scroll_multiplier=1)
            task_completed, spoons, confetti_particles = logic_complete_tasks(chores_tasks_list, task_buttons_chores, event, spoons)
        elif page == "complete_work_tasks":
            scroll_limit = max(0, len(misc_tasks_list) - 8)
            scroll_offset = handle_task_scroll(event, scroll_offset, scroll_limit, scroll_multiplier=1)
            task_completed, spoons, confetti_particles = logic_complete_tasks(work_tasks_list, task_buttons_work, event, spoons)
        elif page == "complete_misc_tasks":
            scroll_limit = max(0, len(misc_tasks_list) - 8)
            scroll_offset = handle_task_scroll(event, scroll_offset, scroll_limit, scroll_multiplier=1)
            task_completed, spoons, confetti_particles = logic_complete_tasks(misc_tasks_list, task_buttons_misc, event, spoons)
        elif page == "remove_tasks":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if remove_homework_tasks.collidepoint(event.pos):
                    page = "remove_homework_tasks"
                elif remove_chores_tasks.collidepoint(event.pos):
                    page = "remove_chores_tasks"
                elif remove_work_tasks.collidepoint(event.pos):
                    page = "remove_work_tasks"
                elif remove_misc_tasks.collidepoint(event.pos):
                    page = "remove_misc_tasks"
                elif remove_all_tasks_button.collidepoint(event.pos):
                    homework_tasks_list = []
                    chores_tasks_list = []
                    work_tasks_list = []
                    misc_tasks_list = []
        elif page == "remove_homework_tasks":
            scroll_limit = max(0, len(misc_tasks_list) - 8)
            scroll_offset = handle_task_scroll(event, scroll_offset, scroll_limit, scroll_multiplier=1)
            logic_remove_tasks(homework_tasks_list, task_buttons_homework, event)
        elif page == "remove_chores_tasks":
            scroll_limit = max(0, len(misc_tasks_list) - 8)
            scroll_offset = handle_task_scroll(event, scroll_offset, scroll_limit, scroll_multiplier=1)
            logic_remove_tasks(chores_tasks_list, task_buttons_chores, event)
        elif page == "remove_work_tasks":
            scroll_limit = max(0, len(misc_tasks_list) - 8)
            scroll_offset = handle_task_scroll(event, scroll_offset, scroll_limit, scroll_multiplier=1)
            logic_remove_tasks(work_tasks_list, task_buttons_work, event)
        elif page == "remove_misc_tasks":
            scroll_limit = max(0, len(misc_tasks_list) - 8)
            scroll_offset = handle_task_scroll(event, scroll_offset, scroll_limit, scroll_multiplier=1)
            logic_remove_tasks(misc_tasks_list, task_buttons_misc, event)
        elif page == "calendar": 
            displayed_month, displayed_year = logic_calendar(event, displayed_month, displayed_year)
        elif page == "daily_schedule":
            logic_daily_schedule(event, class_schedule, day_offset, homework_tasks_list, work_tasks_list, chores_tasks_list, misc_tasks_list)
        elif page == "settings":
            tool_tips, spoon_name_input, input_active, current_theme, icon_image, folder_one, folder_two, folder_three, folder_four, folder_five, folder_six = logic_settings(event, tool_tips, spoon_name_input, input_active, current_theme, icon_image, folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
            switch_theme(current_theme, globals())
    update_and_draw_confetti(screen, confetti_particles)
    pygame.display.flip()
pygame.quit()
sys.exit()