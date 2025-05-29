from config import *

from drawing_functions.draw_rounded_button import draw_rounded_button
from drawing_functions.draw_input_box import draw_input_box
import importlib
draw_complete_tasks_folders = importlib.import_module("drawing_functions.draw_complete_tasks_folders").draw_complete_tasks_folders
ctf_mod = importlib.import_module("drawing_functions.draw_complete_tasks_folders")


import pygame
import math
from datetime import datetime, timedelta

"""
Summary:
    Draws the task input interface on the given screen, including task name, spoons needed, due date, and time options.

Parameters:
    screen (pygame.Surface): The surface on which the task input interface will be drawn.
    spoons (int): The current number of spoons.
    current_task (str): The current input text for the task name.
    current_spoons (int): The current input text for the spoons needed.
    input_active (str or bool): The currently active input box or False if none is active.
    folder (str): The current folder selected for the task.
    task_month (int): The month of the task's due date.
    task_day (int): The day of the task's due date.
    time_toggle_on (bool): Indicates whether the time toggle is on or off.
    start_time (list): The start time of the task in [HH, MM] format.
    end_time (list): The end time of the task in [HH, MM] format.
    done_button_color (tuple): Color for the 'Done' button.
    add_tasks_choose_folder_color (tuple): Color for the folder selection button.
    add_tasks_chosen_folder_color (tuple): Color for the chosen folder button.

Returns:
    No returns.
"""

# somewhere at module top:
layout_heights = {
    "task_label":                  0.28,    # “Enter task name:”
    "task_input_line":             0.35,   # y=195/600
    "due_date_label":              0.48,   # “Enter due date:” & “Enter Start date:”
    "due_date_input_line":         0.55,   # y=305/600
    "how_often_label":             0.550,   # “How Often:”
    "how_often_input_line":        0.55,   # y=305/600
    "how_long_label":              0.538,   # “How Long:”
    "how_long_input_line":         0.583,   # y=290/600
    "repetitions_amount_label":    0.642,   # “Repetitions:”
    "repetitions_input_line":      0.683,   # y=350/600
    "spoons_label":                0.68,   # “Enter spoons needed:”
    "spoons_input_line":           0.75,   # y=420/600
    "time_toggle_label":           0.100,   # y=60/600
    "done_button":                 0.833,   # y=500/600
    "top_arrow":                   0.447,   # y=303/600
    "bottom_arrow":                0.489,   # y=328/600
}

