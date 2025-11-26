from config import *

from drawing_functions.draw_input_box import draw_input_box, InputBox, logic_input_box
import importlib
draw_complete_tasks_folders = importlib.import_module("drawing_functions.draw_complete_tasks_folders").draw_complete_tasks_folders
ctf_mod = importlib.import_module("drawing_functions.draw_complete_tasks_folders")

import pygame
import math
from datetime import datetime, timedelta

MONTHS = ["January", "February","March","April","May","June","July","August","September","October","November","December"]

current_spoons = ""

# Registry of all input fields on the Add Task screen
input_boxes = {
    "task":          InputBox(None, text="", multiline=False, fontsize=0.06, box_type="text"),
    "description":   InputBox(None, text="", multiline=True,  fontsize=0.05, box_type="text"),
    "spoons":        InputBox(None, text="", multiline=False, fontsize=0.06, box_type="spoons"),

    "month":         InputBox(None, text="", multiline=False, fontsize=0.06, box_type="month"),
    "day":           InputBox(None, text="", multiline=False, fontsize=0.06, box_type="day"),
    "start_time":    InputBox(None, text="", multiline=False, fontsize=0.06, box_type="time"),

    "how_often":     InputBox(None, text="", multiline=False, fontsize=0.05, box_type="positive_int"),
    "how_long":      InputBox(None, text="", multiline=False, fontsize=0.05, box_type="positive_int"),
    "repetitions":   InputBox(None, text="", multiline=False, fontsize=0.05, box_type="positive_int"),
}

# Add flash fields only to task and spoons boxes
input_boxes["task"].flash_timer = 0
input_boxes["task"].flash_error = False

input_boxes["spoons"].flash_timer = 0
input_boxes["spoons"].flash_error = False

# [name, spoons, completed, days_left, due_date, start_time, end_time, labels]
IDX_NAME = 0; IDX_SPOONS = 1; IDX_COMPLETED = 2; IDX_DAYS_LEFT = 3; IDX_DUE_DATE = 4; IDX_START_TIME = 5; IDX_END_TIME = 6; IDX_LABELS = 7

normal_layout_heights = {
    "task_label":                  0.28,    # “Enter task name:”
    "task_input_line":             0.35,   # y=195/600
    "due_date_label":              0.51,   # “Enter due date:” & “Enter Start date:”
    "due_date_input_line":         0.58,   # y=305/600
    "spoons_label":                0.74,   # “Enter spoons needed:”
    "spoons_input_line":           0.81,   # y=420/600
    "description_label":           0.37,   # “Enter description:”
    "description_input_line":      0.47,   # y=255/600
}

description_layout_heights = {
    "task_label":                  0.20,    # “Enter task name:”
    "task_input_line":             0.27,   # y=195/600
    "description_label":           0.37,   # “Enter description:”
    "description_input_line":      0.44,   # y=255/600
    "due_date_label":              0.60,   # “Enter due date:” & “Enter Start date:”
    "due_date_input_line":         0.67,   # y=305/600
    "spoons_label":                0.77,   # “Enter spoons needed:”
    "spoons_input_line":           0.84,   # y=420/600
}

def _compute_due_info(task_month, task_day):
    """Return (line1, line2) such as ('Due in 1 day', 'Tuesday') with correct year logic."""

    today = datetime.now()
    today_date = today.date()

    # Determine correct year using the SAME logic as Add Task
    try:
        proposed_date = datetime(today.year, task_month, task_day)
    except:
        return "", ""

    one_month_ago = today - timedelta(days=30)

    if one_month_ago <= proposed_date <= today:
        due_dt = proposed_date
    elif proposed_date < one_month_ago:
        due_dt = datetime(today.year + 1, task_month, task_day)
    else:
        due_dt = proposed_date if proposed_date >= today else datetime(today.year + 1, task_month, task_day)

    due_date = due_dt.date()

    # Compute delta
    delta = (due_date - today_date).days

    if delta < 0:
        line1 = "Overdue"
    elif delta == 0:
        line1 = "Due today"
    elif delta == 1:
        line1 = "Due 1 day"
    else:
        line1 = f"Due {delta} days"

    weekday = due_date.strftime("%A")

    return line1, weekday

def finalize_month_input(box):
    """
    Centralized commit logic for the month input box.
    Called when leaving the month field (Tab or clicking off).
    """

    # 1. If autofill already determined a match, commit it
    if getattr(box, "pending_full_month", None):
        box.text = box.pending_full_month

    else:
        # 2. Recompute from prefix
        prefix = box.text.strip().lower()
        match = None

        if prefix:
            for m in MONTHS:
                if m.lower().startswith(prefix):
                    match = m
                    break

        if match:
            box.text = match
        else:
            # 3. Invalid input → revert to last known valid text
            box.text = box.saved_text

    # 4. Reset autofill state
    box.pending_full_month = None
    box.autofill_text = ""

    # 5. Reset caret + selection
    box.caret = len(box.text)
    box.sel_start = box.caret
    box.sel_end = box.caret

def draw_tooltip(screen, rect, text):
    """Draws a small tooltip to the RIGHT of the given rect."""
    font_tip = pygame.font.Font("fonts/Stardew_Valley.ttf", 22)

    surf = font_tip.render(text, True, (255, 255, 255))
    padding = 6
    w = surf.get_width() + padding*2
    h = surf.get_height() + padding*2

    tooltip_rect = pygame.Rect(rect.right + 12, rect.y, w, h)
    pygame.draw.rect(screen, (30,30,30), tooltip_rect, border_radius=6)
    pygame.draw.rect(screen, (220,220,220), tooltip_rect, width=2, border_radius=6)

    screen.blit(surf, (tooltip_rect.x + padding, tooltip_rect.y + padding))


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
TASK_NAME_REF = "thisisthecharacterlimit?ye"
MAX_TASK_PIXEL_WIDTH = font.size(TASK_NAME_REF)[0]  # uses your existing `font`

