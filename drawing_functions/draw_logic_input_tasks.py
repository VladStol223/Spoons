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
    "how_long_label":              0.55,   # “How Long:”
    "how_long_input_line":         0.553,   # y=290/600
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
    global start_time_typed, how_often_typed, how_long_typed, repetitions_typed
    global caret_start_time, caret_how_often, caret_how_long, caret_repetitions


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
    done_button       = pygame.Rect(630, done_button_y_pos,50, 32)
    arrow_points = [(done_button.right, done_button.top - 10),(done_button.right + 30, done_button.centery),(done_button.right, done_button.bottom + 10)]

    # Mirror layout math from draw_input_tasks so click/hover regions match visuals
    _recurring_vshift = y_pos["spoons_input_line"] - y_pos["due_date_input_line"]
    _SPOONS_X_BASE = 375
    _SPOONS_X_SHIFTED = 180
    spoon_input_box = pygame.Rect(_SPOONS_X_SHIFTED if recurring_toggle_on else _SPOONS_X_BASE, y_pos["spoons_input_line"], 50, 50)

    gap = 20

    how_often_input_box          = pygame.Rect(spoon_input_box.x + spoon_input_box.width + gap, y_pos["spoons_input_line"], 120, 50)
    how_often_up_button          = pygame.Rect(how_often_input_box.right - 20, y_pos["spoons_input_line"] + 7, 15, 15)
    how_often_down_button        = pygame.Rect(how_often_input_box.right - 20, y_pos["spoons_input_line"] + 25, 15, 15)

    how_long_input_box           = pygame.Rect(how_often_input_box.x + how_often_input_box.width + gap,  y_pos["spoons_input_line"], 120, 50)
    how_long_up_button           = pygame.Rect(how_long_input_box.right - 20, y_pos["spoons_input_line"] + 7, 15, 15)
    how_long_down_button         = pygame.Rect(how_long_input_box.right - 20, y_pos["spoons_input_line"] + 25, 15, 15)

    repetitions_amount_input_box = pygame.Rect(how_long_input_box.x + how_long_input_box.width + gap, y_pos["spoons_input_line"], 120, 50)
    repetitions_amount_up_button = pygame.Rect(repetitions_amount_input_box.right - 20, y_pos["spoons_input_line"] + 7, 15, 15)
    repetitions_amount_down_button = pygame.Rect(repetitions_amount_input_box.right - 20, y_pos["spoons_input_line"] + 25, 15, 15)


    month_input_box_normal = pygame.Rect(280, y_pos["due_date_input_line"], 160, 50)
    month_up_button_normal = pygame.Rect(420, int(y_pos["due_date_input_line"] + 7), 15, 15)
    month_down_button_normal = pygame.Rect(420, int(y_pos["due_date_input_line"] + 25), 15, 15)
    day_input_box_normal   = pygame.Rect(465, y_pos["due_date_input_line"], 70, 50)
    day_up_button_normal   = pygame.Rect(515, int(y_pos["due_date_input_line"] + 7), 15, 15)
    day_down_button_normal = pygame.Rect(515, int(y_pos["due_date_input_line"] + 25), 15, 15)

    time_shift = 80

    month_input_box_recurring_shifted = pygame.Rect(280 - time_shift, y_pos["due_date_input_line"], 160, 50)
    month_up_button_recurring_shifted = pygame.Rect(420 - time_shift, int(y_pos["due_date_input_line"] + 7), 15, 15)
    month_down_button_recurring_shifted = pygame.Rect(420 - time_shift, int(y_pos["due_date_input_line"] + 25), 15, 15)
    day_input_box_recurring_shifted   = pygame.Rect(465 - time_shift, y_pos["due_date_input_line"], 70, 50)
    day_up_button_recurring_shifted   = pygame.Rect(515 - time_shift, int(y_pos["due_date_input_line"] + 7), 15, 15)
    day_down_button_recurring_shifted = pygame.Rect(515 - time_shift, int(y_pos["due_date_input_line"] + 25), 15, 15)

    draw_complete_tasks_folders(screen,folder,folder_one,folder_two,folder_three,folder_four,folder_five,folder_six, homework_tasks_list,chores_tasks_list, work_tasks_list, misc_tasks_list, exams_tasks_list, projects_tasks_list, manillaFolder)

    time_btn_rect = time_button.get_rect(topleft=(120,140))
    recurring_btn_rect = recurring_button.get_rect(topleft=(120,190))
    def _draw_toggle_aura(rect): 
        aura = pygame.Surface((rect.width + 8, rect.height + 8), pygame.SRCALPHA); pygame.draw.rect(aura, (0,255,0,70), aura.get_rect(), border_radius=8); screen.blit(aura, (rect.x - 4, rect.y - 4))
    if time_toggle_on: _draw_toggle_aura(time_btn_rect)
    if recurring_toggle_on: _draw_toggle_aura(recurring_btn_rect)
    screen.blit(time_button, time_btn_rect.topleft)
    screen.blit(recurring_button, recurring_btn_rect.topleft)


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

    # --- Start Time (draw-only) ---
    def _fmt_time_display(t):
        # expects [HH, MM] or similar; safe fallback
        try:
            if isinstance(t, (list, tuple)) and len(t) >= 2:
                return f"{int(t[0]):02d}:{int(t[1]):02d}"
        except Exception:
            pass
        return "HH:MM"  # placeholder

    # position to the right of the day box; same y-level
    _START_TIME_X = day_input_box_recurring_shifted.right + 20  # tweak horizontally later
    _START_TIME_W = 120
    _START_TIME_H = 50
    start_time_input_box = pygame.Rect(_START_TIME_X, day_input_box_recurring_shifted.y, _START_TIME_W, _START_TIME_H)

    # spinner buttons for start time (draw-only for now)
    start_time_up_button   = pygame.Rect(start_time_input_box.right - 20, start_time_input_box.y + 7, 15, 15)
    start_time_down_button = pygame.Rect(start_time_input_box.right - 20, start_time_input_box.y + 25, 15, 15)



    def _render_month_box(active, rect, month_num):
        global caret_month
        pygame.draw.rect(screen, background_color if time_toggle_on else due_date_infill_color, rect, 0)
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
        pygame.draw.rect(screen, background_color if time_toggle_on else due_date_infill_color, rect, 0)
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
        screen.blit(font.render("Spoons:", True, WHITE),(spoon_input_box.x - 15, y_pos["spoons_label"]))

        small_label_shift = 5

        screen.blit(small_font.render("How Often:", True, WHITE), (how_often_input_box.x + 10, y_pos["spoons_label"] + small_label_shift))
        # while active: keep unit visible, hide default "1" if the buffer is empty
        _ho_txt = (how_often_typed if input_active == "how_often" else str(task_how_often)) + " days"
        draw_input_box(screen, how_often_input_box, input_active == "how_often", _ho_txt, DARK_SLATE_GRAY, DARK_SLATE_GRAY, False, background_color, "light")
        if input_active == "how_often" and _caret_visible():
            x0, y0 = how_often_input_box.x + 10, how_often_input_box.y + 8
            # caret goes after the typed digits (before the space in " days")
            cx = _caret_x(font, how_often_typed, x0)
            pygame.draw.line(screen, LIGHT_GRAY, (cx, y0), (cx, y0 + font.get_height()), 2)

        screen.blit(small_font.render("How Long:", True, WHITE), (how_long_input_box.x + 10, y_pos["spoons_label"] + small_label_shift))
        _hl_txt = (how_long_typed if input_active == "how_long" else str(task_how_long)) + " weeks"
        draw_input_box(screen, how_long_input_box, input_active == "how_long", _hl_txt, DARK_SLATE_GRAY, DARK_SLATE_GRAY, False, background_color, "light")
        if input_active == "how_long" and _caret_visible():
            x0, y0 = how_long_input_box.x + 10, how_long_input_box.y + 8
            cx = _caret_x(font, how_long_typed, x0)
            pygame.draw.line(screen, LIGHT_GRAY, (cx, y0), (cx, y0 + font.get_height()), 2)

        screen.blit(small_font.render("Repetitions:", True, WHITE), (repetitions_amount_input_box.x + 7, y_pos["spoons_label"] + small_label_shift))
        _hr_txt = (repetitions_typed if input_active == "repetitions" else str(task_repetitions_amount)) + " times"
        draw_input_box(screen, repetitions_amount_input_box, input_active == "repetitions", _hr_txt, DARK_SLATE_GRAY, DARK_SLATE_GRAY, False, background_color, "light")
        if input_active == "repetitions" and _caret_visible():
            x0, y0 = repetitions_amount_input_box.x + 10, repetitions_amount_input_box.y + 8
            cx = _caret_x(font, repetitions_typed, x0)
            pygame.draw.line(screen, LIGHT_GRAY, (cx, y0), (cx, y0 + font.get_height()), 2)

        # draw a small barrier under the arrow area so clicks don't fall through to the input field
        barrier_w = 24
        for base_rect in (how_often_input_box, how_long_input_box, repetitions_amount_input_box):
            barrier_rect = pygame.Rect(base_rect.right - barrier_w, base_rect.y + 4, barrier_w - 4, base_rect.height - 8)
            pygame.draw.rect(screen, due_date_infill_color, barrier_rect)

        # spinner buttons for all recurring inputs (draw-only)
        for btn in (
            how_often_up_button, how_often_down_button,
            how_long_up_button, how_long_down_button,
            repetitions_amount_up_button, repetitions_amount_down_button
        ):
            pygame.draw.rect(screen, due_date_infill_color, btn)

        # arrows on the buttons
        screen.blit(up_arrow,   (how_often_up_button.x - 9, how_often_up_button.y))
        screen.blit(down_arrow, (how_often_down_button.x - 12, how_often_down_button.y))

        screen.blit(up_arrow,   (how_long_up_button.x - 9, how_long_up_button.y))
        screen.blit(down_arrow, (how_long_down_button.x - 12, how_long_down_button.y))

        screen.blit(up_arrow,   (repetitions_amount_up_button.x - 9, repetitions_amount_up_button.y))
        screen.blit(down_arrow, (repetitions_amount_down_button.x - 12, repetitions_amount_down_button.y))


    else:
        screen.blit(font.render("Spoons:", True, WHITE),(360, y_pos["spoons_label"]))

    if time_toggle_on:
        screen.blit(font.render("Due Date:", True, WHITE),(345 - time_shift + 10, y_pos["due_date_label"]))
        _render_month_box(input_active == "month", month_input_box_recurring_shifted, task_month)
        _render_day_box(input_active == "day", day_input_box_recurring_shifted, int(task_day))

        for btn in (
            month_up_button_recurring_shifted, month_down_button_recurring_shifted,
            day_up_button_recurring_shifted,   day_down_button_recurring_shifted
        ):
            pygame.draw.rect(screen, due_date_infill_color, btn)
        screen.blit(up_arrow,   (month_up_button_recurring_shifted.x - 9, month_up_button_recurring_shifted.y))
        screen.blit(down_arrow, (month_down_button_recurring_shifted.x - 12, month_down_button_recurring_shifted.y))
        screen.blit(up_arrow,   (day_up_button_recurring_shifted.x - 9, day_up_button_recurring_shifted.y))
        screen.blit(down_arrow, (day_down_button_recurring_shifted.x - 12, day_down_button_recurring_shifted.y))

        # Start Time label + box
        screen.blit(font.render("Start Time:", True, WHITE),(start_time_input_box.x - 10, y_pos["due_date_label"]))
        pygame.draw.rect(screen, background_color, start_time_input_box, 0)

        # default shown should be current time if start_time is unset/invalid
        try:
            disp_time = _fmt_time_display(start_time)
        except Exception:
            hh, mm = _now_hh_mm()
            disp_time = f"{hh:02d}:{mm:02d}"

        # when active: always show the raw typed digits (may be empty) and caret; otherwise: HH:MM
        if input_active == "start_time":
            show_txt = start_time_typed  # no colon; may be empty on first focus
            is_active = True
        else:
            show_txt = disp_time          # HH:MM
            is_active = False

        draw_input_box(
            screen, start_time_input_box, is_active, show_txt,
            DARK_SLATE_GRAY, DARK_SLATE_GRAY, False, background_color, "light"
        )
        if input_active == "start_time" and _caret_visible():
            x0, y0 = start_time_input_box.x + 10, start_time_input_box.y + 8
            cx = _caret_x(font, start_time_typed, x0)
            pygame.draw.line(screen, LIGHT_GRAY, (cx, y0), (cx, y0 + font.get_height()), 2)


        # Start Time spinner buttons + arrows (draw-only)
        for btn in (start_time_up_button, start_time_down_button):
            pygame.draw.rect(screen, due_date_infill_color, btn)
        screen.blit(up_arrow,   (start_time_up_button.x - 9, start_time_up_button.y))
        screen.blit(down_arrow, (start_time_down_button.x - 12, start_time_down_button.y))



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

