from config import *

from drawing_functions.draw_rounded_button import draw_rounded_button
from drawing_functions.draw_input_box import draw_input_box
import importlib
draw_complete_tasks_folders = importlib.import_module("drawing_functions.draw_complete_tasks_folders").draw_complete_tasks_folders
ctf_mod = importlib.import_module("drawing_functions.draw_complete_tasks_folders")


import pygame
import math
from datetime import datetime, timedelta

current_spoons = ""

# [name, spoons, completed, days_left, due_date, start_time, end_time, labels]
IDX_NAME = 0; IDX_SPOONS = 1; IDX_COMPLETED = 2; IDX_DAYS_LEFT = 3; IDX_DUE_DATE = 4; IDX_START_TIME = 5; IDX_END_TIME = 6; IDX_LABELS = 7


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

# Max width equals the width of the reference string using the same font as your task input
TASK_NAME_REF = "thisisthecharacterlim"
MAX_TASK_PIXEL_WIDTH = font.size(TASK_NAME_REF)[0]  # uses your existing `font`

layout_heights = {
    "task_label":                  0.28,    # “Enter task name:”
    "task_input_line":             0.35,   # y=195/600
    "due_date_label":              0.51,   # “Enter due date:” & “Enter Start date:”
    "due_date_input_line":         0.58,   # y=305/600
    "spoons_label":                0.74,   # “Enter spoons needed:”
    "spoons_input_line":           0.81,   # y=420/600

    "time_toggle_label":           0.100,   # y=60/600

    "repetitions_amount_label":    0.65,   # “Repetitions:”
    "repetitions_input_line":      0.70,   # y=420/600
    "how_long_label":              0.538,   # “How Long:”
    "how_long_input_line":         0.583,   # y=290/600
}