def draw_input_tasks(screen, spoons, current_task, current_description, current_spoons, input_active, 
                     folder, task_month, task_day, description_toggle_on, time_toggle_on, recurring_toggle_on,
                     start_time, end_time, done_button_color, background_color,
                     add_tasks_choose_folder_color, add_tasks_chosen_folder_color,
                     icon_image, spoon_name_input, task_how_often, task_how_long,
                     task_repetitions_amount, folder_one, folder_two,
                     folder_three, folder_four, folder_five, folder_six, 
                     manillaFolder, manilla_folder_text_color):

    if description_toggle_on: layout_heights = description_layout_heights
    else: layout_heights = normal_layout_heights

    screen_h = screen.get_height()
    y_pos = {k: int(v * screen_h) for k, v in layout_heights.items()}

    r, g, b = background_color
    folder_list = ["homework", "chores", "work", "misc", "exams", "projects"]
    done_button_y_pos = 114 + 70 * folder_list.index(folder)

    done_button_color = tuple(max(0, c - 20) for c in (r, g, b))
    due_date_infill_color = tuple(min(255, c + 20) for c in (r, g, b))

    # ----- Sync calendar → input fields whenever entering Input Tasks -----

    # MONTH
    if not input_boxes["month"].active:
        if task_month:
            input_boxes["month"].text = MONTHS[task_month - 1]
            input_boxes["month"].saved_text = input_boxes["month"].text
            input_boxes["month"].autofill_text = ""
            input_boxes["month"].pending_full_month = None
            input_boxes["month"].caret = len(input_boxes["month"].text)

    # DAY
    if not input_boxes["day"].active:
        if task_day:
            input_boxes["day"].text = str(task_day)
            input_boxes["day"].saved_text = input_boxes["day"].text
            input_boxes["day"].caret = len(input_boxes["day"].text)


    # --- Geometry for all boxes (must match logic_input_tasks) ---
    task_rect = pygame.Rect(250, y_pos["task_input_line"], 300, 50)
    description_rect = pygame.Rect(225, y_pos.get("description_input_line", y_pos["task_input_line"]), 350, 80)

    _SPOONS_X_BASE = 375
    _SPOONS_X_SHIFTED = 180
    spoon_rect = pygame.Rect(_SPOONS_X_SHIFTED if recurring_toggle_on else _SPOONS_X_BASE, y_pos["spoons_input_line"], 50, 50)

    gap = 20
    how_often_rect = pygame.Rect(spoon_rect.x + spoon_rect.width + gap, y_pos["spoons_input_line"], 120, 50)
    how_long_rect = pygame.Rect(how_often_rect.x + how_often_rect.width + gap, y_pos["spoons_input_line"], 120, 50)
    repetitions_rect = pygame.Rect(how_long_rect.x + how_long_rect.width + gap, y_pos["spoons_input_line"], 120, 50)

    how_often_up_button = pygame.Rect(how_often_rect.right - 20, y_pos["spoons_input_line"] + 7, 15, 15)
    how_often_down_button = pygame.Rect(how_often_rect.right - 20, y_pos["spoons_input_line"] + 25, 15, 15)
    how_long_up_button = pygame.Rect(how_long_rect.right - 20, y_pos["spoons_input_line"] + 7, 15, 15)
    how_long_down_button = pygame.Rect(how_long_rect.right - 20, y_pos["spoons_input_line"] + 25, 15, 15)
    repetitions_up_button = pygame.Rect(repetitions_rect.right - 20, y_pos["spoons_input_line"] + 7, 15, 15)
    repetitions_down_button = pygame.Rect(repetitions_rect.right - 20, y_pos["spoons_input_line"] + 25, 15, 15)

    month_rect_normal = pygame.Rect(280, y_pos["due_date_input_line"], 160, 50)
    month_up_button_normal = pygame.Rect(420, int(y_pos["due_date_input_line"] + 7), 15, 15)
    month_down_button_normal = pygame.Rect(420, int(y_pos["due_date_input_line"] + 25), 15, 15)
    day_rect_normal = pygame.Rect(465, y_pos["due_date_input_line"], 70, 50)
    day_up_button_normal = pygame.Rect(515, int(y_pos["due_date_input_line"] + 7), 15, 15)
    day_down_button_normal = pygame.Rect(515, int(y_pos["due_date_input_line"] + 25), 15, 15)

    time_shift = 80
    month_rect_shifted = pygame.Rect(280 - time_shift, y_pos["due_date_input_line"], 160, 50)
    month_up_button_shifted = pygame.Rect(420 - time_shift, int(y_pos["due_date_input_line"] + 7), 15, 15)
    month_down_button_shifted = pygame.Rect(420 - time_shift, int(y_pos["due_date_input_line"] + 25), 15, 15)
    day_rect_shifted = pygame.Rect(465 - time_shift, y_pos["due_date_input_line"], 70, 50)
    day_up_button_shifted = pygame.Rect(515 - time_shift, int(y_pos["due_date_input_line"] + 7), 15, 15)
    day_down_button_shifted = pygame.Rect(515 - time_shift, int(y_pos["due_date_input_line"] + 25), 15, 15)

    active_month_rect = month_rect_shifted if time_toggle_on else month_rect_normal
    active_day_rect = day_rect_shifted if time_toggle_on else day_rect_normal

    start_time_rect = pygame.Rect(active_day_rect.right + 20, active_day_rect.y, 120, 50)
    start_time_up_button = pygame.Rect(start_time_rect.right - 20, start_time_rect.y + 7, 15, 15)
    start_time_down_button = pygame.Rect(start_time_rect.right - 20, start_time_rect.y + 25, 15, 15)

    done_button = pygame.Rect(630, done_button_y_pos, 50, 32)
    arrow_points = [(done_button.right, done_button.top - 10), (done_button.right + 30, done_button.centery), (done_button.right, done_button.bottom + 10)]

    # --- Attach rects to InputBoxes ---
    task_box = input_boxes["task"]; task_box.rect = task_rect; task_box.blocked_regions = []
    desc_box = input_boxes["description"]; desc_box.rect = description_rect; desc_box.blocked_regions = []

    spoons_box = input_boxes["spoons"]; spoons_box.rect = spoon_rect; spoons_box.blocked_regions = []

    month_box = input_boxes["month"]; month_box.rect = active_month_rect
    month_box.blocked_regions = [month_up_button_normal, month_down_button_normal, month_up_button_shifted, month_down_button_shifted]

    day_box = input_boxes["day"]; day_box.rect = active_day_rect
    day_box.blocked_regions = [day_up_button_normal, day_down_button_normal, day_up_button_shifted, day_down_button_shifted]

    start_box = input_boxes["start_time"]; start_box.rect = start_time_rect
    start_box.blocked_regions = [start_time_up_button, start_time_down_button]

    how_often_box = input_boxes["how_often"]; how_often_box.rect = how_often_rect
    how_often_box.blocked_regions = [how_often_up_button, how_often_down_button]

    how_long_box = input_boxes["how_long"]; how_long_box.rect = how_long_rect
    how_long_box.blocked_regions = [how_long_up_button, how_long_down_button]

    repetitions_box = input_boxes["repetitions"]; repetitions_box.rect = repetitions_rect
    repetitions_box.blocked_regions = [repetitions_up_button, repetitions_down_button]


    # --- Sync visible text from state when not actively edited ---
    if not task_box.active: task_box.text = current_task
    if not desc_box.active: desc_box.text = current_description
    if not spoons_box.active:
        if isinstance(current_spoons, int): spoons_box.text = "" if current_spoons == 0 else str(current_spoons)
        else: spoons_box.text = current_spoons

    # --- INITIALIZE month/day text if box is empty and user is not typing ---
    if not month_box.active and month_box.text.strip() == "":
        month_box.text = MONTHS[task_month - 1]  # e.g. "November"
        month_box.saved_text = month_box.text

    if not day_box.active and day_box.text.strip() == "":
        day_box.text = str(task_day)
        day_box.saved_text = day_box.text

    # --- Restore month/day if user clicked in then clicked off without typing ---
    if not month_box.active:
        finalize_month_input(month_box)

    # TIME — finalize on blur: clamp to 23:59 and sync formatted text
    if not start_box.active:
        start_time[:] = _parse_start_time_text(start_box.text, start_time)
        try:
            hh = int(start_time[0]); mm = int(start_time[1])
        except Exception:
            hh, mm = _now_hh_mm(); start_time[:] = [hh, mm]
        hh = max(0, min(23, hh)); mm = max(0, min(59, mm))
        start_time[0], start_time[1] = hh, mm
        if time_toggle_on:
            start_box.text = f"{hh:02d}:{mm:02d}"
        else:
            start_box.text = ""

    if not day_box.active and day_box.text.strip() == "":
        day_box.text = str(task_day)

    if time_toggle_on:
        # keep whatever text draw_input_box formats; start_box.text already synced above
        pass
    else:
        start_box.text = ""

    if recurring_toggle_on:
        if not how_often_box.active: how_often_box.text = str(task_how_often)
        if not how_long_box.active: how_long_box.text = str(task_how_long)
        if not repetitions_box.active: repetitions_box.text = str(task_repetitions_amount)

    # --- Draw folders and toggles ---
    draw_complete_tasks_folders(screen, folder, folder_one, folder_two, folder_three, folder_four, folder_five, folder_six, manillaFolder, manilla_folder_text_color)

    # --- Arrows for spinners ---
    arrow = font.render(">", True, done_button_color)  # type: ignore
    up_arrow = pygame.transform.rotate(arrow, 90)
    down_arrow = pygame.transform.rotate(arrow, 270)

    # --- Labels ---
    screen.blit(font.render("Task Name:", True, WHITE), (335, y_pos["task_label"]))  # type: ignore

    if description_toggle_on: screen.blit(font.render("Description:", True, WHITE), (335, y_pos["description_label"]))  # type: ignore

    if recurring_toggle_on: screen.blit(font.render("Spoons:", True, WHITE), (spoon_rect.x - 15, y_pos["spoons_label"]))  # type: ignore
    else: screen.blit(font.render("Spoons:", True, WHITE), (360, y_pos["spoons_label"]))  # type: ignore

    # --- Draw InputBoxes ---
    draw_input_box(screen, task_box, DARK_SLATE_GRAY, DARK_SLATE_GRAY, background_color=background_color, infill="light")  # type: ignore

    if description_toggle_on: draw_input_box(screen, desc_box, DARK_SLATE_GRAY, DARK_SLATE_GRAY, background_color=background_color, infill="light")  # type: ignore

    draw_input_box(screen, spoons_box, DARK_SLATE_GRAY, DARK_SLATE_GRAY, centered=True, background_color=background_color, infill="light")  # type: ignore

    # Month / Day / Start Time
    if time_toggle_on:
        screen.blit(font.render("Start Date:" if recurring_toggle_on else "Due Date:", True, WHITE), (345  - time_shift if recurring_toggle_on else 345 - time_shift + 10, y_pos["due_date_label"]))  # type: ignore
        draw_input_box(screen, month_box, DARK_SLATE_GRAY, DARK_SLATE_GRAY, background_color=background_color, infill="light")  # type: ignore
        draw_input_box(screen, day_box, DARK_SLATE_GRAY, DARK_SLATE_GRAY, background_color=background_color, infill="light")  # type: ignore

        for btn in (month_up_button_shifted, month_down_button_shifted, day_up_button_shifted, day_down_button_shifted): pygame.draw.rect(screen, due_date_infill_color, btn)
        screen.blit(up_arrow, (month_up_button_shifted.x - 9, month_up_button_shifted.y)); screen.blit(down_arrow, (month_down_button_shifted.x - 12, month_down_button_shifted.y))
        screen.blit(up_arrow, (day_up_button_shifted.x - 9, day_up_button_shifted.y)); screen.blit(down_arrow, (day_down_button_shifted.x - 12, day_down_button_shifted.y))

        screen.blit(font.render("Start Time:", True, WHITE), (start_time_rect.x - 10, y_pos["due_date_label"]))  # type: ignore
        draw_input_box(screen, start_box, DARK_SLATE_GRAY, DARK_SLATE_GRAY, background_color=background_color, infill="light")  # type: ignore

        for btn in (start_time_up_button, start_time_down_button): pygame.draw.rect(screen, due_date_infill_color, btn)
        screen.blit(up_arrow, (start_time_up_button.x - 9, start_time_up_button.y)); screen.blit(down_arrow, (start_time_down_button.x - 12, start_time_down_button.y))
    else:
        screen.blit(font.render("Start Date:" if recurring_toggle_on else "Due Date:", True, WHITE), (335 if recurring_toggle_on else 345, y_pos["due_date_label"]))  # type: ignore
        draw_input_box(screen, month_box, DARK_SLATE_GRAY, DARK_SLATE_GRAY, background_color=background_color, infill="light")  # type: ignore
        draw_input_box(screen, day_box, DARK_SLATE_GRAY, DARK_SLATE_GRAY, background_color=background_color, infill="light")  # type: ignore

        for btn in (month_up_button_normal, month_down_button_normal, day_up_button_normal, day_down_button_normal): pygame.draw.rect(screen, due_date_infill_color, btn)
        screen.blit(up_arrow, (month_up_button_normal.x - 9, month_up_button_normal.y)); screen.blit(down_arrow, (month_down_button_normal.x - 12, month_down_button_normal.y))
        screen.blit(up_arrow, (day_up_button_normal.x - 9, day_up_button_normal.y)); screen.blit(down_arrow, (day_down_button_normal.x - 12, day_down_button_normal.y))

    # Recurring fields
    if recurring_toggle_on:
        small_label_shift = 5
        screen.blit(small_font.render("How Often:", True, WHITE), (how_often_rect.x + 10, y_pos["spoons_label"] + small_label_shift))  # type: ignore
        screen.blit(small_font.render("How Long:", True, WHITE), (how_long_rect.x + 10, y_pos["spoons_label"] + small_label_shift))  # type: ignore
        screen.blit(small_font.render("Repetitions:", True, WHITE), (repetitions_rect.x + 10, y_pos["spoons_label"] + small_label_shift))  # type: ignore

        draw_input_box(screen, how_often_box, DARK_SLATE_GRAY, DARK_SLATE_GRAY, background_color=background_color, infill="light")  # type: ignore
        draw_input_box(screen, how_long_box, DARK_SLATE_GRAY, DARK_SLATE_GRAY, background_color=background_color, infill="light")  # type: ignore
        draw_input_box(screen, repetitions_box, DARK_SLATE_GRAY, DARK_SLATE_GRAY, background_color=background_color, infill="light")  # type: ignore

        screen.blit(font.render("days", True, BLACK), (how_often_rect.x + 35, y_pos["spoons_label"] + small_label_shift + 40))  # type: ignore
        screen.blit(font.render("weeks", True, BLACK), (how_long_rect.x + 27, y_pos["spoons_label"] + small_label_shift + 40))  # type: ignore
        screen.blit(font.render("times", True, BLACK), (repetitions_rect.x + 31, y_pos["spoons_label"] + small_label_shift + 40))  # type: ignore

        barrier_w = 24
        for base_rect in (how_often_rect, how_long_rect, repetitions_rect):
            barrier_rect = pygame.Rect(base_rect.right - barrier_w, base_rect.y + 4, barrier_w - 4, base_rect.height - 8); pygame.draw.rect(screen, due_date_infill_color, barrier_rect)

        for btn in (how_often_up_button, how_often_down_button, how_long_up_button, how_long_down_button, repetitions_up_button, repetitions_down_button): pygame.draw.rect(screen, due_date_infill_color, btn)

        screen.blit(up_arrow, (how_often_up_button.x - 9, how_often_up_button.y)); screen.blit(down_arrow, (how_often_down_button.x - 12, how_often_down_button.y))
        screen.blit(up_arrow, (how_long_up_button.x - 9, how_long_up_button.y)); screen.blit(down_arrow, (how_long_down_button.x - 12, how_long_down_button.y))
        screen.blit(up_arrow, (repetitions_up_button.x - 9, repetitions_up_button.y)); screen.blit(down_arrow, (repetitions_down_button.x - 12, repetitions_down_button.y))

    # --- Add button ---
    pygame.draw.rect(screen, done_button_color, done_button)
    pygame.draw.polygon(screen, done_button_color, arrow_points)
    screen.blit(font.render("Add", True, BLACK), (done_button.x + 15, done_button.y + 2))  # type: ignore

    #   DUE DATE PREVIEW TEXT
    line1, line2 = _compute_due_info(task_month, task_day)

    preview_color = done_button_color   # match Add button color
    preview_font = small_font

    # Position logic
    is_bottom_folder = (folder == "projects")

    # Default (text below button)
    text_y = done_button.bottom + 8

    # If bottom folder → move text ABOVE button
    if is_bottom_folder:
        text_y = done_button.top - 48

    # Draw Line 1
    surf1 = preview_font.render(line1, True, preview_color)
    screen.blit(surf1, (done_button.x - 21, text_y))

    # Draw Line 2
    surf2 = preview_font.render(line2, True, preview_color)
    screen.blit(surf2, (done_button.x - 21, text_y + 18))


    #-- Toggle Buttons ---
    description_btn_rect = description_button.get_rect(topleft=(120, 100))
    time_btn_rect = time_button.get_rect(topleft=(120, 150))
    recurring_btn_rect = recurring_button.get_rect(topleft=(120, 200))

    def _draw_toggle_aura(rect):
        aura = pygame.Surface((rect.width + 8, rect.height + 8), pygame.SRCALPHA); pygame.draw.rect(aura, (0, 255, 0, 70), aura.get_rect(), border_radius=8); screen.blit(aura, (rect.x - 4, rect.y - 4))

    if description_toggle_on: _draw_toggle_aura(description_btn_rect)
    if time_toggle_on: _draw_toggle_aura(time_btn_rect)
    if recurring_toggle_on: _draw_toggle_aura(recurring_btn_rect)

    screen.blit(description_button, description_btn_rect.topleft)
    screen.blit(time_button, time_btn_rect.topleft)
    screen.blit(recurring_button, recurring_btn_rect.topleft)

    # --- Tooltip Hover Detection ---
    mx, my = pygame.mouse.get_pos()

    if description_btn_rect.collidepoint(mx, my):
        draw_tooltip(screen, description_btn_rect, "Add a description")

    if time_btn_rect.collidepoint(mx, my):
        draw_tooltip(screen, time_btn_rect, "Enable start time")

    if recurring_btn_rect.collidepoint(mx, my):
        draw_tooltip(screen, recurring_btn_rect, "Add a repeating task")

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