# typed buffers for editable fields
start_time_typed = ""           # raw digits while editing (e.g., "930", "1230")
how_often_typed = ""            # raw digits while editing (no unit)
how_long_typed = ""             # raw digits while editing (no unit)
repetitions_typed = ""          # raw digits while editing (no unit)

# carets
caret_task = 0
caret_month = 0
caret_day = 0
caret_spoons = 0
caret_start_time = 0
caret_how_often = 0
caret_how_long = 0
caret_repetitions = 0

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

# ---- Time + integer field commits ----
def _now_hh_mm():
    n = datetime.now()
    return n.hour, n.minute

def _start_time_from_digits(d):
    """Parse 'H', 'HH', 'HMM', 'HHMM' into (hh, mm) with clamping."""
    d = "".join(ch for ch in d if ch.isdigit())[:4]
    if not d:
        return _now_hh_mm()
    if len(d) <= 2:
        hh = int(d)
        return max(0, min(23, hh)), 0
    hh = int(d[:-2]) if d[:-2] else 0
    mm = int(d[-2:])
    hh = max(0, min(23, hh))
    mm = max(0, min(59, mm))
    return hh, mm

def _start_time_digits(hh, mm):
    return f"{int(hh):02d}{int(mm):02d}"

def _commit_start_time(global_state, start_time_list):
    """Commit typed digits to start_time list; if empty, keep current value."""
    s = global_state["start_time_typed"]
    if s != "":
        hh, mm = _start_time_from_digits(s)
        start_time_list[0], start_time_list[1] = hh, mm
    global_state["start_time_typed"] = ""
    return start_time_list

