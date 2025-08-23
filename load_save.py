import json
import datetime
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
    if len(task) == 8 or len(task) == 7:  # Task has start_time and end_time
        task_name, spoons_needed, done, days_till_due_date, due_date, start_time, end_time, labels = task
        return {
            "task_name": task_name,
            "spoons_needed": spoons_needed,
            "done": done,
            "days_till_due_date": days_till_due_date,
            "due_date": due_date.isoformat(),
            "start_time": start_time,
            "end_time": end_time,
            "labels": labels if isinstance(labels, list) else []
        }
    elif len(task) == 5:  # Task without start_time and end_time
        task_name, spoons_needed, done, days_till_due_date, due_date, labels = task
        return {
            "task_name": task_name,
            "spoons_needed": spoons_needed,
            "done": done,
            "days_till_due_date": days_till_due_date,
            "due_date": due_date.isoformat(),
            "labels": labels if isinstance(labels, list) else []
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

def save_data(
    spoons, homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list,
    exams_tasks_list, projects_tasks_list, daily_spoons, theme, icon_image,
    spoon_name_input, folder_one, folder_two, folder_three, folder_four,
    folder_five, folder_six, streak_dates,
    border, hubIcons, spoonIcons, restIcons, hotbar, manillaFolder,
    taskBorder, scrollBar, calendarImages, themeBackgroundsImages, intro,
    level, coins):
    
    global icon_image_name
    if icon_image == spoon_image:
        icon_image_name = "spoon.png"
    elif icon_image == battery_image:
        icon_image_name = "battery.png"
    elif icon_image == star_image:
        icon_image_name = "star.png"
    elif icon_image == potion_image:
        icon_image_name = "potion.png"
    elif icon_image == yourdidit_image:
        icon_image_name = "yourdidit.png"
    elif icon_image == mike_image:
        icon_image_name = "mike.png"
    elif icon_image == lightningface_image:
        icon_image_name = "lightningface.png"
    elif icon_image == diamond_image:
        icon_image_name = "diamond.png"
    elif icon_image == starfruit_image:
        icon_image_name = "starfruit.png"
    elif icon_image == strawberry_image:
        icon_image_name = "strawberry.png"
    elif icon_image == terstar_image:
        icon_image_name = "terstar.png"
    elif icon_image == hcheart_image:
        icon_image_name = "hcheart.png"
    elif icon_image == beer_image:
        icon_image_name = "beer.png"
    elif icon_image == drpepper_image:
        icon_image_name = "drpepper.png"

    try:
        with open("data.json", "w") as f:
            f.write("{\n")
            f.write(f'  "spoons": {json.dumps(spoons)},\n')
            f.write(f'  "homework_tasks_list": {json.dumps([task_to_serializable(t) for t in homework_tasks_list])},\n')
            f.write(f'  "chores_tasks_list": {json.dumps([task_to_serializable(t) for t in chores_tasks_list])},\n')
            f.write(f'  "work_tasks_list": {json.dumps([task_to_serializable(t) for t in work_tasks_list])},\n')
            f.write(f'  "misc_tasks_list": {json.dumps([task_to_serializable(t) for t in misc_tasks_list])},\n')
            f.write(f'  "exams_tasks_list": {json.dumps([task_to_serializable(t) for t in exams_tasks_list])},\n')
            f.write(f'  "projects_tasks_list": {json.dumps([task_to_serializable(t) for t in projects_tasks_list])},\n')
            f.write(f'  "daily_spoons": {json.dumps(daily_spoons)},\n')
            f.write(f'  "theme": {json.dumps(theme)},\n')
            f.write(f'  "icon_image": {json.dumps(icon_image_name)},\n')
            f.write(f'  "spoon_name_input": {json.dumps(spoon_name_input)},\n')
            f.write(
                f'  "folder_one": {json.dumps(folder_one)}, "folder_two": {json.dumps(folder_two)}, '
                f'"folder_three": {json.dumps(folder_three)}, "folder_four": {json.dumps(folder_four)}, '
                f'"folder_five": {json.dumps(folder_five)}, "folder_six": {json.dumps(folder_six)},\n'
            )
            # streak_dates now with a trailing comma
            f.write(f'  "streak_dates": {json.dumps(streak_dates)},\n')
            # all the rest in one line under "assets"
            f.write(
                '  "assets": ' +
                json.dumps({
                    "border": border,
                    "hubIcons": hubIcons,
                    "spoonIcons": spoonIcons,
                    "restIcons": restIcons,
                    "hotbar": hotbar,
                    "manillaFolder": manillaFolder,
                    "taskBorder": taskBorder,
                    "scrollBar": scrollBar,
                    "calendarImages": calendarImages,
                    "themeBackgrounds": themeBackgroundsImages,
                    "intro": intro
                }) +
                ",\n"
            )
            f.write(f'  "level": {json.dumps(level)},\n')
            f.write(f'  "coins": {json.dumps(coins)}\n')
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
    labels = task.get("labels", [])
    if not isinstance(labels, list): labels = []

    # Return the task as a list with all fields
    return [task_name, spoons_needed, done, days_till_due_date, due_date, start_time, end_time, labels]

"""
Summary:
    Loads the application data from a JSON file.

Parameters:
    None

Returns:
    dict: A dictionary containing the loaded data.
"""

def load_data():
    global spoons, homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list
    global exams_tasks_list, projects_tasks_list, current_theme, daily_spoons, icon_image
    global spoon_name_input, folder_one, folder_two, folder_three, folder_four
    global folder_five, folder_six, streak_dates
    global border, hubIcons, spoonIcons, restIcons, hotbar, manillaFolder
    global taskBorder, scrollBar, calendarImages, themeBackgroundsImages, intro
    # globals for asset names
    global border_name, hubIcons_name, spoonIcons_name, restIcons_name
    global hotbar_name, manillaFolder_name, taskBorder_name, scrollBar_name
    global calendarImages_name, themeBackgroundsImages_name, intro_name
    global level, coins

    try:
        with open("data.json", "r") as f:
            data = json.load(f)

        # — your existing field loading —
        spoons = data.get("spoons", 0)
        homework_tasks_list = [task_from_serializable(t) for t in data.get("homework_tasks_list", [])]
        chores_tasks_list   = [task_from_serializable(t) for t in data.get("chores_tasks_list", [])]
        work_tasks_list     = [task_from_serializable(t) for t in data.get("work_tasks_list", [])]
        misc_tasks_list     = [task_from_serializable(t) for t in data.get("misc_tasks_list", [])]
        exams_tasks_list    = [task_from_serializable(t) for t in data.get("exams_tasks_list", [])]
        projects_tasks_list = [task_from_serializable(t) for t in data.get("projects_tasks_list", [])]

        daily_spoons = data.get("daily_spoons", {"Mon":0,"Tue":0,"Wed":0,"Thu":0,"Fri":0,"Sat":0,"Sun":0})
        loaded_theme = data.get("theme", "")

        # icon_image mapping…
        icon_image_name = data.get("icon_image","spoon.png")
        if   icon_image_name=="spoon.png":       icon_image=spoon_image
        elif icon_image_name=="battery.png":     icon_image=battery_image
        elif icon_image_name=="star.png":        icon_image=star_image
        elif icon_image_name=="potion.png":      icon_image=potion_image
        elif icon_image_name=="yourdidit.png":   icon_image=yourdidit_image
        elif icon_image_name=="mike.png":        icon_image=mike_image
        elif icon_image_name=="lightningface.png": icon_image=lightningface_image
        elif icon_image_name=="diamond.png":     icon_image=diamond_image
        elif icon_image_name=="starfruit.png":   icon_image=starfruit_image
        elif icon_image_name=="strawberry.png":  icon_image=strawberry_image
        elif icon_image_name=="terstar.png":     icon_image=terstar_image
        elif icon_image_name=="hcheart.png":     icon_image=hcheart_image
        elif icon_image_name=="beer.png":        icon_image=beer_image
        elif icon_image_name=="drpepper.png":    icon_image=drpepper_image
        else:                                    icon_image=spoon_image

        spoon_name_input = data.get("spoon_name_input","Spoons")
        folder_one   = data.get("folder_one","Homework")
        folder_two   = data.get("folder_two","Chores")
        folder_three = data.get("folder_three","Work")
        folder_four  = data.get("folder_four","Misc")
        folder_five  = data.get("folder_five","Exams")
        folder_six   = data.get("folder_six","Projects")

        streak_dates = data.get("streak_dates", [])

        level = data.get("level", 0)
        coins = data.get("coins", 0)

        # now only overwrite your asset‐images if they exist in JSON
        assets = data.get("assets", {})

        # — border
        border_name = assets.get("border")
        if border_name:
            border, border_name = set_image('border', border_name)

        # — hub icons
        hubIcons_name = assets.get("hubIcons")
        if hubIcons_name:
            hubIcons, hubIcons_name = set_image('hubIcons', hubIcons_name)

        # — spoon icons
        spoonIcons_name = assets.get("spoonIcons")
        if spoonIcons_name:
            spoonIcons, spoonIcons_name = set_image('spoonIcons', spoonIcons_name)

        # — rest icons
        restIcons_name = assets.get("restIcons")
        if restIcons_name:
            restIcons, restIcons_name = set_image('restIcons', restIcons_name)

        # — hotbar icons
        hotbar_name = assets.get("hotbar")
        if hotbar_name:
            hotbar, hotbar_name = set_image('hotbar', hotbar_name)

        # — manilla folder icons
        manillaFolder_name = assets.get("manillaFolder")
        if manillaFolder_name:
            manillaFolder, manillaFolder_name = set_image('manillaFolder', manillaFolder_name)

        # — task border pieces
        taskBorder_name = assets.get("taskBorder")
        if taskBorder_name:
            taskBorder, taskBorder_name = set_image('taskBorder', taskBorder_name)

        # — scroll bar pieces
        scrollBar_name = assets.get("scrollBar")
        if scrollBar_name:
            scrollBar, scrollBar_name = set_image('scrollBar', scrollBar_name)

        # — calendar misc icons
        calendarImages_name = assets.get("calendarImages")
        if calendarImages_name:
            calendarImages, calendarImages_name = set_image('calendarImages', calendarImages_name)

        # — theme backgrounds
        themeBackgroundsImages_name = assets.get("themeBackgroundsImages")
        if themeBackgroundsImages_name:
            themeBackgroundsImages, themeBackgroundsImages_name = set_image('themeBackgroundsImages', themeBackgroundsImages_name)

        # — intro/logo
        intro_name = assets.get("intro")
        if intro_name:
            intro, intro_name = set_image('intro', intro_name)

    except Exception as e:
        print(f"Error loading data: {e}")

    return (
        spoons, homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list,
        exams_tasks_list, projects_tasks_list, daily_spoons, loaded_theme, icon_image,
        spoon_name_input, folder_one, folder_two, folder_three, folder_four,
        folder_five, folder_six, streak_dates,
        border, hubIcons, spoonIcons, restIcons, hotbar, manillaFolder,
        taskBorder, scrollBar, calendarImages, themeBackgroundsImages, intro,
        border_name, hubIcons_name, spoonIcons_name, restIcons_name,
        hotbar_name, manillaFolder_name, taskBorder_name, scrollBar_name,
        calendarImages_name, themeBackgroundsImages_name, intro_name,
        level, coins
    )