# --- Helper parsing & defaults for InputBox-based fields ---

def _now_hh_mm():
    n = datetime.now(); return n.hour, n.minute

def _month_from_text(text, current_month):
    t = (text or "").strip()
    if not t: return current_month
    if t.isdigit():
        val = int(t)
        return val if 1 <= val <= 12 else current_month
    t_low = t.lower()
    for i, name in enumerate(MONTHS):
        name_low = name.lower()
        if t_low == name_low or t_low == name_low[:3]:
            return i + 1
    return current_month

def _day_from_text(text, current_day, max_days):
    t = (text or "").strip()
    if not t or not t.isdigit(): return current_day
    val = int(t)
    val = max(1, min(val, max_days))
    return val

def _parse_positive_int(text, current_val, min_val=1, max_val=None):
    t = (text or "").strip()
    if not t.isdigit(): return current_val
    v = int(t)
    if max_val is not None: v = min(v, max_val)
    if v < min_val: v = min_val
    return v

def _parse_start_time_text(text, current_start_time):
    t = (text or "").strip()
    if not t: return current_start_time
    digits = "".join(ch for ch in t if ch.isdigit())[:4]
    if not digits: return current_start_time
    if len(digits) <= 2:
        hh = int(digits); mm = 0
    else:
        hh = int(digits[:-2]) if digits[:-2] else 0; mm = int(digits[-2:])
    hh = max(0, min(23, hh)); mm = max(0, min(59, mm))
    return [hh, mm]