def _commit_positive_int(global_state, key_name, current_val, default_val=1, min_val=1, max_val=None):
    """Commit a typed numeric buffer into an int with bounds; empty -> default."""
    raw = global_state[key_name]
    if raw.isdigit():
        v = int(raw)
        if max_val is not None: v = min(max_val, v)
        v = max(min_val, v)
        current_val = v
    else:
        current_val = default_val
    global_state[key_name] = ""
    return current_val

def _add_task_entry(current_task, current_spoons, folder, task_date, current_time, lists_tuple,
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

    if recurring_toggle_on:
        for i in range(task_repetitions_amount):
            actual_date = task_date + timedelta(days=i * task_how_often)
            days_left = (actual_date - current_time).days + 1
            _push([current_task, int(current_spoons), 0, days_left, actual_date,
                   start_time_4, [0,0,0,0], []])
    else:
        _push([current_task, int(current_spoons), 0, days_till_due, task_date,
               start_time_4, [0,0,0,0], []])

def logic_input_tasks(event,screen,current_task,current_spoons,folder,task_month,task_day,task_how_often,task_how_long,task_repetitions_amount,time_toggle_on,recurring_toggle_on,max_days,input_active,homework_tasks_list,chores_tasks_list,work_tasks_list,misc_tasks_list,exams_tasks_list,projects_tasks_list, start_time):
    global month_typed, day_typed, caret_task, caret_month, caret_day, caret_spoons
    global start_time_typed, how_often_typed, how_long_typed, repetitions_typed
    global caret_start_time, caret_how_often, caret_how_long, caret_repetitions

    # default start_time -> current time if not provided
    try:
        _ = int(start_time[0]); _ = int(start_time[1])
    except Exception:
        now = datetime.now()
        start_time[:] = [now.hour, now.minute]

    page = "input_tasks"
    screen_h = screen.get_height()
    y_pos = {k: int(v * screen_h) for k, v in layout_heights.items()}

    folder_list = ["homework", "chores", "work", "misc", "exams", "projects"]
    done_button_y_pos = 144 + 60 * folder_list.index(folder)

    task_input_box = pygame.Rect(250, y_pos["task_input_line"], 300, 50)

    # Needed in this scope too
    done_button = pygame.Rect(630, done_button_y_pos, 50, 32)
    time_btn_rect = time_button.get_rect(topleft=(120, 140))
    recurring_btn_rect = recurring_button.get_rect(topleft=(120, 190))

    _recurring_vshift = y_pos["spoons_input_line"] - y_pos["due_date_input_line"]
    _SPOONS_X_BASE = 375
    _SPOONS_X_SHIFTED = 180  # must match draw_input_tasks
    spoon_input_box = pygame.Rect(
        _SPOONS_X_SHIFTED if recurring_toggle_on else _SPOONS_X_BASE,
        y_pos["spoons_input_line"], 50, 50
    )

    gap = 20  # must match draw_input_tasks

    how_often_input_box   = pygame.Rect(spoon_input_box.x + spoon_input_box.width + gap, y_pos["spoons_input_line"], 120, 50)
    how_often_up_button   = pygame.Rect(how_often_input_box.right - 20, y_pos["spoons_input_line"] + 7, 15, 15)
    how_often_down_button = pygame.Rect(how_often_input_box.right - 20, y_pos["spoons_input_line"] + 25, 15, 15)

    how_long_input_box    = pygame.Rect(how_often_input_box.x + how_often_input_box.width + gap, y_pos["spoons_input_line"], 120, 50)
    how_long_up_button    = pygame.Rect(how_long_input_box.right - 20, y_pos["spoons_input_line"] + 7, 15, 15)
    how_long_down_button  = pygame.Rect(how_long_input_box.right - 20, y_pos["spoons_input_line"] + 25, 15, 15)

    repetitions_amount_input_box   = pygame.Rect(how_long_input_box.x + how_long_input_box.width + gap, y_pos["spoons_input_line"], 120, 50)
    repetitions_amount_up_button   = pygame.Rect(repetitions_amount_input_box.right - 20, y_pos["spoons_input_line"] + 7, 15, 15)
    repetitions_amount_down_button = pygame.Rect(repetitions_amount_input_box.right - 20, y_pos["spoons_input_line"] + 25, 15, 15)


    month_input_box_normal = pygame.Rect(280, y_pos["due_date_input_line"], 160, 50)
    month_up_button_normal = pygame.Rect(420, int(y_pos["due_date_input_line"] + 7), 15, 15)
    month_down_button_normal = pygame.Rect(420, int(y_pos["due_date_input_line"] + 25), 15, 15)
    day_input_box_normal   = pygame.Rect(465, y_pos["due_date_input_line"], 70, 50)
    day_up_button_normal   = pygame.Rect(515, int(y_pos["due_date_input_line"] + 7), 15, 15)
    day_down_button_normal = pygame.Rect(515, int(y_pos["due_date_input_line"] + 25), 15, 15)

    time_shift = 80  # must match draw_input_tasks

    month_input_box_recurring_shifted = pygame.Rect(280 - time_shift, y_pos["due_date_input_line"], 160, 50)
    month_up_button_recurring_shifted = pygame.Rect(420 - time_shift, int(y_pos["due_date_input_line"] + 7), 15, 15)
    month_down_button_recurring_shifted = pygame.Rect(420 - time_shift, int(y_pos["due_date_input_line"] + 25), 15, 15)
    day_input_box_recurring_shifted   = pygame.Rect(465 - time_shift, y_pos["due_date_input_line"], 70, 50)
    day_up_button_recurring_shifted   = pygame.Rect(515 - time_shift, int(y_pos["due_date_input_line"] + 7), 15, 15)
    day_down_button_recurring_shifted = pygame.Rect(515 - time_shift, int(y_pos["due_date_input_line"] + 25), 15, 15)


    # --- Start Time geometry (must follow day_input_box_recurring_shifted) ---
    _START_TIME_X = day_input_box_recurring_shifted.right + 20
    _START_TIME_W = 120
    _START_TIME_H = 50
    start_time_input_box = pygame.Rect(_START_TIME_X, day_input_box_recurring_shifted.y, _START_TIME_W, _START_TIME_H)
    start_time_up_button   = pygame.Rect(start_time_input_box.right - 20, start_time_input_box.y + 7, 15, 15)
    start_time_down_button = pygame.Rect(start_time_input_box.right - 20, start_time_input_box.y + 25, 15, 15)



    def _active_month_rect():
        return month_input_box_recurring_shifted if time_toggle_on else month_input_box_normal

    def _active_day_rect():
        return day_input_box_recurring_shifted if time_toggle_on else day_input_box_normal


    if event.type == pygame.MOUSEBUTTONDOWN:
        if time_btn_rect.collidepoint(event.pos):
            time_toggle_on = not time_toggle_on
        elif recurring_btn_rect.collidepoint(event.pos):
            if input_active == "month": task_month = _commit_month({"month_typed": month_typed}, task_month, months); month_typed = ""
            if input_active == "day": task_day = _commit_day({"day_typed": day_typed}, task_day, max_days); day_typed = ""
            recurring_toggle_on = not recurring_toggle_on


        # --- 1) SPINNER BUTTONS FIRST (so they don't trigger edit mode) ---
        clicked_spinner = False
        if time_toggle_on:
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

            month_rect_edit = month_rect_full.copy(); month_rect_edit.width = max(10, month_rect_edit.width - 24)
            day_rect_edit   = day_rect_full.copy();  day_rect_edit.width   = max(10, day_rect_edit.width   - 20)
            start_time_rect_edit = start_time_input_box.copy(); start_time_rect_edit.width = max(10, start_time_rect_edit.width - 24)

            how_often_rect_edit      = how_often_input_box.copy();      how_often_rect_edit.width      = max(10, how_often_rect_edit.width      - 24)
            how_long_rect_edit       = how_long_input_box.copy();       how_long_rect_edit.width       = max(10, how_long_rect_edit.width       - 24)
            repetitions_rect_edit    = repetitions_amount_input_box.copy(); repetitions_rect_edit.width = max(10, repetitions_rect_edit.width    - 24)

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
            elif time_toggle_on and start_time_rect_edit.collidepoint(event.pos):
                input_active = "start_time"
                # Clear for free typing (show nothing while active)
                start_time_typed = ""
                caret_start_time = 0

            # numeric recurring inputs: focus -> erase default "1", keep unit text, caret at start of number
            elif how_often_rect_edit.collidepoint(event.pos):
                input_active = "how_often"
                how_often_typed = ""  # hide default 1 on focus
                caret_how_often = 0
            elif how_long_rect_edit.collidepoint(event.pos):
                input_active = "how_long"
                how_long_typed = ""   # hide default 1 on focus
                caret_how_long = 0
            elif repetitions_rect_edit.collidepoint(event.pos):
                input_active = "repetitions"
                repetitions_typed = ""   # hide default 1 on focus
                caret_repetitions = 0
            elif spoon_input_box.collidepoint(event.pos):
                input_active = "spoons"
                if isinstance(current_spoons, int): current_spoons = ""
                caret_spoons = _index_from_click(font, current_spoons, event.pos[0], spoon_input_box.x + 10)
            else:
                # Clicking elsewhere commits any active edit box
                if input_active == "month":
                    task_month = _commit_month({"month_typed": month_typed}, task_month, months); month_typed = ""
                elif input_active == "day":
                    task_day = _commit_day({"day_typed": day_typed}, task_day, max_days); day_typed = ""
                elif input_active == "start_time":
                    start_time = _commit_start_time({"start_time_typed": start_time_typed}, start_time); start_time_typed = ""
                elif input_active == "how_often":
                    task_how_often = _commit_positive_int({"how_often_typed": how_often_typed}, "how_often_typed", task_how_often, default_val=1, min_val=1); how_often_typed = ""
                elif input_active == "how_long":
                    task_how_long = _commit_positive_int({"how_long_typed": how_long_typed}, "how_long_typed", task_how_long, default_val=1, min_val=1); how_long_typed = ""
                elif input_active == "repetitions":
                    task_repetitions_amount = _commit_positive_int({"repetitions_typed": repetitions_typed}, "repetitions_typed", task_repetitions_amount, default_val=1, min_val=1, max_val=26); repetitions_typed = ""
                input_active = False

        # Start Time spinner clicks (15-minute steps, 24h wrap)
        if time_toggle_on and start_time_up_button.collidepoint(event.pos):
            try:
                hh, mm = int(start_time[0]) % 24, int(start_time[1]) % 60
            except Exception:
                hh, mm = 0, 0
            mm += 15
            if mm >= 60: mm = 0; hh = (hh + 1) % 24
            start_time[0], start_time[1] = hh, mm
        elif time_toggle_on and start_time_down_button.collidepoint(event.pos):
            try:
                hh, mm = int(start_time[0]) % 24, int(start_time[1]) % 60
            except Exception:
                hh, mm = 0, 0
            mm -= 15
            if mm < 0: mm = 45; hh = (hh - 1) % 24
            start_time[0], start_time[1] = hh, mm

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
                    recurring_toggle_on, task_how_often, task_how_long, task_repetitions_amount,
                    start_time
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

        # Tab order:
        # with time: task -> month -> day -> start_time -> how_often -> how_long -> repetitions -> spoons -> task
        # without time: task -> month -> day -> how_often -> how_long -> repetitions -> spoons -> task
        tab_core = ["task","month","day", "spoons"]
        if time_toggle_on: tab_core = ["task","month","day","start_time","spoons"]
        if recurring_toggle_on: tab_core = ["task","month","day","spoons", "how_often","how_long","repetitions"]
        if time_toggle_on and recurring_toggle_on: tab_core = ["task","month","day","start_time","spoons", "how_often","how_long","repetitions"]
        tab_order = tab_core


        if event.key == pygame.K_TAB:
            # commit fields you're leaving
            if input_active == "month":
                task_month = _commit_month({"month_typed": month_typed}, task_month, months); month_typed = ""
            elif input_active == "day":
                task_day = _commit_day({"day_typed": day_typed}, task_day, max_days); day_typed = ""
            elif input_active == "start_time":
                start_time = _commit_start_time({"start_time_typed": start_time_typed}, start_time)  # buffer cleared inside
                start_time_typed = ""
            elif input_active == "how_often":
                task_how_often = _commit_positive_int({"how_often_typed": how_often_typed}, "how_often_typed", task_how_often, default_val=1, min_val=1)
                how_often_typed = ""
            elif input_active == "how_long":
                task_how_long = _commit_positive_int({"how_long_typed": how_long_typed}, "how_long_typed", task_how_long, default_val=1, min_val=1)
                how_long_typed = ""
            elif input_active == "repetitions":
                task_repetitions_amount = _commit_positive_int({"repetitions_typed": repetitions_typed}, "repetitions_typed", task_repetitions_amount, default_val=1, min_val=1, max_val=26)
                repetitions_typed = ""

            # move focus
            try:
                i = tab_order.index(input_active) if input_active in tab_order else -1
                input_active = tab_order[(i + 1) % len(tab_order)]
            except ValueError:
                input_active = "task"

            # set carets / prefill on entry
            if input_active == "task":
                caret_task = len(current_task)
            elif input_active == "month":
                caret_month = 0
            elif input_active == "day":
                caret_day = 0
            elif input_active == "start_time":
                start_time_typed = ""
                caret_start_time = 0
            elif input_active == "how_often":
                how_often_typed = ""; caret_how_often = 0
            elif input_active == "how_long":
                how_long_typed = ""; caret_how_long = 0
            elif input_active == "repetitions":
                repetitions_typed = ""; caret_repetitions = 0
            elif input_active == "spoons":
                caret_spoons = 0

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

        elif input_active == "start_time":
            # digits only; no colon while editing
            if event.key == pygame.K_RETURN:
                start_time = _commit_start_time({"start_time_typed": start_time_typed}, start_time); start_time_typed = ""
                # advance to next editable: how_often
                input_active = "how_often"; caret_how_often = 0; how_often_typed = ""
            elif event.key == pygame.K_BACKSPACE:
                if len(start_time_typed) > 0:
                    start_time_typed = start_time_typed[:-1]
                    caret_start_time = max(0, caret_start_time - 1)
            elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                # optional: nudge minutes in 15-min steps with arrows
                try: hh, mm = int(start_time[0]) % 24, int(start_time[1]) % 60
                except Exception: hh, mm = _now_hh_mm()
                if event.key == pygame.K_RIGHT:
                    mm += 15; 
                    if mm >= 60: mm = 0; hh = (hh + 1) % 24
                else:
                    mm -= 15; 
                    if mm < 0: mm = 45; hh = (hh - 1) % 24
                start_time[0], start_time[1] = hh, mm
                start_time_typed = _start_time_digits(hh, mm)
                caret_start_time = len(start_time_typed)
            else:
                ch = event.unicode
                if ch.isdigit() and len(start_time_typed) < 4:
                    start_time_typed += ch
                    caret_start_time = len(start_time_typed)

        elif input_active == "how_often":
            if event.key == pygame.K_RETURN:
                task_how_often = _commit_positive_int({"how_often_typed": how_often_typed}, "how_often_typed", task_how_often, default_val=1, min_val=1); how_often_typed = ""
                input_active = "how_long"; caret_how_long = 0; how_long_typed = ""
            elif event.key == pygame.K_BACKSPACE:
                if len(how_often_typed) > 0:
                    how_often_typed = how_often_typed[:-1]; caret_how_often = max(0, caret_how_often - 1)
            else:
                ch = event.unicode
                if ch.isdigit() and len(how_often_typed) < 3:
                    how_often_typed += ch; caret_how_often = len(how_often_typed)

        elif input_active == "how_long":
            if event.key == pygame.K_RETURN:
                task_how_long = _commit_positive_int({"how_long_typed": how_long_typed}, "how_long_typed", task_how_long, default_val=1, min_val=1); how_long_typed = ""
                input_active = "repetitions"; caret_repetitions = 0; repetitions_typed = ""
            elif event.key == pygame.K_BACKSPACE:
                if len(how_long_typed) > 0:
                    how_long_typed = how_long_typed[:-1]; caret_how_long = max(0, caret_how_long - 1)
            else:
                ch = event.unicode
                if ch.isdigit() and len(how_long_typed) < 3:
                    how_long_typed += ch; caret_how_long = len(how_long_typed)

        elif input_active == "repetitions":
            if event.key == pygame.K_RETURN:
                task_repetitions_amount = _commit_positive_int({"repetitions_typed": repetitions_typed}, "repetitions_typed", task_repetitions_amount, default_val=1, min_val=1, max_val=26); repetitions_typed = ""
                input_active = "spoons"; caret_spoons = 0
            elif event.key == pygame.K_BACKSPACE:
                if len(repetitions_typed) > 0:
                    repetitions_typed = repetitions_typed[:-1]; caret_repetitions = max(0, caret_repetitions - 1)
            else:
                ch = event.unicode
                if ch.isdigit() and len(repetitions_typed) < 2:
                    repetitions_typed += ch; caret_repetitions = len(repetitions_typed)


        elif input_active == "spoons":
            if isinstance(current_spoons, int): current_spoons = ""
            if event.key == pygame.K_RETURN:
                if current_task and current_spoons:
                    task_date = datetime(current_time.year, task_month, int(task_day))
                    _add_task_entry(
                        current_task, current_spoons, folder, task_date, current_time,
                        (homework_tasks_list,chores_tasks_list,work_tasks_list,misc_tasks_list,exams_tasks_list,projects_tasks_list),
                        recurring_toggle_on, task_how_often, task_how_long, task_repetitions_amount,
                        start_time
                    )
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


    return (input_active,page,folder,time_toggle_on,recurring_toggle_on,current_task,current_spoons,task_month,task_day,homework_tasks_list,chores_tasks_list,work_tasks_list,misc_tasks_list,exams_tasks_list,projects_tasks_list,task_how_often,task_how_long,task_repetitions_amount, start_time)
