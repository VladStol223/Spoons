#Vladislav Stolbennikov
#8/7/2024
#Spoons App

'''
Total pages:
1.) Add Spoons
2.) Add Tasks
3.) Complete Tasks
4.) Remove Tasks
5.) Calendar
6.) daily schedule
7.) Settings

To do:
 - fix the date not changing after midnight
 - remove dropwndows for colors in settings.
 - move all functions from main to their own files
 - Add a "today's schedule" page, where you can see all of the tasks you set for that day, in a specific time. When you don't have any tasks set for that day but you want to get ahead, 
    the daily schedule should auto-populate with the the tasks that have the closest due date.
 - themes should have names
 - icon name and spoons amount should move where the spoons icon is 
'''
from os import system, name
from datetime import datetime
from datetime import timedelta

from config import *
from colors import COLORS
for name, value in COLORS.items():
    globals()[name] = value
from switch_themes import switch_theme
from themes import DROPDOWN_LISTS

import pygame
import sys
import calendar
import json

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Spoons")

spoons = 0
current_task = ""
current_spoons = 0
homework_tasks_list = []
chores_tasks_list = []
work_tasks_list = []
misc_tasks_list = []
task_buttons_homework = []
task_buttons_chores = []
task_buttons_work = []
task_buttons_misc = []
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
tool_tips = True
icon_image = spoon_image
spoon_name = "Spoons"
page = "input_spoons"
folder = "misc"
running = True
time_toggle_on = False
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

####################################################################################################################################

def hub_buttons_show():
    global hub_buttons_showing
    # Display hub buttons if toggle is on
    if hub_toggle.collidepoint(mouse_pos):
        hub_buttons_showing = True
        draw_hub_buttons(screen, page, tool_tips, background_color, add_spoons_color, add_tasks_color, complete_tasks_color, remove_tasks_color, daily_schedule_color, calendar_color, settings_color)
    if hub_buttons_showing:
        draw_hub_buttons(screen, page, tool_tips, background_color, add_spoons_color, add_tasks_color, complete_tasks_color, remove_tasks_color, daily_schedule_color, calendar_color, settings_color)
    if not hub_toggle.collidepoint(mouse_pos) and not hub_cover.collidepoint(mouse_pos):
        hub_buttons_showing = False
from drawing_functions.draw_hub_buttons import draw_hub_buttons
from drawing_functions.draw_input_spoons import draw_input_spoons, logic_input_spoons
from drawing_functions.draw_input_tasks import draw_input_tasks
from drawing_functions.draw_complete_tasks_hub import draw_complete_tasks_hub
from drawing_functions.draw_complete_tasks import draw_complete_tasks
from drawing_functions.draw_remove_tasks import draw_remove_tasks
from drawing_functions.draw_remove_tasks_hub import draw_remove_tasks_hub
from drawing_functions.draw_daily_schedule import draw_daily_schedule
from drawing_functions.draw_calendar import draw_calendar, logic_calendar
from drawing_functions.draw_settings import draw_settings

def handle_scroll(event):
    global scroll_offset, scroll_multiplier, scroll_limit
    scroll_multiplier = 1
    scroll_limit = 20
    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 4:  # Scroll up
            scroll_offset = max(scroll_offset - (1 * scroll_multiplier), 0)  # Adjust and limit the scroll offset
        elif event.button == 5:  # Scroll down
            scroll_offset = min(scroll_offset + (1 * scroll_multiplier), scroll_limit)  # Adjust and cap for 24 hours

