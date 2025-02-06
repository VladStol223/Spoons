from config import *

from drawing_functions.draw_rounded_button import draw_rounded_button
from drawing_functions.draw_input_box import draw_input_box
from drawing_functions.draw_complete_tasks_folders import draw_complete_tasks_folders
from drawing_functions.draw_spoons import draw_spoons

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

def draw_input_tasks(screen, spoons, current_task, current_spoons, input_active, 
                         folder, task_month, task_day, time_toggle_on, recurring_toggle_on,  start_time, end_time,
                         done_button_color, add_tasks_choose_folder_color, add_tasks_chosen_folder_color, icon_image, spoon_name_input,
                         task_how_often, task_how_long, task_repetitions_amount,
                         folder_one, folder_two, folder_three, folder_four, folder_five, folder_six):
    global hub_buttons_showing
    
    # Draw hub and existing UI elements
    draw_rounded_button(screen, hub_toggle, LIGHT_GRAY, BLACK, 0, 2)# type: ignore
    pygame.draw.rect(screen, BLACK, hub_menu1)# type: ignore
    pygame.draw.rect(screen, BLACK, hub_menu2)# type: ignore
    pygame.draw.rect(screen, BLACK, hub_menu3)# type: ignore
    
    draw_complete_tasks_folders(screen, folder, add_tasks_chosen_folder_color, add_tasks_choose_folder_color,
                                folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)
    draw_spoons(screen, spoons, icon_image, spoon_name_input)
    draw_input_box(screen, task_input_box, input_active == "task", current_task, GREEN, LIGHT_GRAY)# type: ignore
    draw_input_box(screen, spoon_input_box, input_active == "spoons", str(current_spoons), GREEN, LIGHT_GRAY)# type: ignore

    up_arrow = font.render(">", True, BLACK)# type: ignore
    down_arrow = font.render("<", True, BLACK)# type: ignore

    # Display the time toggle button
    draw_rounded_button(screen, time_toggle_button, RED if not time_toggle_on else GREEN, BLACK, 15)# type: ignore

    #Display the recurring tasks button
    draw_rounded_button(screen, recurring_toggle_button, RED if not recurring_toggle_on else GREEN, BLACK, 15)# type: ignore

    # Check toggle state and draw respective UI elements
    if time_toggle_on:
        # Draw the time input fields
        screen.blit(font.render("Enter due date:", True, BLACK), (200, 270))# type: ignore
        draw_input_box(screen, month_input_box_time_shifted, input_active == "month", str(months[task_month - 1]), GREEN, LIGHT_GRAY)# type: ignore
        draw_input_box(screen, day_input_box_time_shifted, input_active == "day", task_day, GREEN, LIGHT_GRAY)# type: ignore
        
        # Draw time input fields for start and end time
        time_of_day_label = font.render("Enter time of day:", True, BLACK)# type: ignore
        screen.blit(time_of_day_label, (420, 270))
        # Format the time as HH:MM for display
        start_time_display = f"{start_time[0]}{start_time[1]}:{start_time[2]}{start_time[3]}"
        end_time_display = f"{end_time[0]}{end_time[1]}:{end_time[2]}{end_time[3]}"


        # Draw start and end time input boxes with formatted time
        draw_input_box(screen, start_time_input_box, input_active == "start_time", start_time_display, GREEN, LIGHT_GRAY)# type: ignore
        draw_input_box(screen, end_time_input_box, input_active == "end_time", end_time_display, GREEN, LIGHT_GRAY)# type: ignore
        
        pygame.draw.rect(screen, done_button_color, month_up_button_time_shifted)
        pygame.draw.rect(screen, done_button_color, month_down_button_time_shifted)
        pygame.draw.rect(screen, done_button_color, day_up_button_time_shifted)
        pygame.draw.rect(screen, done_button_color, day_down_button_time_shifted)
        screen.blit(up_arrow, (330, 303))
        screen.blit(down_arrow, (330, 328))
        screen.blit(up_arrow, (415, 303))
        screen.blit(down_arrow, (415, 328))

        # Arrow between start and end time
        screen.blit(font.render("->", True, BLACK), (start_time_input_box.x + 85, start_time_input_box.y + 8))# type: ignore
        time_toggle_label = small_font.render("Remove Time of Day", True, BLACK)# type: ignore
        screen.blit(time_toggle_label, (hub_toggle.x + hub_toggle.width + 10, hub_toggle.y + hub_toggle.height + 20))
        time_toggle_label = small_font.render("Add Recurring Task", True, BLACK)# type: ignore
        screen.blit(time_toggle_label, (hub_toggle.x + hub_toggle.width + 520, hub_toggle.y + hub_toggle.height + 20))
                    
    elif recurring_toggle_on:
        # Draw the recurring task input fields
        screen.blit(font.render("Enter Start date:", True, BLACK), (170, 270))# type: ignore
        draw_input_box(screen, month_input_box_recurring_shifted, input_active == "none", str(months[task_month - 1]), GREEN, LIGHT_GRAY)# type: ignore
        draw_input_box(screen, day_input_box_recurring_shifted, input_active == "none", task_day, GREEN, LIGHT_GRAY)# type: ignore

        pygame.draw.rect(screen, done_button_color, month_up_button_recurring_shifted)
        pygame.draw.rect(screen, done_button_color, month_down_button_recurring_shifted)
        pygame.draw.rect(screen, done_button_color, day_up_button_recurring_shifted)
        pygame.draw.rect(screen, done_button_color, day_down_button_recurring_shifted)
        screen.blit(up_arrow, (month_up_button_recurring_shifted.x, month_up_button_recurring_shifted.y - 7))
        screen.blit(down_arrow, (month_down_button_recurring_shifted.x, month_down_button_recurring_shifted.y - 7))
        screen.blit(up_arrow, (day_up_button_recurring_shifted.x, day_up_button_recurring_shifted.y - 7))
        screen.blit(down_arrow, (day_down_button_recurring_shifted.x, day_down_button_recurring_shifted.y - 7))

        how_often_label = font.render("How Often:", True, BLACK)# type: ignore
        screen.blit(how_often_label, (395, 270))
        draw_input_box(screen, how_often_input_box, input_active == "none", f"{task_how_often} days", GREEN, LIGHT_GRAY)# type: ignore
        pygame.draw.rect(screen, done_button_color, how_often_up_button)
        pygame.draw.rect(screen, done_button_color, how_often_down_button)
        screen.blit(up_arrow, (how_often_up_button.x, how_often_up_button.y - 7))
        screen.blit(down_arrow, (how_often_down_button.x, how_often_down_button.y - 7))

        how_long_label = small_font.render("How Long:", True, BLACK)# type: ignore
        screen.blit(how_long_label, (560, 263))
        draw_input_box(screen, how_long_input_box, "small_font", f"{task_how_long} weeks", GREEN, LIGHT_GRAY)# type: ignore
        pygame.draw.rect(screen, done_button_color, how_long_up_button)
        pygame.draw.rect(screen, done_button_color, how_long_down_button)
        screen.blit(up_arrow, (how_long_up_button.x, how_long_up_button.y - 7))
        screen.blit(down_arrow, (how_long_down_button.x, how_long_down_button.y - 7))

        repetitions_amount_label = small_font.render("Repetitions:", True, BLACK)# type: ignore
        screen.blit(repetitions_amount_label, (552, 325))
        draw_input_box(screen, repetitions_amount_input_box, "small_font", f"{task_repetitions_amount} times", GREEN, LIGHT_GRAY)# type: ignore
        pygame.draw.rect(screen, done_button_color, repetitions_amount_up_button)
        pygame.draw.rect(screen, done_button_color, repetitions_amount_down_button)
        screen.blit(up_arrow, (repetitions_amount_up_button.x, repetitions_amount_up_button.y - 7))
        screen.blit(down_arrow, (repetitions_amount_down_button.x, repetitions_amount_down_button.y - 7))


        time_toggle_label = small_font.render("Remove Recurring Task", True, BLACK)# type: ignore
        screen.blit(time_toggle_label, (hub_toggle.x + hub_toggle.width + 480, hub_toggle.y + hub_toggle.height + 20))
        time_toggle_label = small_font.render("Add Time of Day", True, BLACK)# type: ignore
        screen.blit(time_toggle_label, (hub_toggle.x + hub_toggle.width + 10, hub_toggle.y + hub_toggle.height + 20))

    else:
        # Draw the normal due date prompt and input boxes
        screen.blit(font.render("Enter due date:", True, BLACK), (305, 270))# type: ignore
        draw_input_box(screen, month_input_box_normal, input_active == "month", str(months[task_month - 1]), GREEN, LIGHT_GRAY)# type: ignore
        draw_input_box(screen, day_input_box_normal, input_active == "day", task_day, GREEN, LIGHT_GRAY)# type: ignore
        pygame.draw.rect(screen, done_button_color, month_up_button_normal)
        pygame.draw.rect(screen, done_button_color, month_down_button_normal)
        pygame.draw.rect(screen, done_button_color, day_up_button_normal)
        pygame.draw.rect(screen, done_button_color, day_down_button_normal)
        screen.blit(up_arrow, (420, 303))
        screen.blit(down_arrow, (420, 328))
        screen.blit(up_arrow, (515, 303))
        screen.blit(down_arrow, (515, 328))
        time_toggle_label = small_font.render("Add Time of Day", True, BLACK)# type: ignore
        screen.blit(time_toggle_label, (hub_toggle.x + hub_toggle.width + 10, hub_toggle.y + hub_toggle.height + 20))
        time_toggle_label = small_font.render("Add Recurring Task", True, BLACK)# type: ignore
        screen.blit(time_toggle_label, (hub_toggle.x + hub_toggle.width + 520, hub_toggle.y + hub_toggle.height + 20))

    # Display other task input prompts
    screen.blit(font.render("Enter task name:", True, BLACK), (300, 155))# type: ignore
    screen.blit(font.render("Enter spoons needed:", True, BLACK), (280, 380))# type: ignore
    draw_rounded_button(screen, done_button, done_button_color, BLACK, 15)# type: ignore
    screen.blit(font.render("Done", True, WHITE), (done_button.x + 69, done_button.y + 12))# type: ignore

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