def draw_input_tasks(screen, spoons, current_task, current_spoons, input_active, 
                     folder, task_month, task_day, time_toggle_on, recurring_toggle_on,
                     start_time, end_time, done_button_color,
                     add_tasks_choose_folder_color, add_tasks_chosen_folder_color,
                     icon_image, spoon_name_input, task_how_often, task_how_long,
                     task_repetitions_amount, folder_one, folder_two,
                     folder_three, folder_four, folder_five, folder_six
                     , homework_tasks_list,chores_tasks_list, work_tasks_list, misc_tasks_list, exams_tasks_list, projects_tasks_list):

    screen_h = screen.get_height()
    y_pos = {k: int(v * screen_h) for k, v in layout_heights.items()}

    # Task Input boxes
    task_input_box = pygame.Rect(250, y_pos["task_input_line"], 300, 50)
    spoon_input_box = pygame.Rect(375, y_pos["spoons_input_line"], 50, 50)
    done_button       = pygame.Rect(300, y_pos["done_button"],       200, 50)

    # Recurring toggle (still at fixed y=50, could be pulled into layout_heights too)
    recurring_toggle_button = pygame.Rect(760, 50, 40, 40)

    # Repeat-task inputs & arrows
    how_often_input_box          = pygame.Rect(410, y_pos["how_often_input_line"], 120, 50)
    how_often_up_button          = pygame.Rect(510, int(y_pos["top_arrow"] + 7), 15, 15)
    how_often_down_button        = pygame.Rect(510, int(y_pos["bottom_arrow"] + 7), 15, 15)

    how_long_input_box           = pygame.Rect(555, y_pos["how_long_input_line"], 115, 30)
    how_long_up_button           = pygame.Rect(650, int(y_pos["top_arrow"] - 7), 15, 15)
    how_long_down_button         = pygame.Rect(650, int(y_pos["bottom_arrow"] - 7), 15, 15)

    repetitions_amount_input_box = pygame.Rect(555, y_pos["repetitions_input_line"], 115, 30)
    repetitions_amount_up_button = pygame.Rect(650, y_pos["repetitions_input_line"] + 0, 15, 15)
    repetitions_amount_down_button = pygame.Rect(650, y_pos["repetitions_input_line"] + 15, 15, 15)

    # Due-date boxes (normal vs shifted for recurring)
    month_input_box_normal = pygame.Rect(280, y_pos["due_date_input_line"], 160, 50)
    month_up_button_normal = pygame.Rect(420, int(y_pos["top_arrow"] + 7), 15, 15)
    month_down_button_normal = pygame.Rect(420, int(y_pos["bottom_arrow"] + 7), 15, 15)
    day_input_box_normal   = pygame.Rect(465, y_pos["due_date_input_line"], 70, 50)
    day_up_button_normal   = pygame.Rect(515, int(y_pos["top_arrow"] + 7), 15, 15)
    day_down_button_normal = pygame.Rect(515, int(y_pos["bottom_arrow"] + 7), 15, 15)

    month_input_box_recurring_shifted = pygame.Rect(150, y_pos["due_date_input_line"], 160, 50)
    month_up_button_recurring_shifted = pygame.Rect(290, int(y_pos["top_arrow"] + 7), 15, 15)
    month_down_button_recurring_shifted = pygame.Rect(290, int(y_pos["bottom_arrow"] + 7), 15, 15)
    day_input_box_recurring_shifted   = pygame.Rect(325, y_pos["due_date_input_line"], 70, 50)
    day_up_button_recurring_shifted   = pygame.Rect(375, int(y_pos["top_arrow"] + 7), 15, 15)
    day_down_button_recurring_shifted = pygame.Rect(375, int(y_pos["bottom_arrow"] + 7), 15, 15)

    # Draw folder selector & spoons
    draw_complete_tasks_folders(screen,folder,folder_one,folder_two,folder_three,folder_four,folder_five,folder_six, homework_tasks_list,chores_tasks_list, work_tasks_list, misc_tasks_list, exams_tasks_list, projects_tasks_list)
    

    # Text‐inputs
    draw_input_box(screen, task_input_box,input_active == "task", current_task,GREEN, LIGHT_GRAY)#type: ignore

    draw_input_box(screen, spoon_input_box,input_active == "spoons", str(current_spoons),GREEN, LIGHT_GRAY)#type: ignore


    up_arrow   = font.render(">", True, BLACK)#type: ignore
    down_arrow = font.render("<", True, BLACK)#type: ignore

    if recurring_toggle_on:
        # recurring date & repeat settings
        screen.blit(font.render("Enter Start date:", True, BLACK),(170, y_pos["due_date_label"]))#type: ignore
    
        draw_input_box(screen, month_input_box_recurring_shifted,False, str(months[task_month - 1]),GREEN, LIGHT_GRAY)#type: ignore
    
        draw_input_box(screen, day_input_box_recurring_shifted,False, str(task_day), GREEN, LIGHT_GRAY)#type: ignore
    
        # arrows
        for btn in (month_up_button_recurring_shifted,
                    month_down_button_recurring_shifted,
                    day_up_button_recurring_shifted,
                    day_down_button_recurring_shifted):
            pygame.draw.rect(screen, done_button_color, btn)
        screen.blit(up_arrow,   (month_up_button_recurring_shifted.x, month_up_button_recurring_shifted.y - 7))
        screen.blit(down_arrow, (month_down_button_recurring_shifted.x, month_down_button_recurring_shifted.y - 7))
        screen.blit(up_arrow,   (day_up_button_recurring_shifted.x, day_up_button_recurring_shifted.y - 7))
        screen.blit(down_arrow, (day_down_button_recurring_shifted.x, day_down_button_recurring_shifted.y - 7))

        # How Often
        screen.blit(font.render("How Often:", True, BLACK), (395, y_pos["how_often_label"]))#type: ignore
    
        draw_input_box(screen, how_often_input_box, False, f"{task_how_often} days", GREEN, LIGHT_GRAY)#type: ignore
    
        pygame.draw.rect(screen, done_button_color, how_often_up_button)
        pygame.draw.rect(screen, done_button_color, how_often_down_button)
        screen.blit(up_arrow,   (how_often_up_button.x, how_often_up_button.y - 7))
        screen.blit(down_arrow, (how_often_down_button.x, how_often_down_button.y - 7))

        # How Long
        screen.blit(small_font.render("How Long:", True, BLACK),(560, y_pos["how_long_label"]))#type: ignore
    
        draw_input_box( screen, how_long_input_box, False, f"{task_how_long} weeks", GREEN, LIGHT_GRAY)#type: ignore
    
        pygame.draw.rect(screen, done_button_color, how_long_up_button)
        pygame.draw.rect(screen, done_button_color, how_long_down_button)
        screen.blit(up_arrow,   (how_long_up_button.x, how_long_up_button.y - 7))
        screen.blit(down_arrow, (how_long_down_button.x, how_long_down_button.y - 7))

        # Repetitions
        screen.blit(small_font.render("Repetitions:", True, BLACK), (552, y_pos["repetitions_amount_label"]))#type: ignore
    
        draw_input_box( screen, repetitions_amount_input_box, False, f"{task_repetitions_amount} times", GREEN, LIGHT_GRAY)#type: ignore
    
        pygame.draw.rect(screen, done_button_color, repetitions_amount_up_button)
        pygame.draw.rect(screen, done_button_color, repetitions_amount_down_button)
        screen.blit(up_arrow,   (repetitions_amount_up_button.x, repetitions_amount_up_button.y - 7))
        screen.blit(down_arrow, (repetitions_amount_down_button.x, repetitions_amount_down_button.y - 7))

        screen.blit( small_font.render("Remove Recurring Task", True, BLACK), (recurring_toggle_button.x - 280, y_pos["time_toggle_label"]))#type: ignore
    

    else:
        # normal due date
        screen.blit( font.render("Enter due date:", True, BLACK),  (305, y_pos["due_date_label"]))#type: ignore
    
        draw_input_box(  screen, month_input_box_normal, input_active == "month", str(months[task_month - 1]), GREEN, LIGHT_GRAY)#type: ignore
    
        draw_input_box(  screen, day_input_box_normal, input_active == "day",  str(task_day), GREEN, LIGHT_GRAY)#type: ignore
    
        for btn in (month_up_button_normal, month_down_button_normal,
                    day_up_button_normal,   day_down_button_normal):
            pygame.draw.rect(screen, done_button_color, btn)
        screen.blit(up_arrow,   (month_up_button_normal.x, month_up_button_normal.y - 7))
        screen.blit(down_arrow, (month_down_button_normal.x, month_down_button_normal.y - 7))
        screen.blit(up_arrow,   (day_up_button_normal.x, day_up_button_normal.y - 7))
        screen.blit(down_arrow, (day_down_button_normal.x, day_down_button_normal.y - 7))

        #screen.blit(small_font.render("Add Recurring Task", True, BLACK),(recurring_toggle_button.x - 240, y_pos["time_toggle_label"]))

    # bottom labels & done#type: ignore
    screen.blit(font.render("Enter task name:", True, BLACK),(300, y_pos["task_label"]))#type: ignore
    screen.blit(font.render("Enter spoons needed:", True, BLACK),(280, y_pos["spoons_label"]))#type: ignore
    draw_rounded_button(screen, done_button, done_button_color, BLACK, 15)#type: ignore
    screen.blit(font.render("Done", True, WHITE),(done_button.x + 69, done_button.y + (done_button.height // 4)))#type: ignore


"""
Summary:
    Handles the logic for interacting with the task input interface, including updating task details and toggling time options.

Parameters:
    event (pygame.event.Event): The event object containing information about the user input.
    current_task (str): The current input text for the task name.
    current_spoons (int): The current input text for the spoons needed.
    folder (str): The current folder selected for the task.
    task_month (int): The month of the task's due date.
    task_day (int): The day of the task's due date.
    time_toggle_on (bool): Indicates whether the time toggle is on or off.
    start_time (list): The start time of the task in [HH, MM] format.
    end_time (list): The end time of the task in [HH, MM] format.
    max_days (int): The maximum number of days in the selected month.
    input_active (str or bool): The currently active input box or False if none is active.
    homework_tasks_list (list): List of homework tasks.
    chores_tasks_list (list): List of chores tasks.
    work_tasks_list (list): List of work tasks.
    misc_tasks_list (list): List of miscellaneous tasks.

Returns:
    tuple: Updated current_task, current_spoons, task_month, task_day, time_toggle_on, start_time, end_time, input_active.
"""

import math

def logic_input_tasks(event,screen,current_task,current_spoons,folder,task_month,task_day,task_how_often,task_how_long,task_repetitions_amount,recurring_toggle_on,max_days,input_active,homework_tasks_list,chores_tasks_list,work_tasks_list,misc_tasks_list,exams_tasks_list,projects_tasks_list): 

    page = "input_tasks"

    screen_h = screen.get_height()
    y_pos = {k: int(v * screen_h) for k, v in layout_heights.items()}

    # Task Input boxes
    task_input_box = pygame.Rect(250, y_pos["task_input_line"], 300, 50)
    spoon_input_box = pygame.Rect(375, y_pos["spoons_input_line"], 50, 50)
    done_button       = pygame.Rect(300, y_pos["done_button"],       200, 50)

    # Recurring toggle (still at fixed y=50, could be pulled into layout_heights too)
    recurring_toggle_button = pygame.Rect(760, 50, 40, 40)

    # Repeat-task inputs & arrows
    how_often_input_box          = pygame.Rect(410, y_pos["how_often_input_line"], 120, 50)
    how_often_up_button          = pygame.Rect(510, int(y_pos["top_arrow"] + 7), 15, 15)
    how_often_down_button        = pygame.Rect(510, int(y_pos["bottom_arrow"] + 7), 15, 15)

    how_long_input_box           = pygame.Rect(555, y_pos["how_long_input_line"], 115, 30)
    how_long_up_button           = pygame.Rect(650, int(y_pos["top_arrow"] - 7), 15, 15)
    how_long_down_button         = pygame.Rect(650, int(y_pos["bottom_arrow"] - 7), 15, 15)

    repetitions_amount_input_box = pygame.Rect(555, y_pos["repetitions_input_line"], 115, 30)
    repetitions_amount_up_button = pygame.Rect(650, y_pos["repetitions_input_line"] + 0, 15, 15)
    repetitions_amount_down_button = pygame.Rect(650, y_pos["repetitions_input_line"] + 15, 15, 15)

    # Due-date boxes (normal vs shifted for recurring)
    month_input_box_normal = pygame.Rect(280, y_pos["due_date_input_line"], 160, 50)
    month_up_button_normal = pygame.Rect(420, int(y_pos["top_arrow"] + 7), 15, 15)
    month_down_button_normal = pygame.Rect(420, int(y_pos["bottom_arrow"] + 7), 15, 15)
    day_input_box_normal   = pygame.Rect(465, y_pos["due_date_input_line"], 70, 50)
    day_up_button_normal   = pygame.Rect(515, int(y_pos["top_arrow"] + 7), 15, 15)
    day_down_button_normal = pygame.Rect(515, int(y_pos["bottom_arrow"] + 7), 15, 15)

    month_input_box_recurring_shifted = pygame.Rect(150, y_pos["due_date_input_line"], 160, 50)
    month_up_button_recurring_shifted = pygame.Rect(290, int(y_pos["top_arrow"] + 7), 15, 15)
    month_down_button_recurring_shifted = pygame.Rect(290, int(y_pos["bottom_arrow"] + 7), 15, 15)
    day_input_box_recurring_shifted   = pygame.Rect(325, y_pos["due_date_input_line"], 70, 50)
    day_up_button_recurring_shifted   = pygame.Rect(375, int(y_pos["top_arrow"] + 7), 15, 15)
    day_down_button_recurring_shifted = pygame.Rect(375, int(y_pos["bottom_arrow"] + 7), 15, 15)

    if event.type == pygame.MOUSEBUTTONDOWN:
        # Toggle recurring task entry
        if recurring_toggle_button.collidepoint(event.pos):
            recurring_toggle_on = not recurring_toggle_on

        # Task input boxes
        if task_input_box.collidepoint(event.pos):
            input_active = "task"
        elif spoon_input_box.collidepoint(event.pos):
            input_active = "spoons"

        # Month/Day adjustments
        if recurring_toggle_on:
            # Using the shifted rects for recurring toggle
            if month_up_button_recurring_shifted.collidepoint(event.pos):
                task_month = task_month + 1 if task_month < 12 else 1
            elif month_down_button_recurring_shifted.collidepoint(event.pos):
                task_month = task_month - 1 if task_month > 1 else 12
            elif day_up_button_recurring_shifted.collidepoint(event.pos):
                task_day = int(task_day) + 1 if int(task_day) < max_days else 1
            elif day_down_button_recurring_shifted.collidepoint(event.pos):
                task_day = int(task_day) - 1 if int(task_day) > 1 else max_days
        else:
            # Normal (no recurring)
            if month_up_button_normal.collidepoint(event.pos):
                task_month = task_month + 1 if task_month < 12 else 1
            elif month_down_button_normal.collidepoint(event.pos):
                task_month = task_month - 1 if task_month > 1 else 12
            elif day_up_button_normal.collidepoint(event.pos):
                task_day = int(task_day) + 1 if int(task_day) < max_days else 1
            elif day_down_button_normal.collidepoint(event.pos):
                task_day = int(task_day) - 1 if int(task_day) > 1 else max_days

        # Recurring + how_often, how_long, repetitions adjustments
        if how_often_up_button.collidepoint(event.pos):
            new_val = task_how_often + 1
            task_how_often = max(1, new_val)
            total_days = (task_repetitions_amount - 1) * task_how_often + 1
            task_how_long = max(1, math.ceil(total_days / 7))

        elif how_often_down_button.collidepoint(event.pos):
            new_val = task_how_often - 1
            if new_val >= 1:
                task_how_often = new_val
                total_days = (task_repetitions_amount - 1) * task_how_often + 1
                task_how_long = max(1, math.ceil(total_days / 7))

        elif how_long_up_button.collidepoint(event.pos):
            task_how_long = task_how_long + 1
            total_days = task_how_long * 7
            new_reps = math.floor((total_days - 1) / task_how_often) + 1
            task_repetitions_amount = min(26, max(1, new_reps))

        elif how_long_down_button.collidepoint(event.pos):
            if task_how_long > 1:
                task_how_long -= 1
                total_days = task_how_long * 7
                new_reps = math.floor((total_days - 1) / task_how_often) + 1
                task_repetitions_amount = min(26, max(1, new_reps))

        elif repetitions_amount_up_button.collidepoint(event.pos):
            if task_repetitions_amount < 26:
                task_repetitions_amount += 1
                total_days = (task_repetitions_amount - 1) * task_how_often + 1
                task_how_long = max(1, math.ceil(total_days / 7))

        elif repetitions_amount_down_button.collidepoint(event.pos):
            if task_repetitions_amount > 1:
                task_repetitions_amount -= 1
                total_days = (task_repetitions_amount - 1) * task_how_often + 1
                task_how_long = max(1, math.ceil(total_days / 7))

        # Done button: create task(s)
        elif done_button.collidepoint(event.pos):
            if current_task and current_spoons:
                task_date = datetime(current_time.year, task_month, int(task_day))
                days_till_due = (task_date - current_time).days + 1

                if recurring_toggle_on:
                    for i in range(task_repetitions_amount):
                        actual_date = task_date + timedelta(days=i * task_how_often)
                        days_left = (actual_date - current_time).days + 1
                        entry = [
                            current_task,
                            current_spoons,
                            "❌",
                            days_left,
                            actual_date,
                            # no time fields
                            [0,0,0,0],
                            [0,0,0,0]
                        ]
                        if folder == "homework":
                            homework_tasks_list.append(entry)
                        elif folder == "chores":
                            chores_tasks_list.append(entry)
                        elif folder == "work":
                            work_tasks_list.append(entry)
                        elif folder == "misc":
                            misc_tasks_list.append(entry)
                        elif folder == "exams":
                            exams_tasks_list.append(entry)
                        elif folder == "projects":
                            projects_tasks_list.append(entry)
                else:
                    entry = [
                        current_task,
                        current_spoons,
                        "❌",
                        days_till_due,
                        task_date,
                        [0,0,0,0],
                        [0,0,0,0]
                    ]
                    if folder == "homework":
                        homework_tasks_list.append(entry)
                    elif folder == "chores":
                        chores_tasks_list.append(entry)
                    elif folder == "work":
                        work_tasks_list.append(entry)
                    elif folder == "misc":
                        misc_tasks_list.append(entry)
                    elif folder == "exams":
                        exams_tasks_list.append(entry)
                    elif folder == "projects":
                        projects_tasks_list.append(entry)
                        

                # reset inputs
                current_task = ""
                current_spoons = 0
                input_active = False

        # Folder selection
        for f_key, rect in reversed(ctf_mod.folder_rects):
            if rect.collidepoint(event.pos):
                folder = f_key
                break

    # Keyboard handling
    if event.type == pygame.KEYDOWN:
        if input_active == "task":
            if event.key == pygame.K_RETURN:
                input_active = "spoons"
            elif event.key == pygame.K_BACKSPACE:
                current_task = current_task[:-1]
            else:
                current_task += event.unicode

        elif input_active == "spoons":
            if event.key == pygame.K_BACKSPACE:
                current_spoons //= 10
            elif event.unicode.isdigit():
                current_spoons = current_spoons * 10 + int(event.unicode)

    return (input_active,page,folder,recurring_toggle_on,current_task,current_spoons,task_month,task_day,homework_tasks_list,chores_tasks_list,work_tasks_list,misc_tasks_list,exams_tasks_list,projects_tasks_list,task_how_often,task_how_long,task_repetitions_amount)