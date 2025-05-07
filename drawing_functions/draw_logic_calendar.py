from config import *
from datetime import datetime
import calendar

from drawing_functions.draw_rounded_button import draw_rounded_button

import pygame

"""
Summary:
    Draws a calendar on the given screen with tasks and their respective colors for a specified month and year.

Parameters:
    screen (pygame.Surface): The surface on which the calendar will be drawn.
    homework_tasks_list (list): List of homework tasks.
    chores_tasks_list (list): List of chores tasks.
    work_tasks_list (list): List of work tasks.
    misc_tasks_list (list): List of miscellaneous tasks.
    displayed_month (int): The month to be displayed on the calendar.
    displayed_year (int): The year to be displayed on the calendar.
    homework_fol_color (tuple): Color for homework tasks.
    chores_fol_color (tuple): Color for chores tasks.
    work_fol_color (tuple): Color for work tasks.
    misc_fol_color (tuple): Color for miscellaneous tasks.
    calendar_month_color (tuple): Color for the calendar month header.
    calendar_previous_day_header_color (tuple): Color for the previous day's header.
    calendar_next_day_header_color (tuple): Color for the next day's header.
    calendar_current_day_header_color (tuple): Color for the current day's header.
    calendar_previous_day_color (tuple): Color for the previous day's box.
    calendar_current_day_color (tuple): Color for the current day's box.
    calendar_next_day_color (tuple): Color for the next day's box.

Returns:
    No returns.
"""