def _add_task_entry(current_task, current_description, current_spoons, folder, task_date, current_time, lists_tuple,
                    recurring_toggle_on, task_how_often, task_how_long, task_repetitions_amount,
                    start_time):
    (homework_tasks_list, chores_tasks_list, work_tasks_list,
     misc_tasks_list, exams_tasks_list, projects_tasks_list) = lists_tuple

    # Normalize start_time -> [HH, MM, 0, 0]
    try:
        hh, mm = int(start_time[0]) % 24, int(start_time[1]) % 60
    except Exception:
        now = datetime.now(); hh, mm = now.hour, now.minute
    start_time_4 = [hh, mm, 0, 0]

    days_till_due = (task_date - current_time).days + 1

    def _push(entry):
        if folder == "homework": homework_tasks_list.append(entry)
        elif folder == "chores": chores_tasks_list.append(entry)
        elif folder == "work": work_tasks_list.append(entry)
        elif folder == "misc": misc_tasks_list.append(entry)
        elif folder == "exams": exams_tasks_list.append(entry)
        elif folder == "projects": projects_tasks_list.append(entry)

    new_entry = [
        current_task,                # 0 name
        current_description.strip(), # 1 description (new)
        int(current_spoons),         # 2 spoons
        0,                           # 3 completed flag
        days_till_due,               # 4 days_left
        task_date,                   # 5 due_date
        start_time_4,                # 6 start_time
        [0,0,0,0],                   # 7 end_time (placeholder)
        []                           # 8 labels
    ]

    if recurring_toggle_on:
        for i in range(task_repetitions_amount):
            actual_date = task_date + timedelta(days=i * task_how_often)
            days_left = (actual_date - current_time).days + 1
            new_entry[4] = days_left
            new_entry[5] = actual_date
            _push(new_entry.copy())
    else:
        _push(new_entry)

