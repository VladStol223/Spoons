import json
from datetime import datetime, date
import os
import tempfile
from config import *

"""
Summary:
    Converts a task tuple into a serializable dictionary format.

Parameters:
    task (tuple): The task tuple containing task details.

Returns:
    dict: A dictionary representation of the taskv.
"""
# Internal variable → Generic JSON key
TASK_CATEGORY_JSON_MAP = {
    "homework_tasks_list": "folder_1_tasks",
    "chores_tasks_list": "folder_2_tasks",
    "work_tasks_list": "folder_3_tasks",
    "misc_tasks_list": "folder_4_tasks",
    "exams_tasks_list": "folder_5_tasks",
    "projects_tasks_list": "folder_6_tasks"
}

# Reverse mapping: JSON key → internal variable
TASK_CATEGORY_JSON_REVERSE = {v: k for k, v in TASK_CATEGORY_JSON_MAP.items()}

def task_to_serializable(task):
    """
    Accepts either a tuple/list in legacy formats (5/6/7/8 fields) or a dict.
    Outputs a dict with stable keys.
    """
    if isinstance(task, dict):
        name = task.get("task_name", "")
        spoons_needed = int(task.get("spoons_needed", 0))
        done = int(task.get("done", 0))
        days_left = int(task.get("days_till_due_date", 0))
        due = task.get("due_date", "1970-01-01T00:00:00")
        # keep ISO string if provided; else assume datetime and convert
        if isinstance(due, datetime):
            due_iso = due.isoformat()
        else:
            due_iso = str(due)
        start_time = task.get("start_time", [0,0,0,0])
        end_time   = task.get("end_time",   [0,0,0,0])
        labels     = task.get("labels", [])
        if not isinstance(labels, list): labels = []
        return {
            "task_name": name,
            "spoons_needed": spoons_needed,
            "done": done,
            "days_till_due_date": days_left,
            "due_date": due_iso,
            "start_time": start_time,
            "end_time": end_time,
            "labels": labels
        }

    # tuple/list paths
    t = list(task)
    L = len(t)

    # Common pieces
    name = t[0] if L >= 1 else ""
    spoons_needed = int(t[1]) if L >= 2 else 0
    # default to 0 (int), not "❌"
    done = int(t[2]) if L >= 3 and isinstance(t[2], (int, float)) else 0
    days_left = int(t[3]) if L >= 4 else 0
    due_dt = t[4] if L >= 5 else datetime(1970,1,1)

    # optional bits
    start_time = t[5] if L >= 6 else [0,0,0,0]
    end_time   = t[6] if L >= 7 else [0,0,0,0]
    labels     = t[7] if L >= 8 else []
    if not isinstance(labels, list): labels = []

    # normalize due_date
    if isinstance(due_dt, datetime):
        due_iso = due_dt.isoformat()
    else:
        # if someone stored a date or string, coerce to string
        try:
            due_iso = due_dt.isoformat()  # date has isoformat too
        except Exception:
            due_iso = "1970-01-01T00:00:00"

    return {
        "task_name": name,
        "spoons_needed": spoons_needed,
        "done": done,
        "days_till_due_date": days_left,
        "due_date": due_iso,
        "start_time": start_time,
        "end_time": end_time,
        "labels": labels
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

import os
import tempfile
from datetime import date  # at top alongside datetime import

def save_data(
    spoons, homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list,
    exams_tasks_list, projects_tasks_list, daily_spoons, theme, icon_image,
    spoon_name_input, folder_one, folder_two, folder_three, folder_four,
    folder_five, folder_six, streak_dates,
    border, hubIcons, spoonIcons, restIcons, hotbar, manillaFolder,
    taskBorder, scrollBar, calendarImages, themeBackgroundsImages, intro, label_favorites,
    spoons_used_today, sound_toggle, spoons_debt_toggle, spoons_debt_consequences_toggle):


    # resolve icon file name
    global icon_image_name
    if   icon_image == spoon_image:        icon_image_name = "spoon.png"
    elif icon_image == battery_image:      icon_image_name = "battery.png"
    elif icon_image == star_image:         icon_image_name = "star.png"
    elif icon_image == potion_image:       icon_image_name = "potion.png"
    elif icon_image == yourdidit_image:    icon_image_name = "yourdidit.png"
    elif icon_image == mike_image:         icon_image_name = "mike.png"
    elif icon_image == lightningface_image: icon_image_name = "lightningface.png"
    elif icon_image == diamond_image:      icon_image_name = "diamond.png"
    elif icon_image == starfruit_image:    icon_image_name = "starfruit.png"
    elif icon_image == strawberry_image:   icon_image_name = "strawberry.png"
    elif icon_image == terstar_image:      icon_image_name = "terstar.png"
    elif icon_image == hcheart_image:      icon_image_name = "hcheart.png"
    elif icon_image == beer_image:         icon_image_name = "beer.png"
    elif icon_image == drpepper_image:     icon_image_name = "drpepper.png"
    else:                                  icon_image_name = "spoon.png"

    payload = {
        "spoons": spoons,
        **{
        TASK_CATEGORY_JSON_MAP["homework_tasks_list"]: [task_to_serializable(t) for t in homework_tasks_list],
        TASK_CATEGORY_JSON_MAP["chores_tasks_list"]:   [task_to_serializable(t) for t in chores_tasks_list],
        TASK_CATEGORY_JSON_MAP["work_tasks_list"]:     [task_to_serializable(t) for t in work_tasks_list],
        TASK_CATEGORY_JSON_MAP["misc_tasks_list"]:     [task_to_serializable(t) for t in misc_tasks_list],
        TASK_CATEGORY_JSON_MAP["exams_tasks_list"]:    [task_to_serializable(t) for t in exams_tasks_list],
        TASK_CATEGORY_JSON_MAP["projects_tasks_list"]: [task_to_serializable(t) for t in projects_tasks_list],
    	},
        "daily_spoons": daily_spoons,
        "theme": theme,
        "icon_image": icon_image_name,
        "spoon_name_input": spoon_name_input,
        "folder_one": folder_one,
        "folder_two": folder_two,
        "folder_three": folder_three,
        "folder_four": folder_four,
        "folder_five": folder_five,
        "folder_six": folder_six,
        "assets": {
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
        },
        "label_favorites": label_favorites,
        "last_save_date": [date.today().isoformat(), int(spoons_used_today)],
        # NEW FLAGS
        "sound_toggle": sound_toggle,
        "spoons_debt_toggle": spoons_debt_toggle,
        "spoons_debt_consequences_toggle": spoons_debt_consequences_toggle
    }


    try:
        # atomic write
        dir_name = os.path.dirname(os.path.abspath("data.json"))
        fd, tmp_path = tempfile.mkstemp(prefix="data_", suffix=".json", dir=dir_name)
        with os.fdopen(fd, "w", encoding="utf-8") as tmp:
            json.dump(payload, tmp, ensure_ascii=False, indent=2)
            tmp.flush()
            os.fsync(tmp.fileno())
        os.replace(tmp_path, "data.json")
    except Exception as e:
        print(f"Error saving data: {e}")
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass

"""
Summary:
    Converts a serializable dictionary format back into a task tuple.

Parameters:
    task (dict): The dictionary representation of the task.

Returns:
    list: A list representation of the task with all fields.
"""

def task_from_serializable(task):
    """
    Converts saved dict -> canonical list format used in-app:
    [name, spoons_needed, done, days_left, due_datetime, start_time, end_time, labels]
    """
    name = task.get("task_name", "")
    spoons_needed = int(task.get("spoons_needed", 0))
    # store as int; you compare numerically elsewhere
    done = int(task.get("done", 0))
    days_left = int(task.get("days_till_due_date", 0))

    due_str = task.get("due_date", "1970-01-01T00:00:00")
    # be tolerant of both full seconds and possible microseconds
    due_dt = None
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S.%f"):
        try:
            due_dt = datetime.strptime(due_str, fmt)
            break
        except Exception:
            pass
    if due_dt is None:
        # fallback to "now" if completely unparsable
        due_dt = datetime(1970,1,1)

    start_time = task.get("start_time", [0,0,0,0])
    end_time   = task.get("end_time",   [0,0,0,0])
    labels     = task.get("labels", [])
    if not isinstance(labels, list): labels = []

    return [name, spoons_needed, done, days_left, due_dt, start_time, end_time, labels]

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
    global label_favorites, spoons_used_today
    global sound_toggle, spoons_debt_toggle, spoons_debt_consequences_toggle


    try:
        with open("data.json", "r") as f:
            data = json.load(f)

        # — your existing field loading —
        spoons = data.get("spoons", 0)
        for var_name, json_key in TASK_CATEGORY_JSON_MAP.items():
            globals()[var_name] = [task_from_serializable(t) for t in data.get(json_key, [])]

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

        # NEW FLAGS (default values if missing)
        sound_toggle = data.get("sound_toggle", True)
        spoons_debt_toggle = data.get("spoons_debt_toggle", False)
        spoons_debt_consequences_toggle = data.get("spoons_debt_consequences_toggle", False)

        # last_save_date can be legacy string or new pair ["YYYY-MM-DD", spoons_used_today]
        lsd = data.get("last_save_date")
        spoons_used_today = 0
        if isinstance(lsd, list) and len(lsd) == 2:
            last_save_date = lsd[0]
            try:
                spoons_used_today = int(lsd[1])
            except Exception:
                spoons_used_today = 0
        else:
            last_save_date = lsd

        # NEW: load per-folder favorites (with migration & sane defaults)
        default_slots = ["folder_one", "folder_two", "folder_three", "folder_four", "folder_five", "folder_six"]
        label_favorites = data.get("label_favorites", {})

        # Migrate from legacy flat keys if present (optional, safe)
        legacy_map = {
            "folder_one_Label_favorites":   "folder_one",
            "folder_two_Label_favorites":   "folder_two",
            "folder_three_Label_favorites": "folder_three",
            "folder_four_Label_favorites":  "folder_four",
            "folder_five_Label_favorites":  "folder_five",
            "folder_six_Label_favorites":   "folder_six",
        }
        for legacy_key, slot in legacy_map.items():
            if legacy_key in data and slot not in label_favorites:
                v = data.get(legacy_key, [])
                label_favorites[slot] = v if isinstance(v, list) else []

        # Ensure all slots exist with lists
        for slot in default_slots:
            if slot not in label_favorites or not isinstance(label_favorites[slot], list):
                label_favorites[slot] = []

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
        calendarImages_name, themeBackgroundsImages_name, intro_name, label_favorites,
        last_save_date, spoons_used_today, sound_toggle, spoons_debt_toggle, spoons_debt_consequences_toggle
    )