def draw_calendar(screen, spoon_name_input,
                  homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list,
                  displayed_month, displayed_year,
                  homework_fol_color, chores_fol_color, work_fol_color, misc_fol_color,calendar_month_color, 
                  calendar_previous_day_header_color, calendar_next_day_header_color, calendar_current_day_header_color,
                  calendar_previous_day_color, calendar_current_day_color, calendar_next_day_color,
                  folder_one, folder_two, folder_three, folder_four, folder_five, folder_six,
                  streak_dates):
    global hub_buttons_showing

    draw_rounded_button(screen, hub_toggle, LIGHT_GRAY, BLACK, 0, 2)# type: ignore
    pygame.draw.rect(screen, BLACK, hub_menu1)# type: ignore
    pygame.draw.rect(screen, BLACK, hub_menu2)# type: ignore
    pygame.draw.rect(screen, BLACK, hub_menu3)# type: ignore

    # Define the dimensions and spacing
    day_box_width = 100
    start_x = 50  # Start position for the calendar grid
    start_y = 100  # Start position for the calendar grid
    margin = 0
    top_padding = 30  # Padding from the top for day names
    days_of_week = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    today_date = datetime.now()

    def is_streak_day(date_to_check_str):
        for start_str, end_str in streak_dates:
            if start_str <= date_to_check_str <= end_str:
                return True
        return False


    task_colors = {
        "homework": homework_fol_color,
        "chores": chores_fol_color,
        "work": work_fol_color,
        "misc": misc_fol_color
    }
    task_lists = {
        "homework": homework_tasks_list,
        "chores": chores_tasks_list,
        "work": work_tasks_list,
        "misc": misc_tasks_list
    }  

    # Get the mouse position
    mouse_pos = pygame.mouse.get_pos()
    hovered_task_folder = None
    hovered_task_folder_info = None

    # Get the first weekday of the displayed month and the number of days in the month
    first_weekday, number_of_days = calendar.monthrange(displayed_year, displayed_month)
    first_weekday = (first_weekday + 1) % 7

    # Determine if the month requires 6 rows
    total_days = first_weekday + number_of_days
    day_box_height = 80 if total_days > 35 else 95
    folder_box_height = 12 if total_days > 35 else 16

    # Draw the month name at the top
    month_text = big_font.render(calendar.month_name[displayed_month] + ' ' + str(displayed_year), True, BLACK)# type: ignore
    screen.blit(month_text, (570, 25))
    draw_rounded_button(screen, previous_month_button, calendar_month_color, BLACK, 2)# type: ignore
    draw_rounded_button(screen, next_month_button, calendar_month_color, BLACK, 2)# type: ignore
    month_button_text = big_font.render("<   >", True, BLACK)# type: ignore
    screen.blit(month_button_text, (505, 23))

    # Draw the day names
    for i, day_name in enumerate(days_of_week):
        day_text = font.render(day_name, True, BLACK)# type: ignore
        screen.blit(day_text, (start_x + i * (day_box_width + margin) + 25, start_y - top_padding))

    # Draw the calendar boxes
    day_number = 1
    for row in range(6):  # Maximum of 6 rows in a month
        for col in range(7):  # 7 columns for the days of the week
            # Only draw the day number if it's within the current month
            if row == 0 and col < first_weekday:  # Skip the empty days before the 1st of the month
                continue
            if day_number > number_of_days:  # Stop if we've drawn all days in the month
                break

            # Determine the x and y position for the current box
            x = start_x + col * (day_box_width + margin)
            y = start_y + row * (day_box_height + margin)
            checked_date = datetime(displayed_year, displayed_month, day_number)

            # Draw day boxes for previous, current, and future days
            if checked_date < today_date:
                pygame.draw.rect(screen, calendar_previous_day_header_color, (x, y, day_box_width, day_box_height))
                pygame.draw.rect(screen, BLACK, (x, y, day_box_width, day_box_height), 2)# type: ignore
                if total_days > 35:
                    pygame.draw.rect(screen, calendar_previous_day_color, (x, y + 14, day_box_width, day_box_height - 14))
                    pygame.draw.rect(screen, BLACK, (x, y + 14, day_box_width, day_box_height - 14), 2)# type: ignore
                else:
                    pygame.draw.rect(screen, calendar_previous_day_color, (x, y + 16, day_box_width, day_box_height - 16))
                    pygame.draw.rect(screen, BLACK, (x, y + 16, day_box_width, day_box_height - 16), 2)# type: ignore
            elif checked_date > today_date:
                pygame.draw.rect(screen, calendar_next_day_header_color, (x, y, day_box_width, day_box_height))
                pygame.draw.rect(screen, BLACK, (x, y, day_box_width, day_box_height), 2)# type: ignore
                if total_days > 35:
                    pygame.draw.rect(screen, calendar_next_day_color, (x, y + 14, day_box_width, day_box_height - 14))
                    pygame.draw.rect(screen, BLACK, (x, y + 14, day_box_width, day_box_height - 14), 2)# type: ignore
                else:
                    pygame.draw.rect(screen, calendar_next_day_color, (x, y + 16, day_box_width, day_box_height - 16))
                    pygame.draw.rect(screen, BLACK, (x, y + 16, day_box_width, day_box_height - 16), 2)# type: ignore
            if (displayed_month == datetime.now().month and displayed_year == datetime.now().year and day_number == today_date.day):
                pygame.draw.rect(screen, calendar_current_day_header_color, (x, y, day_box_width, day_box_height))
                pygame.draw.rect(screen, BLACK, (x, y, day_box_width, day_box_height), 2)# type: ignore
                if total_days > 35:
                    pygame.draw.rect(screen, calendar_current_day_color, (x, y + 14, day_box_width, day_box_height - 14))
                    pygame.draw.rect(screen, BLACK, (x, y + 14, day_box_width, day_box_height - 14), 2)# type: ignore
                else:
                    pygame.draw.rect(screen, calendar_current_day_color, (x, y + 16, day_box_width, day_box_height - 16))
                    pygame.draw.rect(screen, BLACK, (x, y + 16, day_box_width, day_box_height - 16), 2)# type: ignore

            # Draw the day number in the top right of the box
            day_text = smaller_font.render(str(day_number), True, BLACK)# type: ignore
            checked_date_str = checked_date.strftime("%Y-%m-%d")
            if is_streak_day(checked_date_str):
                s_text = smaller_font.render("S", True, BLACK)# type: ignore
                screen.blit(s_text, (x + day_box_width - 33, y + 2))  # S appears left of the day number

            if day_number > 9:
                screen.blit(day_text, (x + day_box_width - 19, y + 2))
            else:
                screen.blit(day_text, (x + day_box_width - 11, y + 2))

            # Check for tasks on this day and draw folder boxes
            task_y_offset = y + 20  # Starting y-offset for the folder boxes

            for task_type, task_list in task_lists.items():
                # Filter tasks due on this date
                tasks_for_date = [task for task in task_list if task[4] == checked_date]
                task_count = len(tasks_for_date)

                if task_count > 0:
                    # Define folder box rect
                    folder_box_rect = pygame.Rect(x + 5, task_y_offset, day_box_width - 15, folder_box_height)
                    draw_rounded_button(screen, folder_box_rect, task_colors[task_type], BLACK, 1, 1)# type: ignore

                    # Check if all tasks are completed
                    all_completed = all(task[2] == "✅" for task in tasks_for_date)

                    # Check if mouse is hovering over this folder box
                    if folder_box_rect.collidepoint(mouse_pos):
                        hovered_task_folder = task_type
                        hovered_task_folder_info = {
                            "folder_name": task_type,
                            "task_count": task_count,
                            "task_details": tasks_for_date,
                            "hover_position": (x, y),
                            "column": col
                        }

                    # Draw the task count text with strike-through if all completed
                    if task_type == "homework":
                        task_text = smaller_font.render(f"{task_count} {folder_one}" if task_count == 1 else f"{task_count} {folder_one}s", True, BLACK)# type: ignore
                    elif task_type == "chores":
                        task_text = smaller_font.render(f"{task_count} {folder_two}" if task_count == 1 else f"{task_count} {folder_two}s", True, BLACK)# type: ignore
                    elif task_type == "work":
                        task_text = smaller_font.render(f"{task_count} {folder_three}" if task_count == 1 else f"{task_count} {folder_three}s", True, BLACK)# type: ignore
                    elif task_type == "misc":
                        task_text = smaller_font.render(f"{task_count} {folder_four}" if task_count == 1 else f"{task_count} {folder_four}s", True, BLACK)# type: ignore
                    screen.blit(task_text, (x + 10, task_y_offset + 1))
                    if all_completed:
                        pygame.draw.line(screen, BLACK, (x + 10, task_y_offset + 10), (x + 50, task_y_offset + 5), 2)# type: ignore

                    # Move down for the next folder box
                    task_y_offset += folder_box_height + 2

            # Move to the next day
            day_number += 1

        # Stop if we've drawn all days in the month
        if day_number > number_of_days:
            break

    # Draw the hover box with task details if hovering over a folder
    if hovered_task_folder_info:
        hover_x, hover_y = hovered_task_folder_info['hover_position']
        if hovered_task_folder_info["column"] <= 3:
            hover_rect = pygame.Rect(hover_x + day_box_width, hover_y, day_box_width * 3, day_box_height)
        else:
            hover_rect = pygame.Rect(hover_x - (day_box_width * 3), hover_y, day_box_width * 3, day_box_height)

        pygame.draw.rect(screen, calendar_current_day_color, hover_rect)
        pygame.draw.rect(screen, BLACK, hover_rect, 2)# type: ignore

        # Display folder name and task details with strike-through if completed
        hover_text_y = hover_y - 5
        if hovered_task_folder_info["folder_name"] == "homework":
            folder_name_text = font.render(folder_one, True, BLACK)# type: ignore
        elif hovered_task_folder_info["folder_name"] == "chores":
            folder_name_text = font.render(folder_two, True, BLACK)# type: ignore
        elif hovered_task_folder_info["folder_name"] == "work":
            folder_name_text = font.render(folder_three, True, BLACK)# type: ignore
        elif hovered_task_folder_info["folder_name"] == "misc":
            folder_name_text = font.render(folder_four, True, BLACK)# type: ignore
        screen.blit(folder_name_text, (hover_rect.x + 5, hover_text_y + 8))
        underline = pygame.Rect(hover_rect.x + 5, hover_text_y + 30, 100, 3)
        draw_rounded_button(screen, underline, BLACK, 1, 0)# type: ignore

        hover_text_y += 20
        for task in hovered_task_folder_info["task_details"]:
            task_name_text = smaller_font.render(f"{task[1]} {spoon_name_input} for {task[0]}", True, BLACK)# type: ignore
            screen.blit(task_name_text, (hover_rect.x + 5, hover_text_y + 15))
            
            # Calculate the width of the text for the strike-through line
            text_width = task_name_text.get_width()
            
            if task[2] == "✅":  # If the task is marked as completed
                pygame.draw.line(screen, BLACK, (hover_rect.x + 5, hover_text_y + 23), (hover_rect.x + 5 + text_width, hover_text_y + 18), 2)# type: ignore
            hover_text_y += 15

"""
Summary:
    Handles the logic for navigating the calendar by changing the displayed month and year based on user input.

Parameters:
    event (pygame.event.Event): The event object containing information about the user input.
    displayed_month (int): The currently displayed month on the calendar.
    displayed_year (int): The currently displayed year on the calendar.

Returns:
    (tuple) Updated values for: displayed month and year.
"""

def logic_calendar(event, displayed_month, displayed_year):
    if event.type == pygame.MOUSEBUTTONDOWN:
        if previous_month_button.collidepoint(event.pos):
            displayed_month -= 1
            if displayed_month < 1:
                displayed_month = 12
                displayed_year -= 1
        elif next_month_button.collidepoint(event.pos):
            displayed_month += 1
            if displayed_month > 12:
                displayed_month = 1
                displayed_year += 1
    return displayed_month, displayed_year