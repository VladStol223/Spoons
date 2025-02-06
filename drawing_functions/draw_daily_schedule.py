from config import *
from datetime import datetime
from datetime import timedelta

from drawing_functions.draw_rounded_button import draw_rounded_button

import pygame

def draw_daily_schedule(screen, scheduled_tasks,
                        homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list, day_offset,
                        homework_fol_color, chores_fol_color, work_fol_color, misc_fol_color, background_color, calendar_previous_day_header_color, calendar_next_day_header_color):
    global hub_buttons_showing, dropdown_colors_open, current_time_indicator, scroll_offset, scroll_limit, scroll_multiplier

    # Set up layout parameters
    scroll_offset = 30
    day_offset = 0
    start_hour = 6
    end_hour = 24
    hour_height = 90
    start_y = 50 - scroll_offset  # Adjust vertical start position by scroll offset
    left_margin = 100
    current_time = datetime.now()
    scroll_limit = ((end_hour - start_hour) * hour_height) - 550
    scroll_multiplier = 30

    # Calculate dates for the three days in view based on day_offset
    today = current_time + timedelta(days=day_offset)
    next_day = today + timedelta(days=1)
    next_next_day = today + timedelta(days=2)

    # Define x-coordinates for the columns of each day
    day_x_coords = {
        today.strftime('%A'): 100,
        next_day.strftime('%A'): 325,
        next_next_day.strftime('%A'): 550
    }

    day_dates = [today.strftime('%Y-%m-%d'), next_day.strftime('%Y-%m-%d'), next_next_day.strftime('%Y-%m-%d')]

    # Draw the timeline with hours
    for hour in range(start_hour, end_hour):
        y_position = start_y + (hour - start_hour) * hour_height
        pygame.draw.line(screen, BLACK, (left_margin - 45, y_position), (left_margin + 690, y_position), 1)# type: ignore
        hour_text = small_one_font.render(f"{hour % 12 if hour % 12 else 12} {'AM' if hour < 12 else 'PM'}", True, BLACK)# type: ignore
        screen.blit(hour_text, (left_margin - 95, y_position - 5))

    # Divider lines for columns:
    pygame.draw.line(screen, BLACK, (65, 20), (65, 600), 1)# type: ignore
    pygame.draw.line(screen, BLACK, (215, 20), (215, 600), 1)# type: ignore
    pygame.draw.line(screen, BLACK, (365, 20), (365, 600), 1)# type: ignore
    pygame.draw.line(screen, BLACK, (515, 20), (515, 600), 1)# type: ignore
    pygame.draw.line(screen, BLACK, (665, 20), (665, 600), 1)# type: ignore

    task_colors = {
        "homework": homework_fol_color,
        "chores": chores_fol_color,
        "work": work_fol_color,
        "misc": misc_fol_color,
        "Break": LIGHT_GRAY# type: ignore
    }

    # Loop through each day and display scheduled tasks -------------------------------
    for i, day_date in enumerate(day_dates):
        weekday_name = list(day_x_coords.keys())[i]
        x_position = day_x_coords[weekday_name]

        if day_date in scheduled_tasks:
            for task in scheduled_tasks[day_date]:
                task_name = task["name"]
                start_time = task["start_time"]
                end_time = task["end_time"]

                # Determine color based on task name (e.g., breaks have a different color)
                #task_color = task_colors.get(task_type, misc_fol_color)
                task_color = BLUE# type: ignore

                # Convert start and end times to y-coordinates
                start_minutes = start_time[0] * 60 + start_time[1]
                end_minutes = end_time[0] * 60 + end_time[1]
                task_start_y = start_y + ((start_minutes - (start_hour * 60)) / 60) * hour_height
                task_end_y = start_y + ((end_minutes - (start_hour * 60)) / 60) * hour_height
                task_height = task_end_y - task_start_y

                # Draw the task block
                if task_name != 'Break':
                    task_rect = pygame.Rect(x_position + 25, task_start_y, 175, task_height)
                    draw_rounded_button(screen, task_rect, task_color, BLACK, 5, 3)# type: ignore

                    # Render and display the task name within the block, wrapping text if needed
                    max_width = task_rect.width - 10
                    words = task_name.split()
                    line = ""
                    y_offset = 10
                    for word in words:
                        # Check if adding this word would exceed the width
                        test_line = f"{line} {word}" if line else word
                        test_text = small_font.render(test_line, True, BLACK)# type: ignore
                        if test_text.get_width() > max_width:
                            # Render the current line and start a new one
                            rendered_line = small_font.render(line, True, BLACK)# type: ignore
                            screen.blit(rendered_line, (task_rect.x + 10, task_rect.y + y_offset - 3))
                            y_offset += rendered_line.get_height() + 2
                            line = word  # Start new line with current word
                        else:
                            line = test_line  # Add word to the current line

                    # Render any remaining text
                    if line:
                        rendered_line = small_font.render(line, True, BLACK)# type: ignore
                        screen.blit(rendered_line, (task_rect.x + 5, task_rect.y + y_offset))



    # Display classes for each day and commute ----------------------------------------
    for day_name, classes in class_schedule.items():
        if day_name in day_x_coords:
            x_position = day_x_coords[day_name]
            first_class = True

            # Loop through each class and calculate its position
            for class_info in classes:
                start_time, end_time = class_info["start_time"], class_info["end_time"]

                # Convert start and end time to y-coordinates
                start_hour_pos = start_time[0] * 10 + start_time[1]
                start_minute_pos = start_time[2] * 10 + start_time[3]
                end_hour_pos = end_time[0] * 10 + end_time[1]
                end_minute_pos = end_time[2] * 10 + end_time[3]

                task_start_y = start_y + ((start_hour_pos - start_hour) * hour_height) + int(hour_height * (start_minute_pos / 60))
                task_end_y = start_y + ((end_hour_pos - start_hour) * hour_height) + int(hour_height * (end_minute_pos / 60))
                task_height = task_end_y - task_start_y

                #Draw the commute block
                if first_class == True:
                    commute_rect = pygame.Rect(x_position + 25, task_start_y-68, 175, 68)
                    draw_rounded_button(screen, commute_rect, calendar_previous_day_header_color, BLACK, 5, 3)# type: ignore
                    first_class = False
                else:
                    commute_rect = pygame.Rect(x_position + 25, task_start_y-30, 175, 30)
                    draw_rounded_button(screen, commute_rect, calendar_previous_day_header_color, BLACK, 5, 3)# type: ignore

                rendered_line = small_font.render("commute", True, BLACK)# type: ignore
                screen.blit(rendered_line, (commute_rect.x + 9, commute_rect.y + 5))

                # Draw the class block
                class_rect = pygame.Rect(x_position + 25, task_start_y, 175, task_height)
                draw_rounded_button(screen, class_rect, calendar_next_day_header_color, BLACK, 5, 3)# type: ignore

                # Render and display the class name within the block, wrapping text if needed
                max_width = class_rect.width - 10
                words = class_info["name"].split()
                line = ""
                y_offset = 10
                for word in words:
                    # Check if adding this word would exceed the width
                    test_line = f"{line} {word}" if line else word
                    test_text = small_font.render(test_line, True, BLACK)# type: ignore
                    if test_text.get_width() > max_width:
                        # Render the current line and start a new one
                        rendered_line = small_font.render(line, True, BLACK)# type: ignore
                        screen.blit(rendered_line, (class_rect.x + 9, class_rect.y + y_offset))
                        y_offset += rendered_line.get_height() + 2
                        line = word  # Start new line with current word
                    else:
                        line = test_line  # Add word to the current line

                # Render any remaining text
                if line:
                    rendered_line = small_font.render(line, True, BLACK)# type: ignore
                    screen.blit(rendered_line, (class_rect.x + 9, class_rect.y + y_offset))

    # Collect tasks with valid times for today
    tasks_with_time = []
    today_date = current_time.date()
    task_colors = {
        "homework": homework_fol_color,
        "chores": chores_fol_color,
        "work": work_fol_color,
        "misc": misc_fol_color,}

    # Gather tasks with times for each category
    for task_list, task_type in zip(
        [homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list],
        ["homework", "chores", "work", "misc"]
    ):
        for task in task_list:
            task_name, spoons_needed, done, days, due_date, start_time, end_time = task[:7]
            if due_date.date() == today_date and start_time != [0, 0, 0, 0] and end_time != [0, 0, 0, 0]:
                tasks_with_time.append((task, task_type))  # Store the task with its type

    # Draw task blocks based on the category and time
    for (task, task_type) in tasks_with_time:
        task_name, spoons_needed, done, days, due_date, start_time, end_time = task[:7]
        
        # Calculate task start and end positions based on times
        start_hour_pos = start_time[0] * 10 + start_time[1]
        start_minute_pos = start_time[2] * 10 + start_time[3]
        end_hour_pos = end_time[0] * 10 + end_time[1]
        end_minute_pos = end_time[2] * 10 + end_time[3]
        
        task_start_y = start_y + ((start_hour_pos - start_hour) * hour_height) + int(hour_height * (start_minute_pos / 60))
        task_end_y = start_y + ((end_hour_pos - start_hour) * hour_height) + int(hour_height * (end_minute_pos / 60))
        task_height = task_end_y - task_start_y

        # Draw the task block in the color of its category
        task_rect = pygame.Rect(left_margin + 25, task_start_y, 175, task_height)
        draw_rounded_button(screen, task_rect, task_colors[task_type], BLACK, 5, 3)# type: ignore

        # Render and display the task name within the block, wrapping text if needed
        max_width = task_rect.width - 10
        words = task_name.split()
        line = ""
        y_offset = 10
        for word in words:
            # Check if adding this word would exceed the width
            test_line = f"{line} {word}" if line else word
            test_text = small_font.render(test_line, True, BLACK)# type: ignore
            if test_text.get_width() > max_width:
                # Render the current line and start a new one
                rendered_line = small_font.render(line, True, BLACK)# type: ignore
                screen.blit(rendered_line, (task_rect.x + 5, task_rect.y + y_offset))
                y_offset += rendered_line.get_height() + 2
                line = word  # Start new line with current word
            else:
                line = test_line  # Add word to the current line

        # Render any remaining text
        if line:
            rendered_line = small_font.render(line, True, BLACK)# type: ignore
            screen.blit(rendered_line, (task_rect.x + 5, task_rect.y + y_offset))

    pygame.draw.rect(screen, background_color, daily_schedule_top_cover)

    # Render the formatted text for each displayed day
    current_day_text = font.render(f"{today.strftime('%a')} - {today.strftime('%d')}", True, BLACK)# type: ignore
    screen.blit(current_day_text, (160, 16))
    next_day_text = font.render(f"{next_day.strftime('%a')} - {next_day.strftime('%d')}", True, BLACK)# type: ignore
    screen.blit(next_day_text, (385, 16))
    next_next_day_text = font.render(f"{next_next_day.strftime('%a')} - {next_next_day.strftime('%d')}", True, BLACK)# type: ignore
    screen.blit(next_next_day_text, (610, 16))

    draw_rounded_button(screen, last_day_button, calendar_next_day_header_color, BLACK, 0, 2)# type: ignore
    draw_rounded_button(screen, next_day_button, calendar_previous_day_header_color, BLACK, 0, 2)# type: ignore

    # Draw current time indicator line if within displayed hours
    if start_hour <= current_time.hour < end_hour:
        current_time_y = start_y + (current_time.hour - start_hour) * hour_height + int(hour_height * (current_time.minute / 60))
        if 50 <= current_time_y <= 650:
            pygame.draw.line(screen, RED, (left_margin + 25, current_time_y), (left_margin + 575, current_time_y), 2)# type: ignore

    # Draw hub toggle
    draw_rounded_button(screen, hub_toggle, LIGHT_GRAY, BLACK, 0, 2)# type: ignore
    pygame.draw.rect(screen, BLACK, hub_menu1)# type: ignore
    pygame.draw.rect(screen, BLACK, hub_menu2)# type: ignore
    pygame.draw.rect(screen, BLACK, hub_menu3)# type: ignore

def logic_daily_schedule(event, class_schedule, day_offset, homework_tasks_list, work_tasks_list, chores_tasks_list, misc_tasks_list):
    if event.type == pygame.MOUSEBUTTONDOWN:
                if last_day_button.collidepoint(event.pos):
                    day_offset -= 1  # Move back one day
                elif next_day_button.collidepoint(event.pos):
                    day_offset += 1  # Move forward one day
                    # Step 1: Get the available time blocks by date and the initial task schedule
                    available_blocks_by_date, task_schedule = get_available_time_blocks(class_schedule, homework_tasks_list, work_tasks_list, chores_tasks_list, misc_tasks_list)

                    # Step 2: Sort unscheduled tasks by priority and due date
                    sorted_tasks = sort_tasks_by_priority_and_due_date(homework_tasks_list, work_tasks_list, chores_tasks_list, misc_tasks_list)
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

def get_available_time_blocks(class_schedule, homework_tasks_list, work_tasks_list, chores_tasks_list, misc_tasks_list, start_hour=6, end_hour=24, 
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

def sort_tasks_by_priority_and_due_date(homework_tasks_list, work_tasks_list, chores_tasks_list, misc_tasks_list):
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