def logic_input_tasks(event, current_task, current_spoons, folder, task_month, task_day,
                      task_how_often, task_how_long, task_repetitions_amount,
                      time_toggle_on, recurring_toggle_on, start_time, end_time,
                      max_days, input_active,
                      homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list):
    page = "input_tasks"

    if event.type == pygame.MOUSEBUTTONDOWN:
        # Toggle time entry
        if time_toggle_button.collidepoint(event.pos):
            recurring_toggle_on = False
            time_toggle_on = not time_toggle_on

        # Toggle recurring task entry
        if recurring_toggle_button.collidepoint(event.pos):
            time_toggle_on = False
            recurring_toggle_on = not recurring_toggle_on

        # Task input boxes
        if task_input_box.collidepoint(event.pos):
            input_active = "task"
        elif spoon_input_box.collidepoint(event.pos):
            input_active = "spoons"

        # Month/Day adjustments
        if time_toggle_on:
            # Using the shifted rects for time toggle
            if month_up_button_time_shifted.collidepoint(event.pos):
                task_month = task_month + 1 if task_month < 12 else 1
            elif month_down_button_time_shifted.collidepoint(event.pos):
                task_month = task_month - 1 if task_month > 1 else 12
            elif day_up_button_time_shifted.collidepoint(event.pos):
                task_day = int(task_day) + 1 if int(task_day) < max_days else 1
            elif day_down_button_time_shifted.collidepoint(event.pos):
                task_day = int(task_day) - 1 if int(task_day) > 1 else max_days
        elif recurring_toggle_on:
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
            # Normal (no time, no recurring)
            if month_up_button_normal.collidepoint(event.pos):
                task_month = task_month + 1 if task_month < 12 else 1
            elif month_down_button_normal.collidepoint(event.pos):
                task_month = task_month - 1 if task_month > 1 else 12
            elif day_up_button_normal.collidepoint(event.pos):
                task_day = int(task_day) + 1 if int(task_day) < max_days else 1
            elif day_down_button_normal.collidepoint(event.pos):
                task_day = int(task_day) - 1 if int(task_day) > 1 else max_days

        # If the user clicks the start/end time boxes
        if start_time_input_box.collidepoint(event.pos):
            input_active = "start_time"
        elif end_time_input_box.collidepoint(event.pos):
            input_active = "end_time"

        # Recurring + how_often, how_long, repetitions
        # -----------------------------------------------------
        if how_often_up_button.collidepoint(event.pos):
            new_val = task_how_often + 1
            # clamp at min=1
            if new_val < 1:
                new_val = 1
            task_how_often = new_val

            # Recalculate how_long from how_often & repetitions
            total_days = (task_repetitions_amount - 1) * task_how_often + 1
            new_weeks = math.ceil(total_days / 7)
            if new_weeks < 1:
                new_weeks = 1
            task_how_long = new_weeks

        elif how_often_down_button.collidepoint(event.pos):
            new_val = task_how_often - 1
            if new_val < 1:
                # do nothing if it would go below 1
                pass
            else:
                task_how_often = new_val
                # Recalculate how_long
                total_days = (task_repetitions_amount - 1) * task_how_often + 1
                new_weeks = math.ceil(total_days / 7)
                if new_weeks < 1:
                    new_weeks = 1
                task_how_long = new_weeks

        elif how_long_up_button.collidepoint(event.pos):
            new_val = task_how_long + 1
            if new_val < 1:
                new_val = 1
            task_how_long = new_val

            # Now recalc repetitions from how_long & how_often
            total_days = task_how_long * 7
            # formula: new_repetitions = floor((total_days - 1) / how_often) + 1
            new_reps = math.floor((total_days - 1) / task_how_often) + 1
            if new_reps < 1:
                new_reps = 1
            if new_reps > 26:
                new_reps = 26
            task_repetitions_amount = new_reps

        elif how_long_down_button.collidepoint(event.pos):
            new_val = task_how_long - 1
            if new_val < 1:
                # do nothing if it would go below 1
                pass
            else:
                task_how_long = new_val
                total_days = task_how_long * 7
                new_reps = math.floor((total_days - 1) / task_how_often) + 1
                if new_reps < 1:
                    new_reps = 1
                if new_reps > 26:
                    new_reps = 26
                task_repetitions_amount = new_reps

        elif repetitions_amount_up_button.collidepoint(event.pos):
            new_val = task_repetitions_amount + 1
            if new_val > 26:
                # do nothing if it would exceed 26
                pass
            else:
                task_repetitions_amount = new_val
                # Recalc how_long from how_often & new reps
                total_days = (task_repetitions_amount - 1) * task_how_often + 1
                new_weeks = math.ceil(total_days / 7)
                if new_weeks < 1:
                    new_weeks = 1
                task_how_long = new_weeks

        elif repetitions_amount_down_button.collidepoint(event.pos):
            new_val = task_repetitions_amount - 1
            if new_val < 1:
                # do nothing if it would go below 1
                pass
            else:
                task_repetitions_amount = new_val
                total_days = (task_repetitions_amount - 1) * task_how_often + 1
                new_weeks = math.ceil(total_days / 7)
                if new_weeks < 1:
                    new_weeks = 1
                task_how_long = new_weeks
        # -----------------------------------------------------

        elif done_button.collidepoint(event.pos):
            # If the user actually typed a task name & spoons
            if current_task and current_spoons:
                task_date = datetime(current_time.year, int(task_month), int(task_day))
                days_till_due_date = (task_date - current_time).days

                if recurring_toggle_on:
                    # Create multiple tasks, one for each repetition
                    # day 0, day how_often, etc...
                    for i in range(task_repetitions_amount):
                        offset_days = i * task_how_often
                        actual_date = task_date + timedelta(days=offset_days)
                        actual_days_till_due = (actual_date - current_time).days
                        
                        task_entry = [
                            current_task, 
                            current_spoons, 
                            "❌", 
                            actual_days_till_due + 1,  # or however your code handles “days left”
                            actual_date
                        ]
                        # If you wanted to forbid time toggle with recurring, you can add the same approach:
                        task_entry.extend([[0,0,0,0],[0,0,0,0]])  # no time
                        
                        # Append to the correct folder
                        if folder == "homework":
                            homework_tasks_list.append(task_entry)
                        elif folder == "chores":
                            chores_tasks_list.append(task_entry)
                        elif folder == "work":
                            work_tasks_list.append(task_entry)
                        elif folder == "misc":
                            misc_tasks_list.append(task_entry)
                else:
                    # Normal single-task approach
                    task_entry = [
                        current_task, current_spoons, "❌", days_till_due_date+1, task_date
                    ]
                    if time_toggle_on:
                        task_entry.extend([start_time, end_time])
                    else:
                        task_entry.extend([[0,0,0,0],[0,0,0,0]])
                    
                    if folder == "homework":
                        homework_tasks_list.append(task_entry)
                    elif folder == "chores":
                        chores_tasks_list.append(task_entry)
                    elif folder == "work":
                        work_tasks_list.append(task_entry)
                    elif folder == "misc":
                        misc_tasks_list.append(task_entry)

                # Reset after appending
                current_task = ""
                current_spoons = 0
                input_active = False
            else:
                page = "complete_tasks"

        # Folder selection
        if homework_tasks.collidepoint(event.pos):
            folder = "homework"
        elif chores_tasks.collidepoint(event.pos):
            folder = "chores"
        elif work_tasks.collidepoint(event.pos):
            folder = "work"
        elif misc_tasks.collidepoint(event.pos):
            folder = "misc"

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
                current_spoons = current_spoons // 10
            else:
                try:
                    current_spoons = current_spoons * 10 + int(event.unicode)
                except ValueError:
                    pass

        elif input_active in ["start_time", "end_time"]:
            # Adjust the time digits
            time_component = start_time if input_active == "start_time" else end_time
            if event.key == pygame.K_BACKSPACE:
                time_component = [0] + time_component[:3]
            elif event.unicode.isdigit():
                time_component = time_component[1:] + [int(event.unicode)]
            # Update the correct variable
            if input_active == "start_time":
                start_time = time_component
            else:
                end_time = time_component

    # Return all updated state
    return (
        input_active, page, folder,
        time_toggle_on, recurring_toggle_on,
        current_task, current_spoons,
        task_month, task_day,
        start_time, end_time,
        homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list,
        task_how_often, task_how_long, task_repetitions_amount
    )
