import json
import datetime
from switch_themes import switch_theme
from config import *

"""
Summary:
    Converts a task tuple into a serializable dictionary format.

Parameters:
    task (tuple): The task tuple containing task details.

Returns:
    dict: A dictionary representation of the task.
"""

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

"""
Summary:
    Saves the application data to a JSON file.

Parameters:
    spoons (int): The current number of spoons.
    homework_tasks_list (list): List of homework tasks.
    chores_tasks_list (list): List of chores tasks.
    work_tasks_list (list): List of work tasks.
    misc_tasks_list (list): List of miscellaneous tasks.
    daily_spoons (dict): Dictionary containing the number of spoons for each day of the week.
    theme (str): The current theme of the application.

Returns:
    No returns.
"""

def save_data(spoons, homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list, exams_tasks_list, projects_tasks_list,
              daily_spoons, theme, icon_image, spoon_name_input,
              folder_one, folder_two, folder_three, folder_four, folder_five, folder_six,
              streak_dates):

    icon_image_name = None
    if icon_image == spoon_image:
        icon_image_name = "spoon.png"
    elif icon_image == battery_image:
        icon_image_name = "battery.png"
    elif icon_image == star_image:
        icon_image_name = "star.png"
    elif icon_image == potion_image:
        icon_image_name = "potion.png"
    try:
        with open("data.json", "w") as f:
            f.write("{\n")
            # Line 1: spoons
            f.write(f'  "spoons": {json.dumps(spoons)},\n')
            # Line 2: homework_tasks_list
            f.write(f'  "homework_tasks_list": {json.dumps([task_to_serializable(t) for t in homework_tasks_list])},\n')
            # Line 3: chores_tasks_list
            f.write(f'  "chores_tasks_list": {json.dumps([task_to_serializable(t) for t in chores_tasks_list])},\n')
            # Line 4: work_tasks_list
            f.write(f'  "work_tasks_list": {json.dumps([task_to_serializable(t) for t in work_tasks_list])},\n')
            # Line 5: misc_tasks_list
            f.write(f'  "misc_tasks_list": {json.dumps([task_to_serializable(t) for t in misc_tasks_list])},\n')
            # Line 5: exams_tasks_list
            f.write(f'  "exams_tasks_list": {json.dumps([task_to_serializable(t) for t in exams_tasks_list])},\n')
            # Line 5: projects_tasks_list
            f.write(f'  "projects_tasks_list": {json.dumps([task_to_serializable(t) for t in projects_tasks_list])},\n')
            # Line 6: daily_spoons
            f.write(f'  "daily_spoons": {json.dumps(daily_spoons)},\n')
            # Line 7: theme
            f.write(f'  "theme": {json.dumps(theme)},\n')
            # Line 8: icon_image
            f.write(f'  "icon_image": {json.dumps(icon_image_name)},\n')
            # Line 9: spoon_name_input
            f.write(f'  "spoon_name_input": {json.dumps(spoon_name_input)},\n')
            # Line 10: folder names
            f.write(f'  "folder_one": {json.dumps(folder_one)}, "folder_two": {json.dumps(folder_two)},  "folder_three": {json.dumps(folder_three)},  "folder_four": {json.dumps(folder_four)},  "folder_five": {json.dumps(folder_five)},  "folder_six": {json.dumps(folder_six)},\n')
            # Line 11: streak_dates
            f.write(f'  "streak_dates": {json.dumps(streak_dates)}\n')
            f.write("}\n")
    except Exception as e:
        print(f"Error saving data: {e}")

"""
Summary:
    Converts a serializable dictionary format back into a task tuple.

Parameters:
    task (dict): The dictionary representation of the task.

Returns:
    list: A list representation of the task with all fields.
"""

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

"""
Summary:
    Loads the application data from a JSON file.

Parameters:
    None

Returns:
    dict: A dictionary containing the loaded data.
"""

def load_data():
    global spoons, homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list, exams_tasks_list, projects_tasks_list, current_theme, daily_spoons, icon_image, streak_dates

    try:
        with open("data.json", "r") as f:
            data = json.load(f)

            # Task Lists
            spoons = data.get("spoons", 0)
            homework_tasks_list = [task_from_serializable(task) for task in data.get("homework_tasks_list", [])]
            chores_tasks_list = [task_from_serializable(task) for task in data.get("chores_tasks_list", [])]
            work_tasks_list = [task_from_serializable(task) for task in data.get("work_tasks_list", [])]
            misc_tasks_list = [task_from_serializable(task) for task in data.get("misc_tasks_list", [])]
            exams_tasks_list = [task_from_serializable(task) for task in data.get("exams_tasks_list", [])]
            projects_tasks_list = [task_from_serializable(task) for task in data.get("projects_tasks_list", [])]
            print("Tasks loaded successfully")

            # Theme
            loaded_theme = data.get("theme", "")
            
            # Load daily spoons data
            daily_spoons = data.get("daily_spoons", {"Mon": 0, "Tue": 0, "Wed": 0, "Thu": 0, "Fri": 0, "Sat": 0, "Sun": 0}) 

            # Load icon image from filename
            icon_image_name = data.get("icon_image", "spoon.png")
            if icon_image_name == "spoon.png":
                icon_image = spoon_image
            elif icon_image_name == "battery.png":
                icon_image = battery_image 
            elif icon_image_name == "star.png":
                icon_image = star_image
            elif icon_image_name == "potion.png":
                icon_image = potion_image
            else:
                icon_image = spoon_image  # Default fallback

            # Load spoon name input
            spoon_name_input = data.get("spoon_name_input", "Spoons")

            # Load folder names
            folder_one = data.get("folder_one", "Homework")
            folder_two = data.get("folder_two", "Chores")
            folder_three = data.get("folder_three", "Work")
            folder_four = data.get("folder_four", "Misc")
            folder_five = data.get("folder_five", "Exams")
            folder_six = data.get("folder_six", "Projects")

            #load streak data
            streak_dates = data.get("streak_dates", [])


    except Exception as e:
        print(f"Error loading data: {e}")

    return spoons, homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list, exams_tasks_list, projects_tasks_list, daily_spoons, loaded_theme, icon_image, spoon_name_input, folder_one, folder_two, folder_three, folder_four, folder_five, folder_six, streak_dates