def draw_input_tasks(screen, spoons, current_task, current_spoons, input_active, 
                     folder, task_month, task_day, time_toggle_on, recurring_toggle_on,
                     start_time, end_time, done_button_color, background_color,
                     add_tasks_choose_folder_color, add_tasks_chosen_folder_color,
                     icon_image, spoon_name_input, task_how_often, task_how_long,
                     task_repetitions_amount, folder_one, folder_two,
                     folder_three, folder_four, folder_five, folder_six
                     , homework_tasks_list,chores_tasks_list, work_tasks_list, misc_tasks_list, exams_tasks_list, projects_tasks_list, manillaFolder):
    global month_typed, day_typed, caret_task, caret_month, caret_day, caret_spoons

    if isinstance(current_spoons, int):
        display_spoons = "" if current_spoons == 0 else str(current_spoons)
    else:
        display_spoons = current_spoons

    screen_h = screen.get_height()
    y_pos = {k: int(v * screen_h) for k, v in layout_heights.items()}

    r, g, b = background_color
    folder_list = ["homework", "chores", "work", "misc", "exams", "projects"]
    done_button_y_pos = 144 + 60 * folder_list.index(folder)

    done_button_color     = tuple(max(0,  c - 20) for c in (r, g, b))
    due_date_infill_color = tuple(min(255, c + 20) for c in (r, g, b))

    task_input_box = pygame.Rect(250, y_pos["task_input_line"], 300, 50)
    spoon_input_box = pygame.Rect(375, y_pos["spoons_input_line"], 50, 50)
    done_button       = pygame.Rect(630, done_button_y_pos,50, 32)
    arrow_points = [(done_button.right, done_button.top - 10),(done_button.right + 30, done_button.centery),(done_button.right, done_button.bottom + 10)]

    recurring_toggle_button = pygame.Rect(760, 50, 40, 40)

    how_often_input_box          = pygame.Rect(410, y_pos["due_date_input_line"], 120, 50)
    how_often_up_button          = pygame.Rect(510, int(y_pos["due_date_input_line"] + 7), 15, 15)
    how_often_down_button        = pygame.Rect(510, int(y_pos["due_date_input_line"] + 7), 15, 15)

    how_long_input_box           = pygame.Rect(555, y_pos["how_long_input_line"], 115, 30)
    how_long_up_button           = pygame.Rect(650, int(y_pos["due_date_input_line"] - 7), 15, 15)
    how_long_down_button         = pygame.Rect(650, int(y_pos["due_date_input_line"] - 7), 15, 15)

    repetitions_amount_input_box = pygame.Rect(555, y_pos["repetitions_input_line"], 115, 30)
    repetitions_amount_up_button = pygame.Rect(650, y_pos["repetitions_input_line"] + 0, 15, 15)
    repetitions_amount_down_button = pygame.Rect(650, y_pos["repetitions_input_line"] + 15, 15, 15)

    month_input_box_normal = pygame.Rect(280, y_pos["due_date_input_line"], 160, 50)
    month_up_button_normal = pygame.Rect(420, int(y_pos["due_date_input_line"] + 7), 15, 15)
    month_down_button_normal = pygame.Rect(420, int(y_pos["due_date_input_line"] + 25), 15, 15)
    day_input_box_normal   = pygame.Rect(465, y_pos["due_date_input_line"], 70, 50)
    day_up_button_normal   = pygame.Rect(515, int(y_pos["due_date_input_line"] + 7), 15, 15)
    day_down_button_normal = pygame.Rect(515, int(y_pos["due_date_input_line"] + 25), 15, 15)

    month_input_box_recurring_shifted = pygame.Rect(150, y_pos["due_date_input_line"], 160, 50)
    month_up_button_recurring_shifted = pygame.Rect(290, int(y_pos["due_date_input_line"] + 7), 15, 15)
    month_down_button_recurring_shifted = pygame.Rect(290, int(y_pos["due_date_input_line"] + 25), 15, 15)
    day_input_box_recurring_shifted   = pygame.Rect(325, y_pos["due_date_input_line"], 70, 50)
    day_up_button_recurring_shifted   = pygame.Rect(375, int(y_pos["due_date_input_line"] + 7), 15, 15)
    day_down_button_recurring_shifted = pygame.Rect(375, int(y_pos["due_date_input_line"] + 25), 15, 15)

    draw_complete_tasks_folders(screen,folder,folder_one,folder_two,folder_three,folder_four,folder_five,folder_six, homework_tasks_list,chores_tasks_list, work_tasks_list, misc_tasks_list, exams_tasks_list, projects_tasks_list, manillaFolder)

    # Draw the boxes as before
    draw_input_box(screen, task_input_box, input_active == "task", current_task, DARK_SLATE_GRAY, DARK_SLATE_GRAY, False, background_color, "light")
    draw_input_box(screen, spoon_input_box, input_active == "spoons", display_spoons, DARK_SLATE_GRAY, DARK_SLATE_GRAY, True, background_color, "light")

    # Overlay a blinking caret for Task / Spoons when active

    if input_active == "task" and _caret_visible():
        left = current_task[:max(0, min(caret_task, len(current_task)))]
        x0, y0 = task_input_box.x + 10, task_input_box.y + 8
        cx = _caret_x(font, left, x0) - 5  # nudge left
        cx = min(cx, task_input_box.right - 6)
        pygame.draw.line(screen, LIGHT_GRAY, (cx, y0), (cx, y0 + font.get_height()), 2)

    if input_active == "spoons" and _caret_visible():
        # The spoons text is centered by draw_input_box (we passed True), so anchor the caret
        # from the centered text start rather than the left padding.
        text = display_spoons if isinstance(display_spoons, str) else str(display_spoons)
        # compute the left edge of centered text
        text_w = font.size(text)[0]
        start_x = spoon_input_box.x + (spoon_input_box.width - text_w) // 2
        y0 = spoon_input_box.y + 8
        left = text[:max(0, min(caret_spoons, len(text)))]
        cx = _caret_x(font, left, start_x)  # nudge left
        cx = min(max(cx, spoon_input_box.x + 4), spoon_input_box.right - 6)
        pygame.draw.line(screen, LIGHT_GRAY, (cx, y0), (cx, y0 + font.get_height()), 2)

    arrow   = font.render(">", True, done_button_color)
    up_arrow = pygame.transform.rotate(arrow, 90)
    down_arrow = pygame.transform.rotate(arrow, 270)

    def _render_month_box(active, rect, month_num):
        global caret_month
        pygame.draw.rect(screen, background_color if recurring_toggle_on else due_date_infill_color, rect, 0)
        draw_input_box(screen, rect, active, "", DARK_SLATE_GRAY, DARK_SLATE_GRAY, False, background_color, "light")
        x0, y0 = rect.x + 10, rect.y + 8
        if active:
            base = month_typed
            suffix = _month_suffix(month_typed, months)
            txt1 = font.render(base, True, LIGHT_GRAY)
            screen.blit(txt1, (x0, y0))
            if suffix:
                txt2 = font.render(suffix, True, (170,170,170))
                screen.blit(txt2, (x0 + txt1.get_width(), y0))
            if _caret_visible():
                left = base[:max(0, min(caret_month, len(base)))]
                cx = _caret_x(font, left, x0)
                pygame.draw.line(screen, LIGHT_GRAY, (cx, y0), (cx, y0 + font.get_height()), 2)
        else:
            label = months[month_num - 1]
            txt = font.render(label, True, BLACK)
            screen.blit(txt, (x0, y0))


    def _render_day_box(active, rect, day_value):
        global caret_day
        pygame.draw.rect(screen, background_color if recurring_toggle_on else due_date_infill_color, rect, 0)
        draw_input_box(screen, rect, active, "", DARK_SLATE_GRAY, DARK_SLATE_GRAY, False, background_color, "light")
        x0, y0 = rect.x + 10, rect.y + 8
        if active:
            disp = day_typed
            txt = font.render(disp, True, LIGHT_GRAY)
            screen.blit(txt, (x0, y0))
            if _caret_visible():
                left = disp[:max(0, min(caret_day, len(disp)))]
                cx = _caret_x(font, left, x0)
                pygame.draw.line(screen, LIGHT_GRAY, (cx, y0), (cx, y0 + font.get_height()), 2)
        else:
            txt = font.render(str(day_value), True, BLACK)
            screen.blit(txt, (x0, y0))

    if recurring_toggle_on:
        screen.blit(font.render("Enter Start date:", True, WHITE),(170, y_pos["due_date_label"]))
        _render_month_box(input_active == "month", month_input_box_recurring_shifted, task_month)
        _render_day_box(input_active == "day", day_input_box_recurring_shifted, int(task_day))
        for btn in (month_up_button_recurring_shifted,month_down_button_recurring_shifted,day_up_button_recurring_shifted,day_down_button_recurring_shifted):
            pygame.draw.rect(screen, background_color, btn)
        screen.blit(up_arrow,   (month_up_button_recurring_shifted.x, month_up_button_recurring_shifted.y - 7))
        screen.blit(down_arrow, (month_down_button_recurring_shifted.x, month_down_button_recurring_shifted.y - 7))
        screen.blit(up_arrow,   (day_up_button_recurring_shifted.x, day_up_button_recurring_shifted.y - 7))
        screen.blit(down_arrow, (day_down_button_recurring_shifted.x, day_down_button_recurring_shifted.y - 7))

        screen.blit(font.render("How Often:", True, WHITE), (395, y_pos["due_date_input_line"]))
        draw_input_box(screen, how_often_input_box, False, f"{task_how_often} days", GREEN, LIGHT_GRAY, False, background_color, "light")
        pygame.draw.rect(screen, background_color, how_often_up_button); pygame.draw.rect(screen, background_color, how_often_down_button)
        screen.blit(up_arrow,   (how_often_up_button.x, how_often_up_button.y - 7)); screen.blit(down_arrow, (how_often_down_button.x, how_often_down_button.y - 7))

        screen.blit(small_font.render("How Long:", True, WHITE),(560, y_pos["how_long_label"]))
        draw_input_box(screen, how_long_input_box, False, f"{task_how_long} weeks", GREEN, LIGHT_GRAY, False, background_color, "light")
        pygame.draw.rect(screen, background_color, how_long_up_button); pygame.draw.rect(screen, background_color, how_long_down_button)
        screen.blit(up_arrow,   (how_long_up_button.x, how_long_up_button.y - 7)); screen.blit(down_arrow, (how_long_down_button.x, how_long_down_button.y - 7))

        screen.blit(small_font.render("Repetitions:", True, WHITE), (552, y_pos["repetitions_amount_label"]))
        draw_input_box(screen, repetitions_amount_input_box, False, f"{task_repetitions_amount} times", GREEN, LIGHT_GRAY, False, background_color, "light")
        pygame.draw.rect(screen, background_color, repetitions_amount_up_button); pygame.draw.rect(screen, background_color, repetitions_amount_down_button)
        screen.blit(up_arrow,   (repetitions_amount_up_button.x, repetitions_amount_up_button.y - 7)); screen.blit(down_arrow, (repetitions_amount_down_button.x, repetitions_amount_down_button.y - 7))

        screen.blit(small_font.render("Remove Recurring Task", True, WHITE), (recurring_toggle_button.x - 280, y_pos["time_toggle_label"]))
    else:
        screen.blit(font.render("Due Date:", True, WHITE),(345, y_pos["due_date_label"]))
        _render_month_box(input_active == "month", month_input_box_normal, task_month)
        _render_day_box(input_active == "day", day_input_box_normal, int(task_day))
        for btn in (month_up_button_normal, month_down_button_normal, day_up_button_normal, day_down_button_normal):
            pygame.draw.rect(screen, due_date_infill_color, btn)
        screen.blit(up_arrow,   (month_up_button_normal.x - 9, month_up_button_normal.y))
        screen.blit(down_arrow, (month_down_button_normal.x - 12, month_down_button_normal.y))
        screen.blit(up_arrow,   (day_up_button_normal.x - 9, day_up_button_normal.y))
        screen.blit(down_arrow, (day_down_button_normal.x - 12, day_down_button_normal.y))

    screen.blit(font.render("Task Name:", True, WHITE),(335, y_pos["task_label"]))
    screen.blit(font.render("Spoons:", True, WHITE),(360, y_pos["spoons_label"]))
    pygame.draw.rect(screen, done_button_color, done_button)
    pygame.draw.polygon(screen, done_button_color, arrow_points)
    screen.blit(font.render("Add", True, BLACK),(done_button.x + 15, done_button.y + 2))



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