def logic_input_tasks(event, screen, current_task, current_description, current_spoons, folder, task_month, task_day, task_how_often, task_how_long, task_repetitions_amount, description_toggle_on, time_toggle_on, recurring_toggle_on, max_days, input_active, homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list, exams_tasks_list, projects_tasks_list, start_time):
    page = "input_tasks"

    # Layout same as draw_input_tasks
    if description_toggle_on: layout_heights = description_layout_heights
    else: layout_heights = normal_layout_heights

    screen_h = screen.get_height()
    y_pos = {k: int(v * screen_h) for k, v in layout_heights.items()}

    folder_list = ["homework", "chores", "work", "misc", "exams", "projects"]
    done_button_y_pos = 114 + 70 * folder_list.index(folder)
    done_button = pygame.Rect(630, done_button_y_pos, 50, 32)

    description_btn_rect = description_button.get_rect(topleft=(120, 100))
    time_btn_rect = time_button.get_rect(topleft=(120, 150))
    recurring_btn_rect = recurring_button.get_rect(topleft=(120, 200))

    # Geometry (must match draw_input_tasks)
    task_rect = pygame.Rect(250, y_pos["task_input_line"], 300, 50)
    description_rect = pygame.Rect(225, y_pos.get("description_input_line", y_pos["task_input_line"]), 350, 80)

    _SPOONS_X_BASE = 375
    _SPOONS_X_SHIFTED = 180
    spoon_rect = pygame.Rect(_SPOONS_X_SHIFTED if recurring_toggle_on else _SPOONS_X_BASE, y_pos["spoons_input_line"], 50, 50)

    gap = 20
    how_often_rect = pygame.Rect(spoon_rect.x + spoon_rect.width + gap, y_pos["spoons_input_line"], 120, 50)
    how_long_rect = pygame.Rect(how_often_rect.x + how_often_rect.width + gap, y_pos["spoons_input_line"], 120, 50)
    repetitions_rect = pygame.Rect(how_long_rect.x + how_long_rect.width + gap, y_pos["spoons_input_line"], 120, 50)

    how_often_up_button = pygame.Rect(how_often_rect.right - 20, y_pos["spoons_input_line"] + 7, 15, 15)
    how_often_down_button = pygame.Rect(how_often_rect.right - 20, y_pos["spoons_input_line"] + 25, 15, 15)
    how_long_up_button = pygame.Rect(how_long_rect.right - 20, y_pos["spoons_input_line"] + 7, 15, 15)
    how_long_down_button = pygame.Rect(how_long_rect.right - 20, y_pos["spoons_input_line"] + 25, 15, 15)
    repetitions_up_button = pygame.Rect(repetitions_rect.right - 20, y_pos["spoons_input_line"] + 7, 15, 15)
    repetitions_down_button = pygame.Rect(repetitions_rect.right - 20, y_pos["spoons_input_line"] + 25, 15, 15)

    month_rect_normal = pygame.Rect(280, y_pos["due_date_input_line"], 160, 50)
    day_rect_normal = pygame.Rect(465, y_pos["due_date_input_line"], 70, 50)

    time_shift = 80
    month_rect_shifted = pygame.Rect(280 - time_shift, y_pos["due_date_input_line"], 160, 50)
    day_rect_shifted = pygame.Rect(465 - time_shift, y_pos["due_date_input_line"], 70, 50)

    active_month_rect = month_rect_shifted if time_toggle_on else month_rect_normal
    active_day_rect = day_rect_shifted if time_toggle_on else day_rect_normal

    start_time_rect = pygame.Rect(active_day_rect.right + 20, active_day_rect.y, 120, 50)
    start_time_up_button = pygame.Rect(start_time_rect.right - 20, start_time_rect.y + 7, 15, 15)
    start_time_down_button = pygame.Rect(start_time_rect.right - 20, start_time_rect.y + 25, 15, 15)

    # Attach rects to InputBoxes
    task_box = input_boxes["task"]; task_box.rect = task_rect
    desc_box = input_boxes["description"]; desc_box.rect = description_rect
    spoons_box = input_boxes["spoons"]; spoons_box.rect = spoon_rect
    month_box = input_boxes["month"]; month_box.rect = active_month_rect
    day_box = input_boxes["day"]; day_box.rect = active_day_rect
    start_box = input_boxes["start_time"]; start_box.rect = start_time_rect
    how_often_box = input_boxes["how_often"]; how_often_box.rect = how_often_rect
    how_long_box = input_boxes["how_long"]; how_long_box.rect = how_long_rect
    repetitions_box = input_boxes["repetitions"]; repetitions_box.rect = repetitions_rect

    # Pass event into each InputBox (typing, caret, selection)
    for box in input_boxes.values(): logic_input_box(event, box, screen)

    typed_month = _month_from_text(input_boxes["month"].text, task_month)
    typed_day   = _day_from_text(input_boxes["day"].text, task_day, max_days)

    task_month = typed_month
    task_day   = typed_day

    # Derive which InputBox is active -> input_active label
    input_active = False
    for name, box in input_boxes.items():
        if box.active:
            input_active = name
            break

    # Make sure start_time list is valid
    try:
        _ = int(start_time[0]); _ = int(start_time[1])
    except Exception:
        hh, mm = _now_hh_mm(); start_time[:] = [hh, mm]

    do_add = False

    # --- Mouse handling: toggles, spinners, add, folders ---
    if event.type == pygame.MOUSEBUTTONDOWN:
        if description_btn_rect.collidepoint(event.pos): description_toggle_on = not description_toggle_on
        elif time_btn_rect.collidepoint(event.pos):
            time_toggle_on = not time_toggle_on
            if not time_toggle_on: start_time[:] = [0, 0]
        elif recurring_btn_rect.collidepoint(event.pos): recurring_toggle_on = not recurring_toggle_on

        # Month/Day spinners use numeric state
        if time_toggle_on:
            if pygame.Rect(420 - time_shift, int(y_pos["due_date_input_line"] + 7), 15, 15).collidepoint(event.pos):
                task_month = task_month + 1 if task_month < 12 else 1
                month_box.text = MONTHS[task_month - 1]
                month_box.saved_text = month_box.text

            elif pygame.Rect(420 - time_shift, int(y_pos["due_date_input_line"] + 25), 15, 15).collidepoint(event.pos):
                task_month = task_month - 1 if task_month > 1 else 12
                month_box.text = MONTHS[task_month - 1]
                month_box.saved_text = month_box.text

            elif pygame.Rect(515 - time_shift, int(y_pos["due_date_input_line"] + 7), 15, 15).collidepoint(event.pos):
                task_day = int(task_day) + 1 if int(task_day) < max_days else 1
                day_box.text = str(task_day)
                day_box.saved_text = day_box.text

            elif pygame.Rect(515 - time_shift, int(y_pos["due_date_input_line"] + 25), 15, 15).collidepoint(event.pos):
                task_day = int(task_day) - 1 if int(task_day) > 1 else max_days
                day_box.text = str(task_day)
                day_box.saved_text = day_box.text
        else:
            if pygame.Rect(420, int(y_pos["due_date_input_line"] + 7), 15, 15).collidepoint(event.pos):
                task_month = task_month + 1 if task_month < 12 else 1
                month_box.text = MONTHS[task_month - 1]
                month_box.saved_text = month_box.text
            elif pygame.Rect(420, int(y_pos["due_date_input_line"] + 25), 15, 15).collidepoint(event.pos):
                task_month = task_month - 1 if task_month > 1 else 12
                month_box.text = MONTHS[task_month - 1]
                month_box.saved_text = month_box.text

            elif pygame.Rect(515, int(y_pos["due_date_input_line"] + 7), 15, 15).collidepoint(event.pos):
                task_day = int(task_day) + 1 if int(task_day) < max_days else 1
                day_box.text = str(task_day)
                day_box.saved_text = day_box.text

            elif pygame.Rect(515, int(y_pos["due_date_input_line"] + 25), 15, 15).collidepoint(event.pos):
                task_day = int(task_day) - 1 if int(task_day) > 1 else max_days
                day_box.text = str(task_day)
                day_box.saved_text = day_box.text

        # Start time spinners (15-min steps)
        if time_toggle_on and start_time_up_button.collidepoint(event.pos):
            try: hh, mm = int(start_time[0]), int(start_time[1])
            except Exception: hh, mm = _now_hh_mm()
            hh = max(0, min(23, hh)); mm = max(0, min(59, mm))
            if hh == 23 and mm >= 59:
                hh, mm = 23, 59
            else:
                mm += 15
                if mm >= 60:
                    mm = 0
                    hh += 1
                    if hh > 23:
                        hh, mm = 23, 59
            start_time[0], start_time[1] = hh, mm
            start_box.text = f"{hh:02d}:{mm:02d}"
        elif time_toggle_on and start_time_down_button.collidepoint(event.pos):
            try: hh, mm = int(start_time[0]), int(start_time[1])
            except Exception: hh, mm = _now_hh_mm()
            hh = max(0, min(23, hh)); mm = max(0, min(59, mm))
            if hh == 0 and mm <= 0:
                hh, mm = 0, 0
            else:
                mm -= 15
                if mm < 0:
                    mm = 45
                    hh -= 1
                    if hh < 0:
                        hh, mm = 0, 0
            start_time[0], start_time[1] = hh, mm
            start_box.text = f"{hh:02d}:{mm:02d}"


        # Recurrence spinners
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
        elif repetitions_up_button.collidepoint(event.pos):
            if task_repetitions_amount < 26:
                task_repetitions_amount += 1
                total_days = (task_repetitions_amount - 1) * task_how_often + 1
                task_how_long = max(1, math.ceil(total_days / 7))
        elif repetitions_down_button.collidepoint(event.pos):
            if task_repetitions_amount > 1:
                task_repetitions_amount -= 1
                total_days = (task_repetitions_amount - 1) * task_how_often + 1
                task_how_long = max(1, math.ceil(total_days / 7))

        # Add task via mouse
        if done_button.collidepoint(event.pos):
            task_text = input_boxes["task"].text.strip()
            spoons_text = input_boxes["spoons"].text.strip()

            valid = True

            if task_text == "":
                tb = input_boxes["task"]
                tb.flash_error = True
                tb.flash_timer = 300
                valid = False

            if not spoons_text.isdigit() or int(spoons_text) <= 0:
                sb = input_boxes["spoons"]
                sb.flash_error = True
                sb.flash_timer = 300
                valid = False

            if valid:
                do_add = True


        # Folder selection
        for f_key, rect in reversed(ctf_mod.folder_rects):
            if rect.collidepoint(event.pos):
                folder = f_key
                break

    # --- Keyboard handling: folder selection, Tab navigation, Enter to add ---
    if event.type == pygame.KEYDOWN:
        if event.key in (pygame.K_UP, pygame.K_DOWN):
            idx = folder_list.index(folder) if folder in folder_list else 0
            step = -1 if event.key == pygame.K_UP else 1
            folder = folder_list[(idx + step) % len(folder_list)]

        # Tab navigation between input boxes (order depends on toggles)
        if event.key == pygame.K_TAB:
            mods = pygame.key.get_mods()
            shift = bool(mods & pygame.KMOD_SHIFT)

            # Identify active field
            active_name = None
            for name, box in input_boxes.items():
                if box.active:
                    active_name = name
                    break

            # ---- month finalize ----
            if active_name == "month":
                finalize_month_input(input_boxes["month"])

            # Build tab order
            tab_order = []
            tab_order.append("task")
            if description_toggle_on:
                tab_order.append("description")
            tab_order.append("month")
            tab_order.append("day")
            if time_toggle_on:
                tab_order.append("start_time")
            tab_order.append("spoons")
            if recurring_toggle_on:
                tab_order.extend(["how_often", "how_long", "repetitions"])

            # Determine next field
            if tab_order:
                if active_name in tab_order:
                    idx = tab_order.index(active_name)
                    step = -1 if shift else 1
                    next_idx = (idx + step) % len(tab_order)
                    next_name = tab_order[next_idx]
                else:
                    next_name = tab_order[0]

                # Switch focus
                for name, box in input_boxes.items():
                    box.active = (name == next_name)
                    box.selecting = False

                # When entering the month box with Tab, clear it like a click
                if next_name == "month":
                    mbox = input_boxes["month"]
                    mbox.saved_text = mbox.text
                    mbox.text = ""
                    mbox.autofill_text = ""
                    mbox.pending_full_month = None
                    mbox.caret = 0
                    mbox.sel_start = 0
                    mbox.sel_end = 0

                input_active = next_name

        # Enter / Return: add task if name + spoons are valid (>0)
        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            task_text = input_boxes["task"].text.strip()
            spoons_text = input_boxes["spoons"].text.strip()

            valid = True

            if task_text == "":
                tb = input_boxes["task"]
                tb.flash_error = True
                tb.flash_timer = 300  # ms
                valid = False

            if not spoons_text.isdigit() or int(spoons_text) <= 0:
                sb = input_boxes["spoons"]
                sb.flash_error = True
                sb.flash_timer = 300
                valid = False

            if valid:
                do_add = True

    # --- If we need to add a task, pull values from InputBoxes, parse, push, clear ---
    if do_add:
        task_text = input_boxes["task"].text.strip()
        desc_text = input_boxes["description"].text
        spoons_text = input_boxes["spoons"].text.strip()

        if task_text and spoons_text.isdigit() and int(spoons_text) > 0:
            # Parse month/day from text, fall back to current numeric state
            task_month = _month_from_text(input_boxes["month"].text, task_month)
            task_day = _day_from_text(input_boxes["day"].text, task_day, max_days)

            # Parse optional time and recurrence fields
            if time_toggle_on: start_time = _parse_start_time_text(input_boxes["start_time"].text, start_time)
            if recurring_toggle_on:
                task_how_often = _parse_positive_int(input_boxes["how_often"].text, task_how_often, 1)
                task_how_long = _parse_positive_int(input_boxes["how_long"].text, task_how_long, 1)
                task_repetitions_amount = _parse_positive_int(input_boxes["repetitions"].text, task_repetitions_amount, 1, 26)

            # Determine correct year for the task date (same logic as before)
            today = datetime.now()
            one_month_ago = today - timedelta(days=30)
            proposed_date = datetime(today.year, task_month, int(task_day))
            if one_month_ago <= proposed_date <= today:
                task_date = proposed_date
            elif proposed_date < one_month_ago:
                task_date = datetime(today.year + 1, task_month, int(task_day))
            else:
                task_date = proposed_date if proposed_date >= today else datetime(today.year + 1, task_month, int(task_day))

            _add_task_entry(task_text, desc_text, spoons_text, folder, task_date, current_time, (homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list, exams_tasks_list, projects_tasks_list), recurring_toggle_on, task_how_often, task_how_long, task_repetitions_amount, start_time)

            # Clear text fields and reset focus to task name
            input_boxes["task"].text = ""
            input_boxes["description"].text = ""
            input_boxes["spoons"].text = ""
            current_task = ""; current_description = ""; current_spoons = ""
            for name, box in input_boxes.items(): box.active = False
            input_boxes["task"].active = True
            input_active = "task"

    # Keep outward-facing text state in sync with InputBoxes
    current_task = input_boxes["task"].text
    current_description = input_boxes["description"].text
    current_spoons = input_boxes["spoons"].text

    return (input_active, page, folder, description_toggle_on, time_toggle_on, recurring_toggle_on, current_task, current_description, current_spoons, task_month, task_day, homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list, exams_tasks_list, projects_tasks_list, task_how_often, task_how_long, task_repetitions_amount, start_time)