def get_available_time_blocks(class_schedule, start_hour=6, end_hour=24,
                              monday_task_start_time=(7, 0), tuesday_task_start_time=(7, 0),
                              wednesday_task_start_time=(7, 0), thursday_task_start_time=(7, 0),
                              friday_task_start_time=(7, 0), saturday_task_start_time=(9, 0),
                              sunday_task_start_time=(9, 0)):
    """
    Identify available time blocks for scheduling tasks over the next 30 days.
    Also gathers tasks with pre-assigned start and end times into `task_schedule`.
    Each weekday can have a customized task start time.
    """
    dates = [datetime.today().date() + timedelta(days=i) for i in range(30)]
    available_blocks_by_date = {}
    task_schedule = {}

    # Define start times for each day
    weekday_task_start_times = {
        "Monday": monday_task_start_time,
        "Tuesday": tuesday_task_start_time,
        "Wednesday": wednesday_task_start_time,
        "Thursday": thursday_task_start_time,
        "Friday": friday_task_start_time,
        "Saturday": saturday_task_start_time,
        "Sunday": sunday_task_start_time
    }

    # Gather tasks with set times from task lists and add to task_schedule
    for task_list in [homework_tasks_list, work_tasks_list, chores_tasks_list, misc_tasks_list]:
        for task in task_list:
            task_name, spoons_needed, done, days, due_date, start_time, end_time = task[:7]
            if start_time != [0, 0, 0, 0] and end_time != [0, 0, 0, 0]:  # Only add tasks with specific times
                date_str = due_date.strftime("%Y-%m-%d")
                if date_str not in task_schedule:
                    task_schedule[date_str] = []
                task_schedule[date_str].append({"name": task_name, "start_time": start_time, "end_time": end_time})

    # Process each day in the next 5 days
    for day in dates:
        first_class = True
        day_str = day.strftime("%Y-%m-%d")
        weekday_name = day.strftime("%A")

        # Determine the start of the day based on the specific weekday's task start time
        start_hour, start_minute = weekday_task_start_times.get(weekday_name, (6, 0))
        start_of_day = start_hour * 60 + start_minute
        end_of_day = end_hour * 60
        occupied_blocks = []

        # Include class and commute times in occupied_blocks based on the weekday
        if weekday_name in class_schedule:
            for class_info in class_schedule[weekday_name]:
                start_time = class_info["start_time"]
                end_time = class_info["end_time"]

                # Calculate start and end in minutes from the day's start
                class_start_minutes = (start_time[0] * 10 + start_time[1]) * 60 + (start_time[2] * 10 + start_time[3])
                class_end_minutes = (end_time[0] * 10 + end_time[1]) * 60 + (end_time[2] * 10 + end_time[3])

                if first_class == True:
                    occupied_blocks.append((class_start_minutes-45, class_end_minutes))
                    first_class = False
                else:
                    occupied_blocks.append((class_start_minutes-20, class_end_minutes))

        # Include tasks with set times in occupied_blocks
        for task in task_schedule.get(day_str, []):
            start_time, end_time = task["start_time"], task["end_time"]
            task_start_minutes = (start_time[0] * 10 + start_time[1]) * 60 + (start_time[2] * 10 + start_time[3])
            task_end_minutes = (end_time[0] * 10 + end_time[1]) * 60 + (end_time[2] * 10 + end_time[3])
            occupied_blocks.append((task_start_minutes, task_end_minutes))

        # Sort and check occupied_blocks
        occupied_blocks.sort()
        available_blocks = []
        last_end_time = start_of_day

        for start, end in occupied_blocks:
            if last_end_time < start:
                available_blocks.append({
                    'start_time': (last_end_time // 60, last_end_time % 60),
                    'end_time': (start // 60, start % 60)
                })
            last_end_time = max(last_end_time, end)

        # Add final available block if any
        if last_end_time < end_of_day:
            available_blocks.append({
                'start_time': (last_end_time // 60, last_end_time % 60),
                'end_time': (end_of_day // 60, end_of_day % 60)
            })

        # Store in dictionary
        available_blocks_by_date[day_str] = available_blocks
        # Debug: print the occupied and available blocks for verification

    return available_blocks_by_date, task_schedule

def sort_tasks_by_priority_and_due_date():
    """
    Gather tasks from global lists, sort them by due date and type priority, and return a sorted list of tasks
    without assigned times, ready for scheduling.

    Returns:
    - sorted_tasks: list of tasks sorted by due date and priority (chore tasks prioritized, others by urgency)
    """

    # Dictionary to define task priorities
    task_priority = {
        "homework": 1,    # Highest priority
        "work": 2,
        "chores": 3,
        "misc": 4       # Lowest priority
    }

    # Collect tasks that do not yet have assigned start/end times
    unscheduled_tasks = []

    # Add unscheduled tasks from each global list
    add_unscheduled_tasks(homework_tasks_list, "homework", task_priority, unscheduled_tasks)
    add_unscheduled_tasks(chores_tasks_list, "chores", task_priority, unscheduled_tasks)
    add_unscheduled_tasks(work_tasks_list, "work", task_priority, unscheduled_tasks)
    add_unscheduled_tasks(misc_tasks_list, "misc", task_priority, unscheduled_tasks)

    # Sort the tasks by (1) due date, (2) priority (chore first), then by task type within the same due date
    sorted_tasks = sorted(
        unscheduled_tasks,
        key=lambda t: (t["due_date"], t["priority"])
    )

    return sorted_tasks

def add_unscheduled_tasks(task_list, task_type, task_priority, unscheduled_tasks):
    for task in task_list:
        task_name, spoons_needed, done, days, due_date, start_time, end_time = task[:7]
        # Only add tasks without assigned times (all zeros)
        if start_time == [0, 0, 0, 0] and end_time == [0, 0, 0, 0]:
            # Convert due_date to a datetime if it's not already
            parsed_due_date = due_date if isinstance(due_date, datetime) else datetime.strptime(due_date, "%Y-%m-%d")
            
            unscheduled_tasks.append({
                "task_name": task_name,
                "spoons_needed": spoons_needed,
                "due_date": parsed_due_date,
                "task_type": task_type,
                "priority": task_priority[task_type]
            })

def allocate_tasks_to_time_blocks(available_blocks_by_date, sorted_tasks):
    """
    Allocates tasks to available time blocks in a given schedule, with a 20-minute break after each hour of task time.
    
    Args:
    - available_blocks_by_date: Dict with keys as dates and values as lists of available time blocks for each date.
    - sorted_tasks: List of tasks sorted by due date and priority.
    
    Returns:
    - scheduled_tasks: A dictionary where each date has tasks allocated with start and end times.
    """
    scheduled_tasks = {}
    original_break_duration = 30
    break_duration = original_break_duration  # Break duration in minutes
    max_task_time_before_break = 60  # Maximum work time before a break
    accumulated_task_time = 0
    today = datetime.today().strftime("%Y-%m-%d")

    for task in sorted_tasks:
        task_name = task["task_name"]
        spoons_needed = task["spoons_needed"]
        duration_minutes = spoons_needed * 20  # Duration in minutes
        due_date = task["due_date"].strftime("%Y-%m-%d")
        
        remaining_task_time = duration_minutes

        for day, available_blocks in available_blocks_by_date.items():
            if (day >= today and task["task_type"] in ["homework", "work"]) or (day == due_date and task["task_type"] in ["chores", "misc"]):
                for block in available_blocks:
                    current_block_start = block["start_time"][0] * 60 + block["start_time"][1]
                    block_end = block["end_time"][0] * 60 + block["end_time"][1]
                    block_duration = block_end - current_block_start

                    # Continue allocating task time and breaks within the block
                    while remaining_task_time > 0 and block_duration > 0:
                        # Schedule a break if accumulated time is 60 minutes or more
                        if (accumulated_task_time >= max_task_time_before_break) and break_duration == original_break_duration:
                            # Define break start and end times
                            break_time = min(break_duration, block_duration)
                            break_start_minutes = current_block_start
                            break_end_minutes = break_start_minutes + break_time
                            break_start_time = (break_start_minutes // 60, break_start_minutes % 60)
                            break_end_time = (break_end_minutes // 60, break_end_minutes % 60)

                            # Schedule break
                            if day not in scheduled_tasks:
                                scheduled_tasks[day] = []
                            scheduled_tasks[day].append({
                                "name": "Break",
                                "start_time": break_start_time,
                                "end_time": break_end_time
                            })

                            # Update for remaining break time and reset accumulated task time
                            current_block_start = break_end_minutes
                            block_duration -= break_time
                            accumulated_task_time = 0  # Reset after a break

                            # If a partial break was taken, continue the rest in the next block
                            if break_time < break_duration:
                                break_duration -= break_time
                                break
                            else:
                                break_duration = original_break_duration  # Reset full break duration

                        elif break_duration != original_break_duration:
                            break_start_minutes = current_block_start
                            break_end_minutes = break_start_minutes + break_duration
                            break_start_time = (break_start_minutes // 60, break_start_minutes % 60)
                            break_end_time = (break_end_minutes // 60, break_end_minutes % 60)

                            if day not in scheduled_tasks:
                                scheduled_tasks[day] = []
                            scheduled_tasks[day].append({
                                "name": "Break",
                                "start_time": break_start_time,
                                "end_time": break_end_time
                            })

                            # Update for remaining break time and reset accumulated task time
                            current_block_start = break_end_minutes
                            block_duration -= break_time
                            accumulated_task_time = 0  # Reset after a break

                        # Allocate task time within remaining block
                        time_to_allocate = min(remaining_task_time, block_duration)
                        task_start_minutes = current_block_start
                        task_end_minutes = task_start_minutes + time_to_allocate
                        task_start_time = (task_start_minutes // 60, task_start_minutes % 60)
                        task_end_time = (task_end_minutes // 60, task_end_minutes % 60)

                        if task_end_minutes - task_start_minutes <= 60: # check if task is less than 1 hour
                            # Schedule task
                            if day not in scheduled_tasks:
                                scheduled_tasks[day] = []
                            scheduled_tasks[day].append({
                                "name": task_name,
                                "start_time": task_start_time,
                                "end_time": task_end_time
                            })
                        else:
                            task_end_minutes = task_start_minutes + 60
                            task_start_time = (task_start_minutes // 60, task_start_minutes % 60)
                            task_end_time = (task_end_minutes // 60, task_end_minutes % 60)

                            if day not in scheduled_tasks:
                                scheduled_tasks[day] = []
                            scheduled_tasks[day].append({
                                "name": task_name,
                                "start_time": task_start_time,
                                "end_time": task_end_time
                            })

                            # Update time counters
                            task_start_minutes = task_end_time  # Move to next block start
                            remaining_task_time -= 60  # Deduct one hour from remaining time

                        # Update remaining task and block durations
                        remaining_task_time -= time_to_allocate
                        accumulated_task_time += time_to_allocate
                        current_block_start = task_end_minutes
                        block_duration -= time_to_allocate

                    # Adjust block start time for remaining available time
                    block["start_time"] = (current_block_start // 60, current_block_start % 60)

                    # Stop allocating the current task if it's completed
                    if remaining_task_time == 0:
                        break

                # Move to next task once fully scheduled
                if remaining_task_time == 0:
                    break

    return scheduled_tasks

def remove_task(task_list, buttons, event):
    global scroll_offset, scroll_last_update_time
    current_time = pygame.time.get_ticks() / 1000  # Current time in seconds
    task_removed = False

    if event.type == pygame.MOUSEBUTTONDOWN:
        for button, index in buttons:
            if button.collidepoint(event.pos):
                task_list.pop(index)  # Remove the task from the list
                task_removed = True  # Flag that a task was removed
                # Adjust scroll_offset if needed
                if scroll_offset > 0 and len(task_list) <= scroll_offset + 8:
                    scroll_offset -= 1
                break  # Exit loop after removing the task

        if task_removed:
            # Rebuild the buttons list after a task is removed
            buttons.clear()
            visible_tasks = task_list[scroll_offset:scroll_offset + 8]
            for i, _ in enumerate(visible_tasks):
                # Recreate the button positions for each task
                button = pygame.Rect(100, 100 + i * 60, 600, 50)
                buttons.append((button, scroll_offset + i))

    # Handle scrolling logic
    if scroll_bar_up_button.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        # Scroll up if enough time has passed since the last scroll
        if current_time - scroll_last_update_time >= scroll_update_interval and scroll_offset > 0:
            scroll_offset -= 1
            scroll_last_update_time = current_time  # Update the last update time
    elif scroll_bar_down_button.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        # Scroll down if enough time has passed since the last scroll
        if current_time - scroll_last_update_time >= scroll_update_interval and scroll_offset < len(task_list) - 8:
            scroll_offset += 1
            scroll_last_update_time = current_time  # Update the last update time

def remove_completed_tasks(tasks_to_remove):
    global spoons
    for index in sorted(tasks_to_remove, reverse=True):
        spoons_needed = tasks[index][1]
        tasks.pop(index)

def complete_task(task_list, buttons, event):
    global spoons, scroll_offset, scroll_last_update_time
    current_time = pygame.time.get_ticks() / 1000  # Current time in seconds
    task_completed = False

    if event.type == pygame.MOUSEBUTTONDOWN:
        # Handle clicking on tasks to mark as complete
        for button, index in buttons:
            if button.collidepoint(event.pos) and task_list[index][2] == "❌":
                if spoons >= task_list[index][1]:
                    task_data = list(task_list[index])  # Convert tuple to list
                    task_data[2] = '✅'  # Mark task as complete
                    task_list[index] = tuple(task_data)  # Update back as tuple
                    spoons -= task_list[index][1]
                    task_completed = True
                    break
                else:
                    print("Not enough spoons to complete this task.")

    # Handle scrolling logic
    if scroll_bar_up_button.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        # Scroll up if enough time has passed since the last scroll
        if current_time - scroll_last_update_time >= scroll_update_interval and scroll_offset > 0:
            scroll_offset -= 1
            scroll_last_update_time = current_time  # Update the last update time
    elif scroll_bar_down_button.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        # Scroll down if enough time has passed since the last scroll
        if current_time - scroll_last_update_time >= scroll_update_interval and scroll_offset < len(task_list) - 8:
            scroll_offset += 1
            scroll_last_update_time = current_time  # Update the last update time

    return task_completed

def hub_buttons(event):
    global scroll_offset
    if not hub_buttons_showing:
        return None
    if event.type == pygame.MOUSEBUTTONDOWN:
        if hub_add_spoons.collidepoint(event.pos):
            return "input_spoons"
        elif hub_add_task.collidepoint(event.pos):
            return "input_tasks"
        elif hub_complete_task.collidepoint(event.pos):
            scroll_offset = 0
            return "complete_tasks"
        elif hub_remove_task.collidepoint(event.pos):
            scroll_offset = 0
            return "remove_tasks"
        elif hub_daily_schedule.collidepoint(event.pos):
            return "daily_schedule"
        elif hub_calendar.collidepoint(event.pos):
            return "calendar"
        elif hub_settings.collidepoint(event.pos):
            return "settings"
    return None 

def get_color_at_pos(pos):
    color_wheel_rect = color_wheel.get_rect(center=(400, 200))
    global r
    global g
    global b
    if color_wheel_rect.collidepoint(pos):
        local_pos = (pos[0] - color_wheel_rect.left, pos[1] - color_wheel_rect.top)
        color = color_wheel.get_at(local_pos)
        if color[3] > 0:
            r, g, b = color[:3]
            return r, g, b
    return None

def task_to_serializable(task):
    if len(task) == 7:  # Task has start_time and end_time
        task_name, spoons_needed, done, days_till_due_date, due_date, start_time, end_time = task
        return {
            "task_name": task_name,
            "spoons_needed": spoons_needed,
            "done": done,
            "days_till_due_date": days_till_due_date,
            "due_date": due_date.isoformat(),
            "start_time": start_time,
            "end_time": end_time
        }
    elif len(task) == 5:  # Task without start_time and end_time
        task_name, spoons_needed, done, days_till_due_date, due_date = task
        return {
            "task_name": task_name,
            "spoons_needed": spoons_needed,
            "done": done,
            "days_till_due_date": days_till_due_date,
            "due_date": due_date.isoformat()
        }

def save_data():
    data = {
        "spoons": spoons,
        "homework_tasks_list": [task_to_serializable(task) for task in homework_tasks_list],
        "chores_tasks_list": [task_to_serializable(task) for task in chores_tasks_list],
        "work_tasks_list": [task_to_serializable(task) for task in work_tasks_list],
        "misc_tasks_list": [task_to_serializable(task) for task in misc_tasks_list],
        "daily_spoons": daily_spoons,  # Save daily spoon values
        "colors": {
            "background_color": background_color,
            "done_button_color": done_button_color,
            "add_tasks_choose_folder_color": add_tasks_choose_folder_color,
            "add_tasks_chosen_folder_color": add_tasks_chosen_folder_color,
            "complete_tasks_hub_folder_color": complete_tasks_hub_folder_color,
            "complete_tasks_task_color": complete_tasks_task_color,
            "remove_tasks_hub_folder_color": remove_tasks_hub_folder_color,
            "remove_tasks_task_color": remove_tasks_task_color,
            "add_spoons_color": add_spoons_color,
            "add_tasks_color": add_tasks_color,
            "complete_tasks_color": complete_tasks_color,
            "remove_tasks_color": remove_tasks_color,
            "daily_schedule_color": daily_schedule_color,
            "calendar_color": calendar_color,
            "settings_color": settings_color,
            "calendar_current_day_color": calendar_current_day_color,
            "calendar_current_day_header_color": calendar_current_day_header_color,
            "calendar_previous_day_color": calendar_previous_day_color,
            "calendar_previous_day_header_color": calendar_previous_day_header_color,
            "calendar_next_day_color": calendar_next_day_color,
            "calendar_next_day_header_color": calendar_next_day_header_color,
            "calendar_month_color": calendar_month_color,
            "homework_fol_color": homework_fol_color,
            "chores_fol_color": chores_fol_color,
            "work_fol_color": work_fol_color,
            "misc_fol_color": misc_fol_color
        }
    }
    try:
        with open("data.json", "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Error saving data: {e}")

def task_from_serializable(task):
    # Default values for start_time and end_time
    default_start_time = [0, 0, 0, 0]
    default_end_time = [0, 0, 0, 0]

    # Extract fields with defaults for optional fields
    task_name = task.get("task_name", "")
    spoons_needed = task.get("spoons_needed", 0)
    done = task.get("done", "❌")
    days_till_due_date = task.get("days_till_due_date", 0)
    due_date_str = task.get("due_date", "1970-01-01T00:00:00")
    due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M:%S')
    start_time = task.get("start_time", default_start_time)
    end_time = task.get("end_time", default_end_time)

    # Return the task as a list with all fields
    return [task_name, spoons_needed, done, days_till_due_date, due_date, start_time, end_time]

def load_data():
    global spoons, homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list
    global background_color, done_button_color, add_tasks_choose_folder_color, add_tasks_chosen_folder_color
    global complete_tasks_hub_folder_color, complete_tasks_task_color, remove_tasks_hub_folder_color
    global remove_tasks_task_color, add_spoons_color, add_tasks_color, complete_tasks_color, remove_tasks_color
    global daily_schedule_color, calendar_color, settings_color, calendar_current_day_color
    global calendar_current_day_header_color, calendar_previous_day_color, calendar_previous_day_header_color
    global calendar_next_day_color, calendar_next_day_header_color, calendar_month_color
    global homework_fol_color, chores_fol_color, work_fol_color, misc_fol_color, daily_spoons

    try:
        with open("data.json", "r") as f:
            data = json.load(f)

            # Task Lists
            spoons = data.get("spoons", 0)
            homework_tasks_list = [task_from_serializable(task) for task in data.get("homework_tasks_list", [])]
            chores_tasks_list = [task_from_serializable(task) for task in data.get("chores_tasks_list", [])]
            work_tasks_list = [task_from_serializable(task) for task in data.get("work_tasks_list", [])]
            misc_tasks_list = [task_from_serializable(task) for task in data.get("misc_tasks_list", [])]
            print("Tasks loaded successfully")

            # Colors
            colors = data.get("colors", {})
            background_color = tuple(colors.get("background_color", (255, 255, 255)))  # Default to white
            done_button_color = tuple(colors.get("done_button_color", (0, 0, 0)))
            add_tasks_choose_folder_color = tuple(colors.get("add_tasks_choose_folder_color", (200, 200, 200)))
            add_tasks_chosen_folder_color = tuple(colors.get("add_tasks_chosen_folder_color", (200, 200, 200)))
            complete_tasks_hub_folder_color = tuple(colors.get("complete_tasks_hub_folder_color", (200, 200, 200)))
            complete_tasks_task_color = tuple(colors.get("complete_tasks_task_color", (200, 200, 200)))
            remove_tasks_hub_folder_color = tuple(colors.get("remove_tasks_hub_folder_color", (200, 200, 200)))
            remove_tasks_task_color = tuple(colors.get("remove_tasks_task_color", (200, 200, 200)))
            add_spoons_color = tuple(colors.get("add_spoons_color", (200, 200, 200)))
            add_tasks_color = tuple(colors.get("add_tasks_color", (200, 200, 200)))
            complete_tasks_color = tuple(colors.get("complete_tasks_color", (200, 200, 200)))
            remove_tasks_color = tuple(colors.get("remove_tasks_color", (200, 200, 200)))
            daily_schedule_color = tuple(colors.get("daily_schedule_color", (200, 200, 200)))
            calendar_color = tuple(colors.get("calendar_color", (200, 200, 200)))
            settings_color = tuple(colors.get("settings_color", (200, 200, 200)))
            calendar_current_day_color = tuple(colors.get("calendar_current_day_color", (200, 200, 200)))
            calendar_current_day_header_color = tuple(colors.get("calendar_current_day_header_color", (200, 200, 200)))
            calendar_previous_day_color = tuple(colors.get("calendar_previous_day_color", (200, 200, 200)))
            calendar_previous_day_header_color = tuple(colors.get("calendar_previous_day_header_color", (200, 200, 200)))
            calendar_next_day_color = tuple(colors.get("calendar_next_day_color", (200, 200, 200)))
            calendar_next_day_header_color = tuple(colors.get("calendar_next_day_header_color", (200, 200, 200)))
            calendar_month_color = tuple(colors.get("calendar_month_color", (200, 200, 200)))
            homework_fol_color = tuple(colors.get("homework_fol_color", (200, 200, 200)))
            chores_fol_color = tuple(colors.get("chores_fol_color", (200, 200, 200)))
            work_fol_color = tuple(colors.get("work_fol_color", (200, 200, 200)))
            misc_fol_color = tuple(colors.get("misc_fol_color", (200, 200, 200)))
            
            # Load daily spoons data
            daily_spoons = data.get("daily_spoons", {"Mon": 0, "Tue": 0, "Wed": 0, "Thu": 0, "Fri": 0, "Sat": 0, "Sun": 0})

    except Exception as e:
        print(f"Error loading data: {e}")

load_data()

# ----------------------------------------------------------------------------------------------------
# Main loop
# ----------------------------------------------------------------------------------------------------

while running:
    max_days = calendar.monthrange(datetime.now().year, task_month)[1]  # Get days in the current month
    mouse_pos = pygame.mouse.get_pos()
    current_month = datetime.now().month
    current_day = datetime.now().day
# Check if the day or month has changed to update task days and reset spoons
    if int(current_day) > int(previous_day) or int(current_month) > int(previous_month):
        # Get the current day of the week (0 = Monday, 6 = Sunday)
        # Get the current weekday as a three-letter abbreviation
        current_weekday = datetime.now().strftime("%a")  # This will give "Mon", "Tue", etc.

        # Set spoons to the corresponding daily value
        spoons = daily_spoons.get(current_weekday, spoons)


        # Update tasks in each list to decrement days left
        if homework_tasks_list:
            for task in homework_tasks_list:
                if task[3] > 0:  # Ensure days don't go below zero
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

        # Update the previous day and month to the current values
        previous_day = current_day
        previous_month = current_month
        print(f"Date changed: {current_month}/{current_day}. Days left updated and spoons reset to {spoons}.")

    screen.fill(background_color)
    tasks_to_remove = []

    if page == "input_spoons":
        draw_input_spoons(screen, daily_spoons, spoons, done_button_color)
        hub_buttons_show()
    elif page == "input_tasks":
        draw_input_tasks(screen, spoons, current_task, current_spoons, 
                         folder, task_month, task_day, time_toggle_on, start_time, end_time,
                         done_button_color, add_tasks_choose_folder_color, add_tasks_chosen_folder_color)
        hub_buttons_show()
    elif page == "complete_tasks":
        draw_complete_tasks_hub(screen, mouse_pos, page, tool_tips, spoons,
                            homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list,
                            complete_tasks_hub_folder_color)
        hub_buttons_show()
    elif page == "complete_homework_tasks":
        draw_complete_tasks(screen, "Homework", homework_tasks_list, task_buttons_homework, spoons, scroll_offset,
                        complete_tasks_task_color)
        hub_buttons_show()
    elif page == "complete_chores_tasks":
        draw_complete_tasks(screen,"Chores", chores_tasks_list, task_buttons_chores, spoons, scroll_offset,
                        complete_tasks_task_color)
        hub_buttons_show()
    elif page == "complete_work_tasks":
        draw_complete_tasks(screen,"Work", work_tasks_list, task_buttons_work, spoons, scroll_offset,
                        complete_tasks_task_color)
        hub_buttons_show()
    elif page == "complete_misc_tasks":
        draw_complete_tasks(screen,"Misc", misc_tasks_list, task_buttons_misc, spoons, scroll_offset,
                        complete_tasks_task_color)
        hub_buttons_show()
    elif page == "remove_tasks":
        draw_remove_tasks_hub(screen, spoons,
                            homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list,
                            remove_tasks_hub_folder_color)
        hub_buttons_show()
    elif page == "remove_homework_tasks":
        draw_remove_tasks(screen, "Homework", homework_tasks_list, task_buttons_homework, spoons, scroll_offset,
                        remove_tasks_task_color)
        hub_buttons_show()
    elif page == "remove_chores_tasks":
        draw_remove_tasks(screen, "Chores", chores_tasks_list, task_buttons_chores, spoons, scroll_offset,
                        remove_tasks_task_color)
        hub_buttons_show()
    elif page == "remove_work_tasks":
        draw_remove_tasks(screen, "Work", work_tasks_list, task_buttons_work, spoons, scroll_offset,
                        remove_tasks_task_color)
        hub_buttons_show()
    elif page == "remove_misc_tasks":
        draw_remove_tasks(screen, "Misc", misc_tasks_list, task_buttons_misc, spoons, scroll_offset,
                        remove_tasks_task_color)
        hub_buttons_show()
    elif page == "daily_schedule":
        available_blocks_by_date, task_schedule = get_available_time_blocks(class_schedule)
        draw_daily_schedule(screen, allocate_tasks_to_time_blocks(available_blocks_by_date, sort_tasks_by_priority_and_due_date()),
                        homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list,
                        homework_fol_color, chores_fol_color, work_fol_color, misc_fol_color, background_color, calendar_previous_day_header_color, calendar_next_day_header_color)
        hub_buttons_show()
    elif page == "calendar":
        draw_calendar(screen, 
                  homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list,
                  displayed_month, displayed_year,
                  homework_fol_color, chores_fol_color, work_fol_color, misc_fol_color,calendar_month_color, 
                  calendar_previous_day_header_color, calendar_next_day_header_color, calendar_current_day_header_color,
                  calendar_previous_day_color, calendar_current_day_color, calendar_next_day_color)
        hub_buttons_show()
    elif page == "settings":
        draw_settings(screen, tool_tips, spoon_name_input, button_chosen, hub_button_chosen, calendar_button_chosen)
        hub_buttons_show()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_data()
            running = False
        handle_scroll(event)
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION):
            if hub_buttons_showing and hub_cover.collidepoint(event.pos):
                new_page = hub_buttons(event)
                if new_page:
                    page = new_page
                continue
        new_page = hub_buttons(event)
        if new_page:
            page = new_page

        if page == "input_spoons":
           spoons, daily_spoons = logic_input_spoons(event, short_rest_amount, half_rest_amount, full_rest_amount, 
                                                           daily_spoons, spoons, draw_input_spoons(screen, daily_spoons, spoons, done_button_color), input_active)
        elif page == "input_tasks":
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Toggle time entry
                if time_toggle_button.collidepoint(event.pos):
                    time_toggle_on = not time_toggle_on

                # Task input boxes
                if task_input_box.collidepoint(event.pos):
                    input_active = "task"
                elif spoon_input_box.collidepoint(event.pos):
                    input_active = "spoons"

                # Month and day button handling
                if time_toggle_on:
                    if month_up_button_shifted.collidepoint(event.pos):
                        task_month = task_month + 1 if task_month < 12 else 1
                    elif month_down_button_shifted.collidepoint(event.pos):
                        task_month = task_month - 1 if task_month > 1 else 12
                    elif day_up_button_shifted.collidepoint(event.pos):
                        task_day = int(task_day) + 1 if int(task_day) < max_days else 1
                    elif day_down_button_shifted.collidepoint(event.pos):
                        task_day = int(task_day) - 1 if int(task_day) > 1 else max_days
                else:
                    if month_up_button_normal.collidepoint(event.pos):
                        task_month = task_month + 1 if task_month < 12 else 1
                    elif month_down_button_normal.collidepoint(event.pos):
                        task_month = task_month - 1 if task_month > 1 else 12
                    elif day_up_button_normal.collidepoint(event.pos):
                        task_day = int(task_day) + 1 if int(task_day) < max_days else 1
                    elif day_down_button_normal.collidepoint(event.pos):
                        task_day = int(task_day) - 1 if int(task_day) > 1 else max_days

                # Start and end time input boxes
                if start_time_input_box.collidepoint(event.pos):
                    input_active = "start_time"
                elif end_time_input_box.collidepoint(event.pos):
                    input_active = "end_time"

                # Done button
                elif done_button.collidepoint(event.pos):
                    if current_task and current_spoons:
                        task_date = datetime(current_time.year, int(task_month), int(task_day))
                        days_till_due_date = (task_date - current_time).days

                        # Append to the appropriate task list based on folder
                        task_entry = [current_task, current_spoons, "❌", days_till_due_date+1, task_date]
                        if time_toggle_on:  # Only add times if the toggle is on
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

                        # Reset inputs
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

            # Handle key inputs for task name, spoons, day, and time
            if event.type == pygame.KEYDOWN:
                if input_active == "task":
                    if event.key == pygame.K_RETURN:
                        input_active = "spoons"
                    elif event.key == pygame.K_BACKSPACE:
                        current_task = current_task[:-1]
                    else:
                        current_task += event.unicode

                elif input_active == "spoons":
                    if event.key == pygame.K_RETURN:
                        if current_task and current_spoons:
                            tasks.append((current_task, current_spoons))
                            current_task = ""
                            current_spoons = 0
                        else:
                            page = "complete_tasks"
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        current_spoons = current_spoons // 10
                    else:
                        try:
                            current_spoons = current_spoons * 10 + int(event.unicode)
                        except ValueError:
                            pass

                elif input_active in ["start_time", "end_time"]:
                    # Choose the correct time list to modify
                    time_component = start_time if input_active == "start_time" else end_time

                    # Shift time digits to the left with new input
                    if event.key == pygame.K_BACKSPACE:
                        time_component = [0] + time_component[:3]  # Shift right with a leading zero
                    elif event.unicode.isdigit():
                        # Shift left and add the new digit at the end
                        time_component = time_component[1:] + [int(event.unicode)]

                    # Update the correct variable
                    if input_active == "start_time":
                        start_time = time_component
                    elif input_active == "end_time":
                        end_time = time_component
                     
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
            complete_task(homework_tasks_list, task_buttons_homework, event)
        elif page == "complete_chores_tasks":
            complete_task(chores_tasks_list, task_buttons_chores, event)
        elif page == "complete_work_tasks":
            complete_task(work_tasks_list, task_buttons_work, event)
        elif page == "complete_misc_tasks":
            complete_task(misc_tasks_list, task_buttons_misc, event)

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
            remove_task(homework_tasks_list, task_buttons_homework, event)
        elif page == "remove_chores_tasks":
            remove_task(chores_tasks_list, task_buttons_chores, event)
        elif page == "remove_work_tasks":
            remove_task(work_tasks_list, task_buttons_work, event)
        elif page == "remove_misc_tasks":
            remove_task(misc_tasks_list, task_buttons_misc, event)

        elif page == "calendar": 
            displayed_month, displayed_year = logic_calendar(event, displayed_month, displayed_year)

        elif page == "daily_schedule":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if last_day_button.collidepoint(event.pos):
                    day_offset -= 1  # Move back one day
                elif next_day_button.collidepoint(event.pos):
                    day_offset += 1  # Move forward one day
                    # Step 1: Get the available time blocks by date and the initial task schedule
                    available_blocks_by_date, task_schedule = get_available_time_blocks(class_schedule)

                    # Step 2: Sort unscheduled tasks by priority and due date
                    sorted_tasks = sort_tasks_by_priority_and_due_date()
                    print("fuck")
                    print(available_blocks_by_date)
                    print("shit")

                    # Step 3: Call allocate_tasks_to_time_blocks with the necessary inputs
                    # Note: We're not passing task_schedule directly to `allocate_tasks_to_time_blocks`, so it will
                    #       dynamically add scheduled tasks into the returned final_schedule.
                    final_schedule = allocate_tasks_to_time_blocks(available_blocks_by_date, sorted_tasks)

                    # Step 4: Print the final schedule to verify the results
                    print("boop")
                    for date, tasks in final_schedule.items():
                        print(f"Date: {date}")
                        for task in tasks:
                            # Check if task has the expected keys
                            if "name" in task and "start_time" in task and "end_time" in task:
                                print(f"  Task: {task['name']}, Start: {task['start_time']}, End: {task['end_time']}")
                            else:
                                 #Print the task directly if structure is unexpected for further inspection
                                print("  Task (unexpected structure):", task)
                    #print("beep")
                    #print(final_schedule)

        elif page == "settings":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if tool_tip_toggle.collidepoint(event.pos):
                    tool_tips = not tool_tips
                if spoon_name_input_box.collidepoint(event.pos):
                    input_active = "spoon_name"
                else:
                    input_active = False
                if spoon_image_outline.collidepoint(event.pos):
                    icon_image = spoon_image
                if battery_image_outline.collidepoint(event.pos):
                    icon_image = battery_image
                if star_image_outline.collidepoint(event.pos):
                    icon_image = star_image
                if potion_image_outline.collidepoint(event.pos):
                    icon_image = potion_image
                if aquatic_theme.collidepoint(event.pos):
                    try:
                        switch_theme("aquatic", globals())
                    except ValueError as e:
                        print(e)
                elif foresty_theme.collidepoint(event.pos):
                    try:
                        switch_theme("foresty", globals())
                    except ValueError as e:
                        print(e)
                elif girly_pop_theme.collidepoint(event.pos):
                    try:
                        switch_theme("girly_pop", globals())
                    except ValueError as e:
                        print(e)
                elif vampire_goth_theme.collidepoint(event.pos):
                    try:
                        switch_theme("vampire_goth", globals())
                    except ValueError as e:
                        print(e)
                elif sunset_glow_theme.collidepoint(event.pos):
                    try:
                        switch_theme("sunset_glow", globals())
                    except ValueError as e:
                        print(e)
    
            elif event.type == pygame.KEYDOWN and input_active == "spoon_name":
                if event.key == pygame.K_RETURN:
                    # Update the spoon_name variable when Enter is pressed
                    spoon_name = spoon_name_input
                    spoon_name_input = ""  # Clear the input
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    # Remove the last character from the input
                    spoon_name_input = spoon_name_input[:-1]
                else:
                    # Add new characters to the input
                    spoon_name_input += event.unicode  
    
    remove_completed_tasks(tasks_to_remove)
    pygame.display.flip()

pygame.quit()
sys.exit()