# --- Inline edit buffers & carets ---
month_typed = ""
day_typed = ""
caret_task = 0
caret_month = 0
caret_day = 0
caret_spoons = 0
def _caret_visible(): return (pygame.time.get_ticks() // 500) % 2 == 0
def _caret_x(font_obj, text, start_x): return start_x + font_obj.size(text)[0]
def _index_from_click(font_obj, text, click_x, start_x):
    x = start_x
    for i, ch in enumerate(text):
        w = font_obj.size(ch)[0]
        if click_x < x + w / 2.0: return i
        x += w
    return len(text)


# --- Helpers ---
def _month_from_typed(typed, months_list):
    if not typed: return None
    t = typed.lower()
    matches = [i for i, m in enumerate(months_list) if m.lower().startswith(t)]
    if len(matches) == 1: return matches[0] + 1  # 1-based month
    # exact match still OK
    exact = [i for i, m in enumerate(months_list) if m.lower() == t]
    if len(exact) == 1: return exact[0] + 1
    return None

def _month_suffix(typed, months_list):
    mnum = _month_from_typed(typed, months_list)
    if not mnum: return ""
    full = months_list[mnum - 1]
    return full[len(typed):] if len(typed) < len(full) else ""

def _commit_month(global_state, task_month, months_list):
    mnum = _month_from_typed(global_state["month_typed"], months_list)
    if mnum:
        task_month = mnum
    global_state["month_typed"] = ""
    return task_month

def _commit_day(global_state, task_day, max_days):
    txt = global_state["day_typed"]
    if txt.isdigit():
        val = max(1, min(int(txt), max_days))
        task_day = val
    global_state["day_typed"] = ""
    return task_day

def _add_task_entry(current_task, current_spoons, folder, task_date, current_time, lists_tuple, recurring_toggle_on, task_how_often, task_how_long, task_repetitions_amount):
    (homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list, exams_tasks_list, projects_tasks_list) = lists_tuple
    days_till_due = (task_date - current_time).days + 1
    def _push(entry):
        if folder == "homework": homework_tasks_list.append(entry)
        elif folder == "chores": chores_tasks_list.append(entry)
        elif folder == "work": work_tasks_list.append(entry)
        elif folder == "misc": misc_tasks_list.append(entry)
        elif folder == "exams": exams_tasks_list.append(entry)
        elif folder == "projects": projects_tasks_list.append(entry)

    if recurring_toggle_on:
        for i in range(task_repetitions_amount):
            actual_date = task_date + timedelta(days=i * task_how_often)
            days_left = (actual_date - current_time).days + 1
            _push([current_task, int(current_spoons), 0, days_left, actual_date, [0,0,0,0], [0,0,0,0], []])
    else:
        _push([current_task, int(current_spoons), 0, days_till_due, task_date, [0,0,0,0], [0,0,0,0], []])


def logic_input_tasks(event,screen,current_task,current_spoons,folder,task_month,task_day,task_how_often,task_how_long,task_repetitions_amount,recurring_toggle_on,max_days,input_active,homework_tasks_list,chores_tasks_list,work_tasks_list,misc_tasks_list,exams_tasks_list,projects_tasks_list):
    global month_typed, day_typed, caret_task, caret_month, caret_day, caret_spoons

    page = "input_tasks"
    screen_h = screen.get_height()
    y_pos = {k: int(v * screen_h) for k, v in layout_heights.items()}

    folder_list = ["homework", "chores", "work", "misc", "exams", "projects"]
    done_button_y_pos = 144 + 60 * folder_list.index(folder)

    task_input_box = pygame.Rect(250, y_pos["task_input_line"], 300, 50)
    spoon_input_box = pygame.Rect(375, y_pos["spoons_input_line"], 50, 50)
    done_button       = pygame.Rect(630, done_button_y_pos,50, 32)

    recurring_toggle_button = pygame.Rect(760, 50, 40, 40)

    how_often_input_box          = pygame.Rect(410, y_pos["due_date_input_line"], 120, 50)
    how_often_up_button          = pygame.Rect(510, int(y_pos["due_date_input_line"] + 7), 15, 15)
    how_often_down_button        = pygame.Rect(510, int(y_pos["due_date_input_line"] + 7), 15, 15)

    how_long_input_box           = pygame.Rect(555, y_pos["how_long_input_line"], 115, 30)
    how_long_up_button           = pygame.Rect(650, int(y_pos["due_date_input_line"] - 7), 15, 15)
    how_long_down_button         = pygame.Rect(650, int(y_pos["due_date_input_line"] - 7), 15, 15)

    repetitions_amount_input_box = pygame.Rect(555, y_pos["repetitions_input_line"], 115, 30)
    repetitions_amount_up_button = pygame.Rect(650, y_pos["repetitions_input_line"] + 0, 15, 15)
    repetitions_amount_down_button = pygame.Rect(650, y_pos["repetitions_input_line"] + 15, 15, 15)

    month_input_box_normal = pygame.Rect(280, y_pos["due_date_input_line"], 160, 50)
    month_up_button_normal = pygame.Rect(420, int(y_pos["due_date_input_line"] + 7), 15, 15)
    month_down_button_normal = pygame.Rect(420, int(y_pos["due_date_input_line"] + 25), 15, 15)
    day_input_box_normal   = pygame.Rect(465, y_pos["due_date_input_line"], 70, 50)
    day_up_button_normal   = pygame.Rect(515, int(y_pos["due_date_input_line"] + 7), 15, 15)
    day_down_button_normal = pygame.Rect(515, int(y_pos["due_date_input_line"] + 25), 15, 15)

    month_input_box_recurring_shifted = pygame.Rect(150, y_pos["due_date_input_line"], 160, 50)
    month_up_button_recurring_shifted = pygame.Rect(290, int(y_pos["due_date_input_line"] + 7), 15, 15)
    month_down_button_recurring_shifted = pygame.Rect(290, int(y_pos["due_date_input_line"] + 25), 15, 15)
    day_input_box_recurring_shifted   = pygame.Rect(325, y_pos["due_date_input_line"], 70, 50)
    day_up_button_recurring_shifted   = pygame.Rect(375, int(y_pos["due_date_input_line"] + 7), 15, 15)
    day_down_button_recurring_shifted = pygame.Rect(375, int(y_pos["due_date_input_line"] + 25), 15, 15)

    def _active_month_rect():
        return month_input_box_recurring_shifted if recurring_toggle_on else month_input_box_normal

    def _active_day_rect():
        return day_input_box_recurring_shifted if recurring_toggle_on else day_input_box_normal

    if event.type == pygame.MOUSEBUTTONDOWN:
        if recurring_toggle_button.collidepoint(event.pos):
            # Commit any in-progress edits before toggling
            if input_active == "month":
                task_month = _commit_month({"month_typed": month_typed}, task_month, months); month_typed = ""
            if input_active == "day":
                task_day = _commit_day({"day_typed": day_typed}, task_day, max_days); day_typed = ""
            recurring_toggle_on = not recurring_toggle_on

        # --- 1) SPINNER BUTTONS FIRST (so they don't trigger edit mode) ---
        clicked_spinner = False
        if recurring_toggle_on:
            if month_up_button_recurring_shifted.collidepoint(event.pos):
                task_month = task_month + 1 if task_month < 12 else 1
                clicked_spinner = True
            elif month_down_button_recurring_shifted.collidepoint(event.pos):
                task_month = task_month - 1 if task_month > 1 else 12
                clicked_spinner = True
            elif day_up_button_recurring_shifted.collidepoint(event.pos):
                task_day = int(task_day) + 1 if int(task_day) < max_days else 1
                clicked_spinner = True
            elif day_down_button_recurring_shifted.collidepoint(event.pos):
                task_day = int(task_day) - 1 if int(task_day) > 1 else max_days
                clicked_spinner = True
        else:
            if month_up_button_normal.collidepoint(event.pos):
                task_month = task_month + 1 if task_month < 12 else 1
                clicked_spinner = True
            elif month_down_button_normal.collidepoint(event.pos):
                task_month = task_month - 1 if task_month > 1 else 12
                clicked_spinner = True
            elif day_up_button_normal.collidepoint(event.pos):
                task_day = int(task_day) + 1 if int(task_day) < max_days else 1
                clicked_spinner = True
            elif day_down_button_normal.collidepoint(event.pos):
                task_day = int(task_day) - 1 if int(task_day) > 1 else max_days
                clicked_spinner = True

        # If the user clicked a spinner, don't enter edit mode or clear typed buffers
        if clicked_spinner:
            pass
        else:
            # --- 2) EDIT HITBOXES (trim right edge so clicks near arrows don't focus) ---
            month_rect_full = _active_month_rect()
            day_rect_full   = _active_day_rect()

            # shrink only the RIGHT side (e.g., 24px for month, 20px for day)
            month_rect_edit = month_rect_full.copy(); month_rect_edit.width = max(10, month_rect_edit.width - 24)
            day_rect_edit   = day_rect_full.copy();  day_rect_edit.width   = max(10, day_rect_edit.width   - 20)

            # Click into inputs (set focus + caret)
            if task_input_box.collidepoint(event.pos):
                input_active = "task"
                caret_task = _index_from_click(font, current_task, event.pos[0], task_input_box.x + 10)
            elif month_rect_edit.collidepoint(event.pos):
                input_active = "month"
                caret_month = _index_from_click(font, month_typed, event.pos[0], month_rect_full.x + 10)
            elif day_rect_edit.collidepoint(event.pos):
                input_active = "day"
                caret_day = _index_from_click(font, day_typed, event.pos[0], day_rect_full.x + 10)
            elif spoon_input_box.collidepoint(event.pos):
                input_active = "spoons"
                if isinstance(current_spoons, int): current_spoons = ""
                caret_spoons = _index_from_click(font, current_spoons, event.pos[0], spoon_input_box.x + 10)
            else:
                # Clicking elsewhere commits month/day edits if active
                if input_active == "month":
                    task_month = _commit_month({"month_typed": month_typed}, task_month, months); month_typed = ""; input_active = False
                elif input_active == "day":
                    task_day = _commit_day({"day_typed": day_typed}, task_day, max_days); day_typed = ""; input_active = False

        # Recurrence controls (unchanged math)
        if how_often_up_button.collidepoint(event.pos):
            new_val = task_how_often + 1; task_how_often = max(1, new_val)
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

        # Add task on click
        if done_button.collidepoint(event.pos):
            if current_task and current_spoons:
                task_date = datetime(current_time.year, task_month, int(task_day))
                _add_task_entry(
                    current_task, current_spoons, folder, task_date, current_time,
                    (homework_tasks_list,chores_tasks_list,work_tasks_list,misc_tasks_list,exams_tasks_list,projects_tasks_list),
                    recurring_toggle_on, task_how_often, task_how_long, task_repetitions_amount
                )
                current_task = ""; current_spoons = ""; input_active = False; month_typed = ""; day_typed = ""

        # Folder selection (unchanged)
        for f_key, rect in reversed(ctf_mod.folder_rects):
            if rect.collidepoint(event.pos):
                folder = f_key
                break


    if event.type == pygame.KEYDOWN:
        # ↑/↓ change the selected folder (wrap-around)
        if event.key in (pygame.K_UP, pygame.K_DOWN):
            idx = folder_list.index(folder) if folder in folder_list else 0
            step = -1 if event.key == pygame.K_UP else 1
            folder = folder_list[(idx + step) % len(folder_list)]

        # Tab order: task -> month -> day -> spoons -> task
        tab_order = ["task","month","day","spoons"]
        if event.key == pygame.K_TAB:
            if input_active == "month": task_month = _commit_month({"month_typed": month_typed}, task_month, months); month_typed = ""
            if input_active == "day": task_day = _commit_day({"day_typed": day_typed}, task_day, max_days); day_typed = ""
            try:
                i = tab_order.index(input_active) if input_active in tab_order else -1
                input_active = tab_order[(i + 1) % len(tab_order)]
            except ValueError:
                input_active = "task"
            if input_active == "task": caret_task = len(current_task)
            elif input_active == "month": caret_month = 0
            elif input_active == "day": caret_day = 0
            elif input_active == "spoons": caret_spoons = 0

        elif input_active == "task":
            if event.key == pygame.K_RETURN:
                input_active = "month"; caret_month = 0
            elif event.key == pygame.K_BACKSPACE:
                if caret_task > 0:
                    current_task = current_task[:caret_task-1] + current_task[caret_task:]
                    caret_task -= 1
            elif event.key == pygame.K_DELETE:
                if caret_task < len(current_task):
                    current_task = current_task[:caret_task] + current_task[caret_task+1:]
            elif event.key == pygame.K_LEFT:
                if caret_task > 0: caret_task -= 1
            elif event.key == pygame.K_RIGHT:
                if caret_task < len(current_task): caret_task += 1
            elif event.key == pygame.K_HOME:
                caret_task = 0
            elif event.key == pygame.K_END:
                caret_task = len(current_task)
            else:
                ch = event.unicode
                if ch:
                    candidate = current_task[:caret_task] + ch + current_task[caret_task:]
                    if font.size(candidate)[0] <= MAX_TASK_PIXEL_WIDTH:
                        current_task = candidate
                        caret_task += 1

        elif input_active == "month":
            if event.key == pygame.K_RETURN:
                task_month = _commit_month({"month_typed": month_typed}, task_month, months); month_typed = ""; input_active = "day"; caret_day = 0
            elif event.key == pygame.K_BACKSPACE:
                if caret_month > 0:
                    month_typed = month_typed[:caret_month-1] + month_typed[caret_month:]
                    caret_month -= 1
            elif event.key == pygame.K_DELETE:
                if caret_month < len(month_typed):
                    month_typed = month_typed[:caret_month] + month_typed[caret_month+1:]
            elif event.key == pygame.K_LEFT:
                if caret_month > 0: caret_month -= 1
            elif event.key == pygame.K_RIGHT:
                if caret_month < len(month_typed): caret_month += 1
            elif event.key == pygame.K_HOME:
                caret_month = 0
            elif event.key == pygame.K_END:
                caret_month = len(month_typed)
            else:
                ch = event.unicode
                if ch.isalpha():
                    month_typed = month_typed[:caret_month] + ch + month_typed[caret_month:]
                    caret_month += 1


        elif input_active == "day":
            if event.key == pygame.K_RETURN:
                task_day = _commit_day({"day_typed": day_typed}, task_day, max_days); day_typed = ""; input_active = "spoons"; caret_spoons = 0
            elif event.key == pygame.K_BACKSPACE:
                if caret_day > 0:
                    day_typed = day_typed[:caret_day-1] + day_typed[caret_day:]
                    caret_day -= 1
            elif event.key == pygame.K_DELETE:
                if caret_day < len(day_typed):
                    day_typed = day_typed[:caret_day] + day_typed[caret_day+1:]
            elif event.key == pygame.K_LEFT:
                if caret_day > 0: caret_day -= 1
            elif event.key == pygame.K_RIGHT:
                if caret_day < len(day_typed): caret_day += 1
            elif event.key == pygame.K_HOME:
                caret_day = 0
            elif event.key == pygame.K_END:
                caret_day = len(day_typed)
            else:
                ch = event.unicode
                if ch.isdigit():
                    if len(day_typed) < 2:
                        day_typed = day_typed[:caret_day] + ch + day_typed[caret_day:]
                        caret_day += 1

        elif input_active == "spoons":
            if isinstance(current_spoons, int): current_spoons = ""
            if event.key == pygame.K_RETURN:
                if current_task and current_spoons:
                    task_date = datetime(current_time.year, task_month, int(task_day))
                    _add_task_entry(current_task, current_spoons, folder, task_date, current_time, (homework_tasks_list,chores_tasks_list,work_tasks_list,misc_tasks_list,exams_tasks_list,projects_tasks_list), recurring_toggle_on, task_how_often, task_how_long, task_repetitions_amount)
                    current_task = ""; current_spoons = ""; input_active = "task"; month_typed = ""; day_typed = ""; caret_task = 0; caret_spoons = 0
            elif event.key == pygame.K_BACKSPACE:
                if caret_spoons > 0:
                    current_spoons = current_spoons[:caret_spoons-1] + current_spoons[caret_spoons:]
                    caret_spoons -= 1
            elif event.key == pygame.K_DELETE:
                if caret_spoons < len(current_spoons):
                    current_spoons = current_spoons[:caret_spoons] + current_spoons[caret_spoons+1:]
            elif event.key == pygame.K_LEFT:
                if caret_spoons > 0: caret_spoons -= 1
            elif event.key == pygame.K_RIGHT:
                if caret_spoons < len(current_spoons): caret_spoons += 1
            elif event.key == pygame.K_HOME:
                caret_spoons = 0
            elif event.key == pygame.K_END:
                caret_spoons = len(current_spoons)
            else:
                ch = event.unicode
                if ch.isdigit():
                    current_spoons = current_spoons[:caret_spoons] + ch + current_spoons[caret_spoons:]
                    caret_spoons += 1
            if str(current_spoons).isdigit() and int(current_spoons) > 10:
                current_spoons = "10"; caret_spoons = min(caret_spoons, len(current_spoons))


    return (input_active,page,folder,recurring_toggle_on,current_task,current_spoons,task_month,task_day,homework_tasks_list,chores_tasks_list,work_tasks_list,misc_tasks_list,exams_tasks_list,projects_tasks_list,task_how_often,task_how_long,task_repetitions_amount)