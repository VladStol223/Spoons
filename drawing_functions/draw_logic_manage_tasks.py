# draw_logic_manage_tasks.py
from config import *
from drawing_functions.draw_rounded_button import draw_rounded_button
from drawing_functions.draw_input_box import draw_input_box, InputBox, logic_input_box
import pygame
import math
import calendar
from datetime import datetime, timedelta

input_boxes = {
    "task":        InputBox(None, text="", multiline=False, fontsize=0.06, box_type="text"),
    "spoons_cost": InputBox(None, text="", multiline=False, fontsize=0.06, box_type="spoons"),
    "spoons_done": InputBox(None, text="", multiline=False, fontsize=0.06, box_type="spoons"), 
    "description": InputBox(None, text="", multiline=True,  fontsize=0.05, box_type="text"),
    "year":        InputBox(None, text="", multiline=False, fontsize=0.06, box_type="number"),
    "month":       InputBox(None, text="", multiline=False, fontsize=0.06, box_type="month"),
    "day":         InputBox(None, text="", multiline=False, fontsize=0.06, box_type="day"),
    "start_time":  InputBox(None, text="", multiline=False, fontsize=0.06, box_type="time"),
}


# Globals for click handling
remove_buttons     = []  # (pygame.Rect, idx)
frame_buttons      = []  # (pygame.Rect, task_index, frame_index)
focus_buttons = []

# --- Focus mode timer state (per-task focus) ---
focus_timer_active       = False
focus_timer_paused       = False
focus_timer_start        = None
focus_timer_last_update  = None
focus_total_secs         = 0.0
focus_remaining_secs     = 0.0
focus_total_spoons       = 0          # how many spoon-intervals this focus session covers
focus_spoons_spent       = 0          # how many spoon-intervals have actually fired

# Start / Pause / Exit buttons in focus UI
focus_start_rect         = None
focus_pause_rect         = None
focus_exit_rect          = None

# Spoon-debt / out-of-spoons popup
focus_popup_text         = ""
focus_popup_start        = None       # datetime
focus_popup_duration     = 5.0        # seconds
focus_warning_shown_for_debt = False  # only show debt warning once per session

# Visual timer state (for smooth drawing independent of events)
focus_visual_start_time   = None      # datetime when focus session started
focus_pause_start_visual  = None      # datetime when pause began
focus_pause_accum_visual  = 0.0       # total paused seconds

# Focus timer uses the same time_per_spoon from config
deg_per_spoon_focus      = time_per_spoon * 6

# Globals for click handling
edit_buttons       = []  # (pygame.Rect, field_name)
cancel_button_rect = None
done_button_rect   = None
add_task_button_rect = None

# State
currently_editing = None  # index of the task being edited
edit_state = {}
focus_task = None

spoons_xp = 0

# Dropdown state + click targets
expanded_label_tasks = set()  # indices of tasks whose label dropdown is open
label_buttons = []            # (pygame.Rect, task_index)

# Label chip hitboxes + drag state
label_chip_buttons = []   # (pygame.Rect, task_index, label_index)
dragging_label = None     # {"task_idx": int, "label_idx": int, "text": str}

# Temporary favorites (will be saved to data.json later)
favorites_labels = []  # this will be rebound per page

description_toggle = toggleButtons['taskDescriptionToggle']

def set_favorites_binding(fav_list_ref):
    """
    Bind the Favorites panel in this module to a *live* list that belongs to the current folder slot.
    Mutations (adding/removing/reordering) will directly update the list in main.label_favorites[slot].
    """
    global favorites_labels
    favorites_labels = fav_list_ref if isinstance(fav_list_ref, list) else []


# --- NEW globals for drag/drop targets + hover indexes ---
favorites_chip_buttons = []  # (pygame.Rect, fav_index)
favorites_drop_rect = None   # pygame.Rect (inner content of favorites panel)
task_drop_rects = {}         # {task_idx: pygame.Rect for that task's labels area}
hover_insert_index_per_task = {}  # {task_idx: int or None}
dropdown_outer_rects = {}    # {task_idx: pygame.Rect}

# --- New label creation state ---
new_label_active_task = None   # int | None  (task idx currently typing a new label for)
new_label_text = ""            # current text being typed
new_label_rect = None          # pygame.Rect of the active "new label" chip for click-away commit
new_label_buttons = []         # (pygame.Rect, task_index) for non-active "new label" chips

# Scrolling layout constants
CONTENT_TOP     = 100   # Where content starts
VIEWPORT_HEIGHT = 420   # Visible content height
SCROLL_X        = 910   # Scrollbar X
SCROLL_Y        = 140   # Scrollbar Y
TRACK_HEIGHT    = 330   # Scrollbar track height

# Max width equals the width of the reference string using the same font as your task input
TASK_NAME_REF = "thisisthecharacterlimiit?y"
MAX_TASK_PIXEL_WIDTH = font.size(TASK_NAME_REF)[0]

DARK_BROWN      = (40, 25, 22)
LIGHT_BROWN     = (85, 50, 43)
VERY_DARK_BROWN = (20, 12, 10)
DROPDOWN_BROWN = (65, 40, 33)

MONTHS = ["January", "February","March","April","May","June","July","August","September","October","November","December"]

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

def _extract_sortable_start_time(task):
    """
    Returns a sortable integer HHMM.
    Tasks with no start time return a large number so they go last.
    """
    try:
        # dict format
        if isinstance(task, tuple):
            st = task[7]   # start time list [hh,mm,...]
        else:
            st = task.get("start_time", None)

        if isinstance(st, (list, tuple)) and len(st) >= 2:
            hh = int(st[0])
            mm = int(st[1])
            return hh * 100 + mm

        # string "HHMM"
        if isinstance(st, str) and st.isdigit() and len(st) >= 3:
            st = st.zfill(4)
            return int(st[:2]) * 100 + int(st[2:])
    except:
        pass

    return 9999  # tasks with no time go LAST

def _blit_task_name_fit(screen, text, x_left, y, x_limit, base_px):
    """
    Render `text` starting at x_left,y with a font size that fits entirely
    before `x_limit`. If it already fits at `base_px`, use that. Otherwise
    scale down but not below ~60% of base size (and not below 12px).
    """
    # Early guard: if there's no room, clamp to a tiny readable size
    min_px = 12
    base_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(base_px))
    width, _ = base_font.size(text)

    available = max(0, x_limit - x_left)
    if width <= available or available <= 0:
        surf = base_font.render(text, True, BLACK)  # type: ignore
        screen.blit(surf, (x_left, y))
        return

    scale = available / max(1, width)
    target_px = int(max(min_px, base_px * max(0.60, min(1.0, scale))))
    font_fit = pygame.font.Font("fonts/Stardew_Valley.ttf", target_px)
    surf = font_fit.render(text, True, BLACK)  # type: ignore
    screen.blit(surf, (x_left, y))

def draw_complete_tasks(
    screen,
    type,
    task_list,
    buttons,
    spoons,
    scroll_offset_px,
    background_color,
    icon_image,
    time_per_spoon
):
    """
    Draws the manage-tasks page, or the edit form if currently_editing is set.
    """
    global edit_buttons, remove_buttons, frame_buttons, label_buttons, label_chip_buttons, dragging_label
    global favorites_chip_buttons, favorites_drop_rect, task_drop_rects, hover_insert_index_per_task
    global dropdown_outer_rects, new_label_rect, new_label_buttons, focus_task, focus_buttons
    edit_buttons.clear()
    remove_buttons.clear()
    buttons.clear()
    frame_buttons.clear()
    label_buttons.clear()
    label_chip_buttons.clear()
    favorites_chip_buttons.clear()
    favorites_drop_rect = None
    task_drop_rects.clear()
    hover_insert_index_per_task.clear()
    dropdown_outer_rects.clear()
    new_label_buttons.clear()
    new_label_rect = None
    focus_buttons.clear()

    global add_task_button_rect
    add_task_button_rect = None
    exit_rect = None

    # If there are no tasks in this folder, draw "Add Task?" button
    if len(task_list) == 0:
        button_w, button_h = 200, 60
        screen_w, screen_h = screen.get_size()
        bx = (screen_w - button_w) // 2 + 25
        by = (screen_h - button_h) // 2

        add_task_button_rect = pygame.Rect(bx, by, button_w, button_h)
        draw_rounded_button(screen, add_task_button_rect, DARK_BROWN, WHITE, border_radius=12) #type: ignore

        font_btn = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen.get_height() * 0.05))
        text_surf = font_btn.render("Add Task?", True, WHITE) #type: ignore
        screen.blit(text_surf, (bx + (button_w - text_surf.get_width()) // 2, by + (button_h - text_surf.get_height()) // 2))

        return scroll_offset_px, 0, exit_rect


    # If we're editing, draw the edit UI instead of the list
    if currently_editing is not None:
        _draw_edit_form(screen, background_color, icon_image, spoons, task_list)
        return scroll_offset_px, 0, exit_rect
    
    if focus_task is not None:
        exit_rect = _draw_focus_mode(screen, task_list[focus_task])
        # Tick focus timer each time logic runs (time-based spoon spending)
        spoons, task_list = _update_focus_timer(task_list, spoons, spoons_debt_toggle, time_per_spoon)
        return scroll_offset_px, 0, exit_rect  # include exit_rect

    # --- existing drawing logic below ---
    border_img   = task_spoons_border
    label_img    = task_label_border
    label_img_blank = task_label_border_blank
    label_img_hover = task_label_border_hover
    label_img_hover_blank = task_label_border_hover_blank
    siding_img   = progress_bar_spoon_siding
    top_img      = progress_bar_spoon_top
    bottom_img   = pygame.transform.flip(top_img, False, True)
    right_siding = pygame.transform.flip(siding_img, True, False)
    remove_edit  = remove_edit_icons
    timer_background = avatarBackgrounds['timer_background']
    timer_hand = avatarBackgrounds['timer_hand']
    timer_top = avatarBackgrounds['timer_top']

    t       = pygame.time.get_ticks() / 300.0
    pulse   = (math.sin(t) + 1) / 2.0
    def lerp(a, b, f):
        return (
            int(a[0] + (b[0] - a[0]) * f),
            int(a[1] + (b[1] - a[1]) * f),
            int(a[2] + (b[2] - a[2]) * f),
        )

    overdue, upcoming, completed = [], {}, []
    for idx, (name, desc, cost, done, days, date, st, et, labels) in enumerate(task_list):
        if done >= cost:
            completed.append((idx, name, desc, cost, done, days, date, st, et, labels,))
        elif days < 0:
            overdue.append((idx, name, desc, cost, done, days, date, st, et, labels,))
        else:
            upcoming.setdefault(days, []).append((idx, name, desc, cost, done, days, date, st, et, labels,))

    # sort upcoming dict
    for d in upcoming:
        upcoming[d].sort(key=lambda t: _extract_sortable_start_time(t))
    overdue.sort(key=lambda x: x[4])
    days_sorted = sorted(upcoming.keys())

    heading_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen.get_height() * 0.05))
    task_font    = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen.get_height() * 0.06))

    y_cursor = CONTENT_TOP
    frame_h  = 2 + 34 + 2
    vpad     = (50 - frame_h) // 2

    if overdue:
        y_cursor += heading_font.render("Overdue", True, BLACK).get_height() + len(overdue)*60 + 4 #type: ignore
    for d in days_sorted:
        hdr = "Due Today" if d==0 else ("Due in 1 Day" if d==1 else f"Due in {d} Days")
        y_cursor += heading_font.render(hdr, True, BLACK).get_height() + len(upcoming[d])*60 + 4 #type: ignore
    if completed:
        y_cursor += heading_font.render("Completed", True, BLACK).get_height() + len(completed)*60 #type: ignore

    # scrollbar
    added_extra = 0

    y_cursor = CONTENT_TOP
    mx, my = pygame.mouse.get_pos()

    def draw_section(header, items, y_cur):
        if not items: return y_cur
        surf = heading_font.render(header, True, BLACK) #type: ignore
        h = surf.get_height()
        py = y_cur - scroll_offset_px
        if py + h >= CONTENT_TOP and py <= CONTENT_TOP + VIEWPORT_HEIGHT:
            screen.blit(surf, (150, py))
        y_cur += h

        for idx, name, desc, cost, done, days, date, st, et, labels, in items:
            by = y_cur - scroll_offset_px
            if not (by+50 < CONTENT_TOP or by > CONTENT_TOP+VIEWPORT_HEIGHT):
                # If this task’s label dropdown is open, draw it and push below rows down
                if idx in expanded_label_tasks:
                    # Attach directly under the task border; border is 50px tall at y=by
                    border_w = border_img.get_width()
                    attach_x = 145
                    attach_y = by + 49
                    attach_w = border_w - 14

                    # --- Compute dropdown inner height from BOTH task labels and favorites ---

                    LABEL_COLS = 3
                    ROW_H = max(28, label_border.get_height() + 8)

                    # Count labels + the "Add label" chip so height grows if it starts a new row
                    labels_count_for_layout = max(1, len(labels) + 1)  # +1 for the add chip
                    label_rows = math.ceil(labels_count_for_layout / LABEL_COLS)
                    labels_height_px = label_rows * ROW_H

                    # Favorites: 2 columns
                    FAV_COLS = 2
                    fav_chip_h = label_favorite_border.get_height() - 2
                    FAV_GAP_Y = 4
                    fav_rows = max(1, math.ceil(len(favorites_labels) / FAV_COLS))
                    favorites_height_px = fav_rows * (fav_chip_h + FAV_GAP_Y)

                    # Use the larger inner height, convert back to "rows" for the dropdown builder
                    inner_needed_px = max(labels_height_px, favorites_height_px)
                    rows_count = max(1, math.ceil(inner_needed_px / ROW_H))

                    # Build dropdown at the needed height
                    content_x, content_y, content_w, content_h = _draw_label_dropdown(
                        screen, attach_x, attach_y, attach_w, rows_count
                    )


                    tc_h = drop_down_top_corners.get_height()
                    bc_h = drop_down_corner.get_height()
                    outer_h = tc_h + content_h + bc_h
                    dropdown_outer_rects[idx] = pygame.Rect(attach_x, attach_y, attach_w, outer_h)

                    # --- Favorites panel docked to the right side of the dropdown ---
                    _draw_favorites_panel(
                        screen,
                        attach_x,            # same outer box x as dropdown
                        attach_y,            # same outer box y as dropdown
                        attach_w,            # same width as dropdown
                        content_y,           # inner content top from _draw_label_dropdown
                        content_h,           # inner content height from _draw_label_dropdown
                        favorites_labels     # temp list for now
                    )
                    
                    # Record where task-labels can accept drops (left of favorites)
                    task_labels_rect = pygame.Rect(content_x, content_y, attach_w - 260, content_h + 30)
                    task_drop_rects[idx] = task_labels_rect

                    inner_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen.get_height() * 0.045))

                    lb = label_border
                    lbw, lbh = lb.get_size()

                    row_h = max(28, lbh + 8)
                    PAD_X = 12
                    GAP_X = 7
                    COLS = 3

                    mx2, my2 = pygame.mouse.get_pos()

                    # 1) Build label/index lists from the ORIGINAL labels
                    orig_labels   = labels
                    orig_indices  = list(range(len(orig_labels)))

                    # 2) If dragging a label from THIS task, remove it from the working lists
                    working_labels  = orig_labels[:]         # copy
                    working_indices = orig_indices[:]        # copy

                    is_drag_from_this_task = (
                        dragging_label is not None
                        and dragging_label.get("source") == "task"
                        and dragging_label.get("task_idx") == idx
                    )

                    if is_drag_from_this_task:
                        drag_i = dragging_label["label_idx"]
                        if 0 <= drag_i < len(working_labels):
                            del working_labels[drag_i]
                            del working_indices[drag_i]

                    ADD_SENTINEL = "__ADD__"
                    working_labels.append(ADD_SENTINEL)
                    working_indices.append(None)  # not a real label index

                    # 3) Build slot rectangles
                    slot_rects = []
                    for i in range(len(working_labels)):  # includes ADD_SENTINEL
                        row = i // COLS
                        col = i % COLS
                        chip_x = content_x + PAD_X + col * (lbw + GAP_X)
                        chip_y = content_y + row * row_h + (row_h - lbh) // 2
                        slot_rects.append(pygame.Rect(chip_x, chip_y, lbw, lbh))

                    hover_insert_index = None
                    if dragging_label is not None:
                        drag_txt = dragging_label.get("text", "")
                        # reordering within same task is allowed; cross-source needs duplicate block
                        is_reorder = (
                            dragging_label.get("source") == "task"
                            and dragging_label.get("task_idx") == idx
                        )
                        allow_preview = True
                        if not is_reorder and drag_txt in orig_labels:
                            # DUPLICATE → block ALL preview positions (including tail)
                            allow_preview = False

                        if allow_preview:
                            # 1) Hovering a chip → insert BEFORE that chip
                            for i, r in enumerate(slot_rects):
                                if r.collidepoint(mx2, my2):
                                    hover_insert_index = i
                                    break

                            # 2) Gaps between chips → i+1
                            if hover_insert_index is None:
                                for i in range(len(slot_rects) - 1):
                                    left_r  = slot_rects[i]
                                    right_r = slot_rects[i+1]
                                    gap_r = pygame.Rect(left_r.right, left_r.y, right_r.left - left_r.right, lbh)
                                    if gap_r.width > 0 and gap_r.collidepoint(mx2, my2):
                                        hover_insert_index = i + 1
                                        break

                            # 3) End-zone: right of ADD or anywhere below ADD
                            if hover_insert_index is None and slot_rects:
                                last = slot_rects[-1]  # ADD_SENTINEL
                                right_tail = pygame.Rect(last.right, task_labels_rect.top,
                                                         max(0, task_labels_rect.right - last.right),
                                                         task_labels_rect.height)
                                below_tail = pygame.Rect(task_labels_rect.left, last.bottom,
                                                         task_labels_rect.width,
                                                         max(0, task_labels_rect.bottom - last.bottom))
                                if right_tail.collidepoint(mx2, my2) or below_tail.collidepoint(mx2, my2):
                                    hover_insert_index = len(working_labels) - 1  # end (just before ADD)
                        else:
                            # ensure no ghost is drawn or drop index stored
                            hover_insert_index = None


                    # 4) Display list + remember whether hover is the terminal end-slot
                    display_labels  = working_labels[:]
                    display_indices = working_indices[:]
                    is_end_slot = (hover_insert_index == len(working_labels) - 1) if hover_insert_index is not None else False
                    if hover_insert_index is not None:
                        display_labels.insert(hover_insert_index, "Temporary Label")
                        display_indices.insert(hover_insert_index, None)

                    # store either an int, "END", or None if suppressed
                    hover_insert_index_per_task[idx] = ("END" if is_end_slot else hover_insert_index)


                    # 5) Draw chips (includes ADD chip; no separate "+ New Label" pass later)
                    for disp_i, lab in enumerate(display_labels):
                        row = disp_i // COLS
                        col = disp_i % COLS
                        chip_x = content_x + PAD_X + col * (lbw + GAP_X)
                        chip_y = content_y + row * row_h + (row_h - lbh) // 2
                        chip_rect = pygame.Rect(chip_x, chip_y, lbw, lbh)

                        if lab == "Temporary Label":
                            ghost = lb.copy(); ghost.set_alpha(90)
                            screen.blit(ghost, (chip_x, chip_y))
                            continue

                        if lab == ADD_SENTINEL:
                            add_w, add_h = label_new_border.get_size()
                            screen.blit(label_new_border, (chip_x, chip_y))
                            if new_label_active_task == idx:
                                inner_font2 = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen.get_height() * 0.045))
                                text_surface = inner_font2.render(new_label_text, True, BLACK) #type: ignore
                                tx = chip_x + (add_w - text_surface.get_width()) // 2
                                ty = chip_y + (add_h - text_surface.get_height()) // 2 - 1
                                if new_label_text:
                                    screen.blit(text_surface, (tx, ty + 2))
                                if (pygame.time.get_ticks() // 400) % 2 == 0:
                                    caret_x = tx + text_surface.get_width()
                                    pygame.draw.line(screen, BLACK, (caret_x + 2, ty + 4), #type: ignore
                                                    (caret_x + 2, ty + text_surface.get_height() - 2), 2)
                                new_label_rect = chip_rect
                            else:
                                inner_font2 = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen.get_height() * 0.045))
                                ts = inner_font2.render("+ New Label", True, BLACK) #type: ignore
                                tx = chip_x + (add_w - ts.get_width()) // 2
                                ty = chip_y + (add_h - ts.get_height()) // 2 - 1
                                screen.blit(ts, (tx, ty + 2))
                                new_label_buttons.append((chip_rect, idx))
                            continue

                        # regular label chip
                        screen.blit(lb, (chip_x, chip_y))
                        ts = inner_font.render(lab, True, BLACK) #type: ignore
                        tx = chip_x + (lbw - ts.get_width()) // 2
                        ty = chip_y + (lbh - ts.get_height()) // 2 - 1
                        screen.blit(ts, (tx, ty + 2))

                        original_idx = display_indices[disp_i]
                        if original_idx is not None:
                            label_chip_buttons.append((chip_rect, idx, original_idx))


                    # Increase the vertical cursor and global extra height to push subsequent rows
                    dropdown_h = (content_y - (attach_y)) + content_h + (attach_y + (content_y - (attach_y)) + content_h - (attach_y + 0)) * 0  # keep simple; actual extra is top corners + content + bottom corners
                    # We already know outer_h = top_corners_h + inner_h + bottom_corners_h; recompute directly:
                    tc_h = drop_down_top_corners.get_height()
                    bc_h = drop_down_corner.get_height()
                    extra_h = tc_h + content_h + bc_h
                    y_cur += extra_h
                    added_extra_local = extra_h
                    # Track added extra to fix total height and scrollbar
                    nonlocal added_extra
                    added_extra += added_extra_local
                # border+name
                screen.blit(border_img, (138, by))
                # --- Time badge replaces label button in LIST view ---
                time_x, time_y = 395, by + 7
                if desc and desc.strip():
                    time_x = 358
                show_time = False
                hh = mm = 0
                try:
                    hh = int(st[0]) if isinstance(st, (list, tuple)) and len(st) >= 2 else 0
                    mm = int(st[1]) if isinstance(st, (list, tuple)) and len(st) >= 2 else 0
                    show_time = (hh != 0 or mm != 0)
                except Exception:
                    show_time = False

                if show_time:
                    tw, th = task_time_border.get_size()
                    screen.blit(task_time_border, (time_x - 26, time_y))
                    # time text centered on image
                    time_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen.get_height() * 0.050))
                    t_str = f"{hh:02d}:{mm:02d}"
                    ts = time_font.render(t_str, True, BLACK)  # type: ignore
                    tx = time_x + (tw - ts.get_width()) // 2 - 26
                    ty = time_y + (th - ts.get_height()) // 2 - 1
                    screen.blit(ts, (tx, ty + 2))

                name_x = 148
                name_y = by + 12

                if show_time:
                    # left edge of the time badge
                    x_limit = time_x - 26
                    base_px = int(screen.get_height() * 0.06)  # same as task_font size
                    _blit_task_name_fit(screen, name, name_x, name_y, x_limit, base_px)
                elif desc and desc.strip():
                    # left edge of the description toggle
                    toggle_w, toggle_h = description_toggle.get_size()
                    x_limit = 430 - toggle_w
                    base_px = int(screen.get_height() * 0.06)  # same as task_font size
                    _blit_task_name_fit(screen, name, name_x, name_y, x_limit, base_px)
                else:
                    ts = task_font.render(name, True, BLACK)  # type: ignore
                    screen.blit(ts, (name_x, name_y))

                # frames...
                region_x, region_w = 138+297, 450
                sp = 10
                fw = (region_w - (cost+1)*sp)//cost
                extra = (region_w - (cost*fw + (cost+1)*sp))//2

                rects = []
                for i in range(cost):
                    fx = region_x + sp + extra + i*(fw+sp)
                    fy = by + vpad
                    rects.append((fx, fy, fw, frame_h))
                    frame_buttons.append((pygame.Rect(fx, fy, fw, frame_h), idx, i))

                # hover index
                hover_index = -1
                if done < cost:
                    for i in range(done, cost):
                        fx, fy, fw2, fh2 = rects[i]
                        if pygame.Rect(fx, fy, fw2, fh2).collidepoint(mx, my):
                            hover_index = i
                            break

                # draw frames
                for i, (fx, fy, fw2, fh2) in enumerate(rects):
                    icon_override = None
                    # COMPLETED SPOON — now supports undo hover
                    if i < done:
                        # Check if the cursor is over ANY completed spoon
                        hovered_completed_index = None
                        for j in range(done):
                            jx, jy, jw, jh = rects[j]
                            if pygame.Rect(jx, jy, jw, jh).collidepoint(mx, my):
                                hovered_completed_index = j
                                break

                        # Should this spoon animate undo?
                        # YES if:
                        #   - it's completed (i < done)
                        #   - AND the hovered spoon index is <= this spoon index
                        if hovered_completed_index is not None and i >= hovered_completed_index:
                            # Animated undo effect
                            bg = (140, 60, 60)  # reddish tint
                            draw_icon = True

                            # inward pressed look
                            fx += 2
                            fy += 1

                            # pulse opacity between 128–255
                            alpha = int(128 + pulse * 127)
                            tmp = icon_image.copy()
                            tmp.set_alpha(alpha)
                            icon_override = tmp

                        else:
                            # normal completed spoon appearance
                            bg = LIGHT_BROWN
                            draw_icon = True
                            icon_override = None

                    elif i <= hover_index:
                        to_fill = (i+1)-done
                        if spoons >= to_fill:
                            bg, draw_icon = lerp(DARK_BROWN,LIGHT_BROWN,pulse), True
                        else:
                            bg, draw_icon = lerp(DARK_BROWN,VERY_DARK_BROWN,pulse), False
                    else:
                        bg, draw_icon = DARK_BROWN, False

                    pygame.draw.rect(screen, bg, (fx+2, fy+4, fw2-4, fh2-8))
                    screen.blit(siding_img, (fx, fy+2))
                    # tile...
                    iw = max(fw2-12,0)
                    tx, ty = fx+6, fy+3
                    d = 0
                    while d+10 <= iw:
                        screen.blit(top_img, (tx+d, ty)); d+=10
                    if iw-d>0:
                        screen.blit(top_img,(tx+d,ty),pygame.Rect(0,0,iw-d,2))
                    by2 = fy+2+34-3; d=0
                    while d+10 <= iw:
                        screen.blit(bottom_img, (tx+d, by2)); d+=10
                    if iw-d>0:
                        screen.blit(bottom_img,(tx+d,by2),pygame.Rect(0,0,iw-d,2))
                    screen.blit(right_siding, (fx+fw2-6, fy+2))

                    if draw_icon:
                        if icon_override:
                            tmp = icon_override
                        else:
                            tmp = icon_image.copy()
                            tmp.set_alpha(255 if i < done else 128)

                        iw2, ih2 = tmp.get_size()
                        cx = fx + 6 + iw // 2 - iw2 // 2
                        cy = fy + 2 + 17 - ih2 // 2
                        screen.blit(tmp, (cx, cy))

                # --- Description toggle and hover text ---
                if desc and desc.strip():
                    # align toggle icon to right edge of task box
                    toggle_w, toggle_h = description_toggle.get_size()
                    toggle_x = 430 - toggle_w  # adjust to your layout width if needed
                    toggle_y = by + (50 - toggle_h) // 2
                    toggle_rect = pygame.Rect(toggle_x, toggle_y, toggle_w, toggle_h)
                    screen.blit(description_toggle, (toggle_x, toggle_y))

                    # If hovering, show description text box
                    if toggle_rect.collidepoint(mx, my):
                        desc_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen.get_height() * 0.04))
                        wrap_width = 1250  # you can change this or tie to screen width

                        # --- Wrap description text ---
                        words = desc.split(" ")
                        wrapped_lines = []
                        current_line = ""

                        for word in words:
                            test_line = current_line + word + " "
                            if desc_font.size(test_line)[0] > wrap_width:
                                wrapped_lines.append(current_line.strip())
                                current_line = word + " "
                            else:
                                current_line = test_line
                        if current_line:
                            wrapped_lines.append(current_line.strip())

                        # --- Compute box size ---
                        max_line_width = max(desc_font.size(line)[0] for line in wrapped_lines)
                        line_height = desc_font.get_height()
                        padding_x, padding_y = 10, 6
                        box_w = max_line_width + padding_x * 2
                        box_h = len(wrapped_lines) * line_height + padding_y * 2

                        box_x = toggle_rect.right + 10
                        box_y = toggle_rect.centery - box_h // 2

                        # --- Draw background box ---
                        pygame.draw.rect(screen, (245, 235, 220), (box_x, box_y, box_w, box_h))
                        pygame.draw.rect(screen, (60, 40, 30), (box_x, box_y, box_w, box_h), 2)

                        # --- Render text lines ---
                        for i, line in enumerate(wrapped_lines):
                            ts2 = desc_font.render(line, True, (0, 0, 0))  # type: ignore
                            screen.blit(ts2, (box_x + padding_x, box_y + padding_y + i * line_height))


                # click target
                btn = pygame.Rect(138, by, 750, 50)
                buttons.append((btn, idx))

                # remove/edit icon
                ix, iy = remove_edit.get_size()
                remove_rect = pygame.Rect(118, by+5, ix, iy)
                if remove_rect.collidepoint(mx,my) or btn.collidepoint(mx,my):
                    screen.blit(remove_edit, remove_rect.topleft)
                    remove_buttons.append((remove_rect, idx))

                # --- Focus mode timer icon ---
                timer_small = pygame.transform.scale(timer_background, (32, 32))
                hand_small = pygame.transform.scale(timer_hand, (32, 32))
                top_small = pygame.transform.scale(timer_top, (32, 32))
                timer_rect = pygame.Rect(remove_rect.right + 735, remove_rect.y + 5, 30, 30)

                # show timer icon only on hover (same rule as remove_edit)
                if remove_rect.collidepoint(mx,my) or btn.collidepoint(mx,my) or timer_rect.collidepoint(mx,my):
                    screen.blit(timer_small, timer_rect.topleft)
                    screen.blit(hand_small, timer_rect.topleft)
                    screen.blit(top_small, timer_rect.topleft)

                # store hitbox
                focus_buttons.append((timer_rect, idx))


            y_cur += 52
        y_cur += 4
        return y_cur

    y_cursor = draw_section("Overdue", overdue, y_cursor)
    for d in days_sorted:
        hdr = "Due Today" if d==0 else ("Due in 1 Day" if d==1 else f"Due in {d} Days")
        y_cursor = draw_section(hdr, upcoming[d], y_cursor)
    y_cursor = draw_section("Completed", completed, y_cursor)

    # Recompute total height with dropdown expansion
    total_content_height = (y_cursor - CONTENT_TOP) + added_extra

    # Now clamp using the correct height
    max_scroll = max(0, total_content_height - VIEWPORT_HEIGHT)
    scroll_offset_px = max(0, min(scroll_offset_px, max_scroll))

    # Then draw the scrollbar using total_content_height
    if len(task_list) > 5:
        screen.blit(scroll_bar, (SCROLL_X, SCROLL_Y))
        if total_content_height <= VIEWPORT_HEIGHT:
            slider_h, slider_y = TRACK_HEIGHT, SCROLL_Y
        else:
            slider_h = max(int((VIEWPORT_HEIGHT/total_content_height)*TRACK_HEIGHT), 20)
            slider_y = SCROLL_Y + int((scroll_offset_px/(total_content_height-VIEWPORT_HEIGHT))*(TRACK_HEIGHT-slider_h))
        slider_x = SCROLL_X + (20 - scroll_bar_slider.get_width())//2
        screen.blit(pygame.transform.scale(scroll_bar_slider, (scroll_bar_slider.get_width(), slider_h)),
                    (slider_x, slider_y))

    # Draw the dragged label chip (overlay) if any
    if dragging_label is not None:
        mx2, my2 = pygame.mouse.get_pos()
        chip_img = label_favorite_border if dragging_label.get("source") == "fav" else label_border
        lbw, lbh = chip_img.get_size()

        chip_x = mx2 - lbw // 2
        chip_y = my2 - lbh // 2

        # Is cursor outside the active dropdown?
        open_task_idx = next(iter(expanded_label_tasks), None)
        outer_rect = dropdown_outer_rects.get(open_task_idx)
        deleting = (outer_rect is not None and not outer_rect.collidepoint(mx2, my2))

        # chip base
        screen.blit(chip_img, (chip_x, chip_y))

        inner_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen.get_height() * 0.045))
        ts = inner_font.render(dragging_label["text"], True, BLACK)  # type: ignore
        tx = chip_x + (lbw - ts.get_width()) // 2
        ty = chip_y + (lbh - ts.get_height()) // 2 - 1
        screen.blit(ts, (tx, ty + 2))

        # trashcan icon if deleting
        if deleting:
            tw, th = trashcan_image.get_size()
            screen.blit(trashcan_image, (chip_x + lbw - tw, chip_y + lbh - th + 2))

    #draw a small rect with background color to cover artifacts on the top of the screen
    pygame.draw.rect(screen, background_color, (100, 0, screen.get_width(), 80))

    return scroll_offset_px, total_content_height, None

def _start_focus_timer(task_list, time_per_spoon):
    """
    Initialize / restart the focus timer for the currently selected focus_task.
    Session length = (cost - done) spoons for that task.
    """
    global focus_timer_active, focus_timer_paused, focus_timer_start, focus_timer_last_update
    global focus_total_secs, focus_remaining_secs, focus_total_spoons, focus_spoons_spent
    global focus_warning_shown_for_debt
    global focus_visual_start_time, focus_pause_start_visual, focus_pause_accum_visual

    if focus_task is None:
        return

    if focus_task < 0 or focus_task >= len(task_list):
        return

    name, desc, cost, done, days, date, st, et, labels = task_list[focus_task]

    remaining_spoons_needed = max(0, cost - done)
    if remaining_spoons_needed <= 0:
        # Task already complete; nothing to time.
        return

    focus_total_spoons       = remaining_spoons_needed
    focus_total_secs         = remaining_spoons_needed * time_per_spoon * 60.0
    focus_remaining_secs     = focus_total_secs
    focus_spoons_spent       = 0

    # Core timer state
    focus_timer_start        = datetime.now()
    focus_timer_last_update  = None
    focus_timer_active       = True
    focus_timer_paused       = False
    focus_warning_shown_for_debt = False

    # Visual timer (for smooth draw independent of events)
    focus_visual_start_time   = focus_timer_start
    focus_pause_start_visual  = None
    focus_pause_accum_visual  = 0.0

def _update_focus_timer(task_list, spoons, spoons_debt_toggle, time_per_spoon):
    """
    Time-based focus logic:
    - Every time_per_spoon minutes:
        * spoons -= 1
        * current task.done += 1
    - If spoons_debt_toggle is False and spoons hits 0, timer PAUSES and
      shows an 'out of spoons' popup.
    - If spoons_debt_toggle is True, timer continues into negative spoons
      but shows a one-time 'debt' warning when crossing 0.
    """
    global focus_timer_active, focus_timer_paused, focus_timer_last_update
    global focus_remaining_secs, focus_spoons_spent
    global focus_popup_text, focus_popup_start, focus_warning_shown_for_debt

    if not focus_timer_active or focus_timer_paused or focus_task is None:
        return spoons, task_list

    if focus_task < 0 or focus_task >= len(task_list):
        focus_timer_active = False
        return spoons, task_list

    now = datetime.now()

    # First call after (re)start: just set last_update
    if focus_timer_last_update is None:
        focus_timer_last_update = now
        return spoons, task_list

    dt = (now - focus_timer_last_update).total_seconds()
    focus_timer_last_update = now

    if dt <= 0 or focus_total_secs <= 0 or focus_remaining_secs <= 0:
        focus_timer_active = False
        return spoons, task_list

    # Update remaining seconds
    focus_remaining_secs = max(0.0, focus_remaining_secs - dt)

    # How many ticks should have occurred total?
    seconds_per_tick = time_per_spoon * 60.0
    ticks_total      = int((focus_total_secs - focus_remaining_secs) // seconds_per_tick)

    # How many NEW ticks to apply this call?
    ticks_to_apply   = max(0, ticks_total - int(focus_spoons_spent))

    for _ in range(ticks_to_apply):
        if focus_task is None or focus_task < 0 or focus_task >= len(task_list):
            focus_timer_active = False
            break

        name, desc, cost, done, days, date, st, et, labels = task_list[focus_task]

        # Stop if task is already complete
        if done >= cost:
            focus_timer_active = False
            break

        prev_spoons = spoons

        # If user does NOT allow spoon debt and we are out of spoons → pause & popup
        if spoons <= 0 and not spoons_debt_toggle:
            focus_timer_paused = True
            focus_popup_text   = "You have run out of spoons, please rest before continuing focus mode."
            focus_popup_start  = now
            break

        # Spend one spoon and advance task progress
        spoons -= 1
        done   += 1
        focus_spoons_spent += 1

        # Save updated task tuple back
        task_list[focus_task] = (name, desc, cost, done, days, date, st, et, labels)

        # If user allows spoon debt, show warning once when crossing 0
        if spoons_debt_toggle and prev_spoons > 0 and spoons <= 0 and not focus_warning_shown_for_debt:
            focus_popup_text  = "Warning: You are now in spoon debt."
            focus_popup_start = now
            focus_warning_shown_for_debt = True

        # If we just finished the task, stop the timer
        if done >= cost:
            focus_timer_active = False
            break

    # Hard stop if time is over
    if focus_remaining_secs <= 0:
        focus_timer_active = False

    return spoons, task_list

def _draw_focus_mode(screen, task):
    """
    Renders focus mode:
    - Task preview with spoon frames
    - Circular timer using same art as input_spoons
    - Start / Restart button (left)
    - Pause / Unpause button (right)
    - Popup that fades away after 5 seconds when out of spoons or in debt
    """
    global focus_start_rect, focus_pause_rect, focus_exit_rect
    global focus_popup_text, focus_popup_start
    global focus_visual_start_time, focus_pause_start_visual, focus_pause_accum_visual

    name, desc, cost, done, days, date, st, et, labels = task

    screen_w, screen_h = screen.get_size()

    header_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen_h * 0.05))
    task_font   = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen_h * 0.06))
    timer_font  = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen_h * 0.047))
    button_font = header_font

    # --- Header (same rules as edit mode) ---
    now = datetime.now()
    days_left = (date - now).days + 1

    if done >= cost:
        header = "Completed"
    elif days_left < 0:
        header = "Overdue"
    elif days_left == 0:
        header = "Due Today"
    elif days_left == 1:
        header = "Due in 1 Day"
    else:
        header = f"Due in {days_left} Days"

    hdr = header_font.render(header, True, BLACK)  # type: ignore
    screen.blit(hdr, (140, 110))

    # --- Task border container ---
    border_img = task_spoons_border
    py = 105 + hdr.get_height() + 10
    screen.blit(border_img, (138, py))

    # Task name
    name_surf = task_font.render(name, True, BLACK)  # type: ignore
    screen.blit(name_surf, (148, py + 12))

    # Spoon frames
    region_x = 138 + 297
    region_w = 450
    sp = 10
    frame_h = 2 + 34 + 2
    vpad = (50 - frame_h) // 2
    fw = (region_w - (cost + 1) * sp) // max(cost, 1)
    extra = (region_w - (cost * fw + (cost + 1) * sp)) // 2

    siding_img = progress_bar_spoon_siding
    top_img    = progress_bar_spoon_top
    bottom_img = pygame.transform.flip(top_img, False, True)
    right_siding = pygame.transform.flip(siding_img, True, False)

    for i in range(cost):
        fx = region_x + sp + extra + i * (fw + sp)
        fy = py + vpad

        if i < done:
            bg = (85, 60, 53)
        else:
            bg = (40, 25, 22)

        pygame.draw.rect(screen, bg, (fx + 2, fy + 4, fw - 4, frame_h - 8))
        screen.blit(siding_img, (fx, fy + 2))

        iw = max(fw - 12, 0)
        tx = fx + 6
        ty = fy + 3
        d = 0
        while d + 10 <= iw:
            screen.blit(top_img, (tx + d, ty))
            d += 10
        if iw - d > 0:
            screen.blit(top_img, (tx + d, ty), pygame.Rect(0, 0, iw - d, 2))

        by2 = fy + 2 + 34 - 3
        d = 0
        while d + 10 <= iw:
            screen.blit(bottom_img, (tx + d, by2))
            d += 10
        if iw - d > 0:
            screen.blit(bottom_img, (tx + d, by2), pygame.Rect(0, 0, iw - d, 2))

        screen.blit(right_siding, (fx + fw - 6, fy + 2))

    # --- Circular timer (same art as input_spoons) ---
    timer_background = avatarBackgrounds['timer_background']
    timer_hand       = avatarBackgrounds['timer_hand']
    timer_top        = avatarBackgrounds['timer_top']

    tw, th = timer_background.get_size()
    timer_x = 200
    timer_y = int(screen_h * 0.42)

    screen.blit(timer_background, (timer_x, timer_y))

    # Smooth visual timer based on wall clock + pause accumulation
    now = datetime.now()
    if focus_total_secs > 0 and focus_visual_start_time is not None:
        paused_offset = focus_pause_accum_visual
        if focus_timer_paused and focus_pause_start_visual is not None:
            paused_offset += (now - focus_pause_start_visual).total_seconds()

        elapsed_secs = max(0.0, (now - focus_visual_start_time).total_seconds() - paused_offset)
        if elapsed_secs > focus_total_secs:
            elapsed_secs = focus_total_secs

        remaining_secs = int(focus_total_secs - elapsed_secs)
        progress = 0.0 if focus_total_secs <= 0 else (elapsed_secs / focus_total_secs)
        total_rotation = focus_total_spoons * deg_per_spoon_focus
        angle = 45 + (1.0 - progress) * total_rotation
    else:
        angle = 45
        remaining_secs = 0

    # Remaining time label (H:MM:SS)
    rh = remaining_secs // 3600
    rm = (remaining_secs % 3600) // 60
    rs = remaining_secs % 60
    time_str = f"{rh}:{rm:02}:{rs:02}"

    text_surf = timer_font.render(time_str, True, BLACK)  # type: ignore
    text_rect = text_surf.get_rect(center=(timer_x + tw // 2, timer_y + th // 2 - 42))
    screen.blit(text_surf, text_rect)

    # Draw rotating hand + top overlay
    rotated_hand = pygame.transform.rotate(timer_hand, -angle)
    hand_rect = rotated_hand.get_rect(center=(timer_x + tw // 2, timer_y + th // 2))
    screen.blit(rotated_hand, hand_rect)
    screen.blit(timer_top, (timer_x, timer_y))

    # --- Start / Pause buttons ---
    btn_w, btn_h = 160, 50
    gap          = 30
    base_y       = timer_y + 150
    total_w      = btn_w * 2 + gap
    base_x       = timer_x + 350

    # Left button: Start Focus / Restart
    focus_start_rect = pygame.Rect(base_x, base_y - gap*3, btn_w, btn_h)
    pygame.draw.rect(screen, (230, 230, 230), focus_start_rect, border_radius=12)

    if not focus_timer_active and focus_spoons_spent == 0:
        start_label = "Start Focus"
    else:
        start_label = "Restart"

    start_surf = button_font.render(start_label, True, BLACK)  # type: ignore
    screen.blit(start_surf, start_surf.get_rect(center=focus_start_rect.center).topleft)

    # Right button: Pause / Unpause
    focus_pause_rect = pygame.Rect(base_x, base_y, btn_w, btn_h)
    pygame.draw.rect(screen, (230, 230, 230), focus_pause_rect, border_radius=12)

    if not focus_timer_active:
        pause_label = "Pause"
    elif focus_timer_paused:
        pause_label = "Unpause"
    else:
        pause_label = "Pause"

    pause_surf = button_font.render(pause_label, True, BLACK)  # type: ignore
    screen.blit(pause_surf, pause_surf.get_rect(center=focus_pause_rect.center).topleft)

    # --- EXIT button (top right) ---
    exit_font = header_font
    exit_surf = exit_font.render("Exit Focus", True, BLACK)  # type: ignore
    exit_rect = exit_surf.get_rect()
    exit_rect.topleft = (800, 105)

    pygame.draw.rect(screen, (220, 220, 220), exit_rect.inflate(20, 5))
    screen.blit(exit_surf, exit_rect.topleft)

    # Keep exit rect in a global so logic can see it
    focus_exit_rect = exit_rect

    # --- Popup overlay (out of spoons / debt warning) ---
    if focus_popup_text and focus_popup_start:
        elapsed_popup = (datetime.now() - focus_popup_start).total_seconds()
        if elapsed_popup < focus_popup_duration:
            # Fade alpha from ~200 down to 0 over popup_duration
            fade = max(0.0, 1.0 - elapsed_popup / focus_popup_duration)
            alpha = int(200 * fade)

            overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, alpha))
            screen.blit(overlay, (0, 0))

            box_w, box_h = 800, 140
            box_x = (screen_w - box_w) // 2
            box_y = (screen_h - box_h) // 2
            pygame.draw.rect(screen, (255, 255, 255), (box_x, box_y, box_w, box_h), border_radius=18)
            pygame.draw.rect(screen, (60, 40, 30), (box_x, box_y, box_w, box_h), 2, border_radius=18)

            msg_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen_h * 0.045))
            msg_surf = msg_font.render(focus_popup_text, True, BLACK)  # type: ignore
            msg_rect = msg_surf.get_rect(center=(box_x + box_w // 2, box_y + box_h // 2))
            screen.blit(msg_surf, msg_rect.topleft)
        else:
            # Clear popup after it has fully faded
            focus_popup_text  = ""
            focus_popup_start = None

    return exit_rect

def _draw_label_dropdown(screen, attach_x, attach_y, attach_w, rows_count):
    # rows_count controls inner height; tweak ROW_H to taste
    ROW_H = max(28, label_border.get_height() + 8)
    inner_h = max(rows_count, 1) * ROW_H
    tc = drop_down_top_corners
    bc = drop_down_corner
    bh = drop_down_border
    bh_v = pygame.transform.rotate(bh, 90)
    tc_w, tc_h = tc.get_size()
    bc_w, bc_h = bc.get_size()
    bh_w, bh_h = bh.get_size()
    bh_v_w, bh_v_h = bh_v.get_size()

    # Outer box geometry
    outer_x = attach_x
    outer_y = attach_y
    outer_w = attach_w
    outer_h = tc_h + inner_h + bc_h

    pygame.draw.rect(screen, DROPDOWN_BROWN, (outer_x + 3, outer_y - 3, outer_w - 6, outer_h))

    # Top corners
    screen.blit(tc, (outer_x - 2, outer_y + 1))
    screen.blit(pygame.transform.flip(tc, True, False), (outer_x + outer_w - tc_w + 2, outer_y - 1))

    # Bottom corners
    by = outer_y + outer_h - bc_h
    screen.blit(pygame.transform.flip(bc, True, True), (outer_x, by))
    screen.blit(pygame.transform.flip(bc, False, True), (outer_x + outer_w - bc_w, by))

    # Bottom horizontal border (between bottom corners)
    bot_gap_w = max(outer_w - 2 * bc_w, 0)
    bx = outer_x + bc_w
    while bx + bh_w <= outer_x + bc_w + bot_gap_w:
        screen.blit(bh, (bx, by + 1))  # +1 to align with bottom edge of corner
        bx += bh_w
    rem = outer_x + bc_w + bot_gap_w - bx
    if rem > 0:
        screen.blit(bh, (bx, by + 1), pygame.Rect(0, 0, rem, bh_h))

    # Left vertical border (between top and bottom corners)
    ly = outer_y + tc_h
    lv_h = max(outer_h - tc_h - bc_h, 0)
    cy = 0
    while cy + bh_v_h <= lv_h:
        screen.blit(bh_v, (outer_x, ly + cy))
        cy += bh_v_h
    remh = lv_h - cy
    if remh > 0:
        screen.blit(bh_v, (outer_x, ly + cy), pygame.Rect(0, 0, bh_v_w, remh))

    # Right vertical border
    rx = outer_x + outer_w - bh_v_w
    cy = 0
    screen.blit(bh_v, (rx, ly + cy - 2))
    while cy + bh_v_h <= lv_h:
        screen.blit(bh_v, (rx, ly + cy))
        cy += bh_v_h
    remh = lv_h - cy
    if remh > 0:
        screen.blit(bh_v, (rx, ly + cy), pygame.Rect(0, 0, bh_v_w, remh))

    # Return outer box geometry for caller to fill content if needed
    return outer_x, outer_y + tc_h, outer_w, inner_h

def _draw_favorites_panel(screen, outer_x, outer_y, outer_w, content_y, content_h, favorites):
    """
    Draw a right-aligned favorites column inside the dropdown area.
    Also: build chip hitboxes and show a ghost slot while dragging.
    Returns: ((inner_x, inner_y, inner_w, inner_h), panel_w)
    """
    global favorites_chip_buttons, favorites_drop_rect
    favorites_chip_buttons.clear()
    favorites_drop_rect = None

    # Art handles
    top_cap = label_favorite_border_top
    bot_cap = pygame.transform.rotate(top_cap, 180)
    side_src = label_favorite_border_side
    side = pygame.transform.rotate(side_src, 180)
    chip = label_favorite_border

    cap_w, cap_h = top_cap.get_size()
    Lw, Lh = side_src.get_size()
    Rw, Rh = side.get_size()
    chip_w, chip_h = chip.get_size()

    # Panel geometry (inside dropdown, flush to the right)
    panel_w = cap_w
    panel_inner_top  = content_y
    panel_inner_bot  = content_y + content_h
    panel_top_y      = panel_inner_top - cap_h // 2
    panel_bot_y      = panel_inner_bot - cap_h // 2
    panel_x          = outer_x + outer_w - panel_w

    # ---- Pixel nudges ----
    dx      = -6
    dy_top  =  3
    dy_bot  =  7

    # Caps
    top_x = panel_x + dx
    top_y = panel_top_y + dy_top
    bot_x = panel_x + dx
    bot_y = panel_bot_y - cap_h + dy_bot
    screen.blit(top_cap, (top_x, top_y))
    screen.blit(bot_cap, (bot_x, bot_y))

    # LEFT wall (between dropdown and favorites)
    wall_start_y = top_y + cap_h
    wall_end_y   = bot_y
    left_x = top_x
    y = wall_start_y
    while y + Lh <= wall_end_y:
        screen.blit(side_src, (left_x + 1, y))
        y += Lh
    if y < wall_end_y:
        screen.blit(side_src, (left_x + 1, y), pygame.Rect(0, 0, Lw, wall_end_y - y))

    # RIGHT wall (outer)
    right_x = (panel_x + panel_w - Rw) + dx
    y = wall_start_y
    while y + Rh <= wall_end_y:
        screen.blit(side, (right_x - 1, y))
        y += Rh
    if y < wall_end_y:
        screen.blit(side, (right_x - 1, y), pygame.Rect(0, 0, Rw, wall_end_y - y))

    # Inner content rect for chips
    inset_l = 10
    inset_r = max(Lw, Rw) + 8
    inset_t = cap_h + 6
    inset_b = cap_h + 6

    inner_x = top_x + inset_l
    inner_y = top_y + inset_t
    inner_w = panel_w - inset_l - inset_r
    inner_h = (bot_y - top_y) - inset_t - inset_b
    inner_rect = pygame.Rect(inner_x, inner_y, inner_w, inner_h)
    accept_rect = inner_rect.copy()
    accept_rect.y -= 10
    accept_rect.h += 20

    favorites_drop_rect = accept_rect 

    # Layout
    COLS  = 2
    GAP_Y = 10
    GAP_X = -2
    left_col_x  = inner_x
    right_col_x = inner_x + inner_w - chip_w - GAP_X
    if right_col_x < left_col_x:
        right_col_x = left_col_x
    col_x = [left_col_x, right_col_x]

    font_chip = pygame.font.Font("fonts/Stardew_Valley.ttf",
                                 int(screen.get_height() * 0.04))

    # Build working list and hover/placeholder for drag from tasks
    display_labels = favorites[:]
    hover_insert_index = None

    if dragging_label is not None and dragging_label.get("source", "task") == "task":
        mx, my = pygame.mouse.get_pos()
        drag_txt = dragging_label.get("text", "")
        allow_preview = drag_txt not in favorites  # DUPLICATE → block preview entirely

        if allow_preview:
            # Build current chip rects
            slot_rects = []
            for i in range(len(display_labels)):
                row = i // COLS
                col = i % COLS
                cx = col_x[col]
                cy = inner_y + row * (chip_h + GAP_Y)
                r = pygame.Rect(cx, cy - 8, chip_w, chip_h)
                slot_rects.append(r)

            for i, r in enumerate(slot_rects):
                if r.collidepoint(mx, my):
                    hover_insert_index = i
                    break
            else:
                # tail insert (only if cursor inside accept_rect)
                tail_row = len(display_labels) // COLS
                tail_col = len(display_labels) % COLS
                tail_x = col_x[tail_col]
                tail_y = inner_y + tail_row * (chip_h + GAP_Y)
                tail_rect = pygame.Rect(tail_x, tail_y - 8, chip_w, chip_h)
                if accept_rect.collidepoint(mx, my):
                    hover_insert_index = len(display_labels)

            if hover_insert_index is not None:
                display_labels.insert(hover_insert_index, "Temporary Label")
        else:
            hover_insert_index = None  # keep it explicit for clarity


    if not favorites and dragging_label is None:
        msg = "No Favorite Labels"
        ts = font_chip.render(msg, True, BLACK)  # type: ignore
        tx = inner_x + (inner_w - ts.get_width()) // 2
        ty = inner_y + (inner_h - ts.get_height()) // 2
        screen.blit(ts, (tx, ty + 8))
        return (inner_x, inner_y, inner_w, inner_h), panel_w

    # Draw chips (and collect hitboxes)
    for i, label_txt in enumerate(display_labels if display_labels else []):
        row = i // COLS
        col = i % COLS
        cx = col_x[col]
        cy = inner_y + row * (chip_h + GAP_Y)

        if label_txt == "Temporary Label":
            ghost = chip.copy()
            ghost.set_alpha(90)
            screen.blit(ghost, (cx, cy - 8))
            continue

        screen.blit(chip, (cx, cy - 8))
        ts = font_chip.render(label_txt, True, BLACK)  # type: ignore
        tx = cx + (chip_w - ts.get_width()) // 2
        ty = cy + (chip_h - ts.get_height()) // 2 - 1
        screen.blit(ts, (tx, ty - 6))

    # Build *real* hitboxes only for actual favorites (not ghost)
    for i, label_txt in enumerate(favorites):
        row = i // COLS
        col = i % COLS
        cx = col_x[col]
        cy = inner_y + row * (chip_h + GAP_Y)
        rect = pygame.Rect(cx, cy - 8, chip_w, chip_h)
        favorites_chip_buttons.append((rect, i))

    return (inner_x, inner_y, inner_w, inner_h), panel_w

def _draw_edit_form(screen, background_color, icon_image, spoons, task_list):
    """
    Draws the edit form for the selected task, including:
    - Live preview of the current task (header + task box with spoon slots & icons)
    - Input fields:
        * Task Name / Cost / Done
        * Description (multiline)
        * Year / Month / Day / Start Time
    Uses the shared `input_boxes` registry for all fields.
    """
    global edit_buttons, cancel_button_rect, done_button_rect
    global dragging_label, label_buttons, new_label_buttons, label_chip_buttons
    global dropdown_outer_rects, task_drop_rects, favorites_drop_rect
    global hover_insert_index_per_task, favorites_labels
    global input_boxes
    global confirm_one_rect, confirm_all_rect

    edit_buttons.clear()

    DARK_BROWN  = (40, 25, 22)
    LIGHT_BROWN = (85, 60, 53)
    r, g, b = background_color
    arrow_color     = (max(0, r - 20), max(0, g - 20), max(0, b - 20))
    input_box_color = (max(0, r + 20), max(0, g + 20), max(0, b + 20))

    # --- Live Preview header + due calculation (from input_boxes) ---
    screen_h    = screen.get_height()
    header_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen_h * 0.05))
    task_font   = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen_h * 0.06))

    # Get the currently-editing task as fallback for date/time
    if currently_editing is not None and 0 <= currently_editing < len(task_list):
        orig_task = task_list[currently_editing]
    else:
        orig_task = ["", "", 0, 0, 0, datetime.now(), [0, 0, 0, 0], None, []]
    orig_name, orig_desc, orig_cost, orig_done, orig_days, orig_date, orig_st, orig_et, orig_labels = orig_task

    # Read current input values
    name_text  = input_boxes["task"].text if input_boxes["task"].text is not None else ""
    desc_text  = input_boxes["description"].text if input_boxes["description"].text is not None else ""
    cost_text  = input_boxes["spoons_cost"].text if input_boxes["spoons_cost"].text is not None else ""
    done_text  = input_boxes["spoons_done"].text if input_boxes["spoons_done"].text is not None else ""
    year_text  = input_boxes["year"].text if input_boxes["year"].text is not None else ""
    month_text = input_boxes["month"].text if input_boxes["month"].text is not None else ""
    day_text   = input_boxes["day"].text if input_boxes["day"].text is not None else ""
    st_text    = input_boxes["start_time"].text if input_boxes["start_time"].text is not None else ""

    # Cost / done numeric with clamps (0–10 for cost, 0–cost for done)
    try:
        cost_val = int(cost_text) if cost_text.strip() != "" else orig_cost
    except Exception:
        cost_val = orig_cost
    cost_val = max(0, min(10, cost_val))

    try:
        done_val = int(done_text) if done_text.strip() != "" else orig_done
    except Exception:
        done_val = orig_done
    done_val = max(0, min(cost_val, done_val))

    # Year/month/day numeric for due date
    now = datetime.now()

    try:
        year_val = int(year_text) if year_text.strip() != "" else orig_date.year
    except Exception:
        year_val = orig_date.year

    # Month: accept digit or full name (case-insensitive)
    def _month_to_int(s, fallback_month):
        s = (s or "").strip()
        if s == "":
            return fallback_month
        if s.isdigit():
            try:
                mv = int(s)
                if 1 <= mv <= 12:
                    return mv
            except Exception:
                pass
        names = list(calendar.month_name)
        low = s.lower()
        for i in range(1, 13):
            if names[i].lower() == low:
                return i
        return fallback_month

    month_val = _month_to_int(month_text, orig_date.month)

    max_day_ctx = calendar.monthrange(year_val, month_val)[1]
    try:
        day_val = int(day_text) if day_text.strip() != "" else orig_date.day
    except Exception:
        day_val = orig_date.day
    day_val = max(1, min(max_day_ctx, day_val))

    try:
        due = datetime(year_val, month_val, day_val)
    except Exception:
        # fallback if insane
        due = datetime(orig_date.year, orig_date.month, orig_date.day)
    days_left = (due - now).days + 1

    if cost_val > 0 and done_val >= cost_val:
        header = "Completed"
    elif days_left < 0:
        header = "Overdue"  
    elif days_left == 0:
        header = "Due Today"
    elif days_left == 1:
        header = "Due in 1 Day"
    else:
        header = f"Due in {days_left} Days"

    hdr_s = header_font.render(header, True, BLACK)  # type: ignore
    screen.blit(hdr_s, (140, 92))

    # --- Task preview box + spoons bar ---
    border_img   = task_spoons_border
    siding_img   = progress_bar_spoon_siding
    top_img      = progress_bar_spoon_top
    bottom_img   = pygame.transform.flip(top_img, False, True)
    right_siding = pygame.transform.flip(siding_img, True, False)

    py = 92 + hdr_s.get_height()
    screen.blit(border_img, (138, py))

    # Label button UI (unchanged logic)
    label_img              = task_label_border
    label_img_blank        = task_label_border_blank
    label_img_hover        = task_label_border_hover
    label_img_hover_blank  = task_label_border_hover_blank

    edit_label_x, edit_label_y = 395, py + 7
    lw, lh = label_img.get_size()
    edit_label_rect = pygame.Rect(edit_label_x, edit_label_y, lw, lh)

    name_x    = 148
    name_y    = py + 12
    x_limit   = edit_label_x
    base_px   = int(screen.get_height() * 0.06)
    _blit_task_name_fit(screen, name_text, name_x, name_y, x_limit, base_px)

    labels_ref = orig_labels if (isinstance(currently_editing, int) and 0 <= currently_editing < len(task_list)) else []

    mx2, my2 = pygame.mouse.get_pos()
    if len(labels_ref) > 0:
        if edit_label_rect.collidepoint(mx2, my2):
            screen.blit(label_img_hover, (edit_label_x, edit_label_y))
        else:
            screen.blit(label_img, (edit_label_x, edit_label_y))
    else:
        if edit_label_rect.collidepoint(mx2, my2):
            screen.blit(label_img_hover_blank, (edit_label_x, edit_label_y))
        else:
            screen.blit(label_img_blank, (edit_label_x, edit_label_y))

    label_buttons.append((edit_label_rect, currently_editing))

    # --- Dropdown for labels (unchanged) ---
    if currently_editing in expanded_label_tasks:
        border_w = border_img.get_width()
        attach_x = 145
        attach_y = py + 49
        attach_w = border_w - 14

        LABEL_COLS = 3
        ROW_H      = max(28, label_border.get_height() + 8)

        labels_count_for_layout = max(1, len(labels_ref) + 1)
        label_rows              = math.ceil(labels_count_for_layout / LABEL_COLS)
        labels_h_px             = label_rows * ROW_H

        FAV_COLS      = 2
        fav_chip_h    = label_favorite_border.get_height() - 2
        FAV_GAP_Y     = 4
        fav_rows      = max(1, math.ceil(len(favorites_labels) / FAV_COLS))
        favorites_h_px = fav_rows * (fav_chip_h + FAV_GAP_Y)

        inner_needed_px = max(labels_h_px, favorites_h_px)
        rows_count      = max(1, math.ceil(inner_needed_px / ROW_H))

        content_x, content_y, content_w, content_h = _draw_label_dropdown(screen, attach_x, attach_y, attach_w, rows_count)
        tc_h = drop_down_top_corners.get_height()
        bc_h = drop_down_corner.get_height()
        dropdown_outer_rects[currently_editing] = pygame.Rect(attach_x, attach_y, attach_w, tc_h + content_h + bc_h)

        _draw_favorites_panel(screen, attach_x, attach_y, attach_w, content_y, content_h, favorites_labels)

        task_labels_rect = pygame.Rect(content_x, content_y, attach_w - 260, content_h + 30)
        task_drop_rects[currently_editing] = task_labels_rect

        inner_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen.get_height() * 0.045))
        lb         = label_border
        lbw, lbh   = lb.get_size()
        row_h      = max(28, lbh + 8)
        PAD_X      = 12
        GAP_X      = 7
        COLS       = 3

        orig_labels   = labels_ref
        orig_indices  = list(range(len(orig_labels)))
        working_labels  = orig_labels[:]
        working_indices = orig_indices[:]

        is_drag_from_this_task = dragging_label is not None and dragging_label.get("source") == "task" and dragging_label.get("task_idx") == currently_editing
        if is_drag_from_this_task:
            drag_i = dragging_label["label_idx"]
            if 0 <= drag_i < len(working_labels):
                del working_labels[drag_i]
                del working_indices[drag_i]

        ADD_SENTINEL = "__ADD__"
        working_labels.append(ADD_SENTINEL)
        working_indices.append(None)

        slot_rects = []
        for i in range(len(working_labels)):
            row = i // COLS
            col = i % COLS
            chip_x = content_x + PAD_X + col * (lbw + GAP_X)
            chip_y = content_y + row * row_h + (row_h - lbh) // 2
            slot_rects.append(pygame.Rect(chip_x, chip_y, lbw, lbh))

        hover_insert_index = None
        if dragging_label is not None:
            drag_txt    = dragging_label.get("text", "")
            is_reorder  = dragging_label.get("source") == "task" and dragging_label.get("task_idx") == currently_editing
            allow_preview = True
            if not is_reorder and drag_txt in orig_labels:
                allow_preview = False
            if allow_preview:
                mx3, my3 = pygame.mouse.get_pos()
                for i, r in enumerate(slot_rects):
                    if r.collidepoint(mx3, my3):
                        hover_insert_index = i
                        break
                if hover_insert_index is None and slot_rects:
                    last       = slot_rects[-1]
                    right_tail = pygame.Rect(last.right, task_labels_rect.top, max(0, task_labels_rect.right - last.right), task_labels_rect.height)
                    below_tail = pygame.Rect(task_labels_rect.left, last.bottom, task_labels_rect.width, max(0, task_labels_rect.bottom - last.bottom))
                    if right_tail.collidepoint(mx3, my3) or below_tail.collidepoint(mx3, my3):
                        hover_insert_index = len(working_labels) - 1
            else:
                hover_insert_index = None

        display_labels  = working_labels[:]
        display_indices = working_indices[:]
        is_end_slot     = hover_insert_index is not None and hover_insert_index == len(working_labels) - 1
        if hover_insert_index is not None:
            display_labels.insert(hover_insert_index, "Temporary Label")
            display_indices.insert(hover_insert_index, None)
        hover_insert_index_per_task[currently_editing] = "END" if is_end_slot else hover_insert_index

        for disp_i, lab in enumerate(display_labels):
            row = disp_i // COLS
            col = disp_i % COLS
            chip_x = content_x + PAD_X + col * (lbw + GAP_X)
            chip_y = content_y + row * row_h + (row_h - lbh) // 2
            chip_rect = pygame.Rect(chip_x, chip_y, lbw, lbh)

            if lab == "Temporary Label":
                ghost = lb.copy()
                ghost.set_alpha(90)
                screen.blit(ghost, (chip_x, chip_y))
                continue

            if lab == ADD_SENTINEL:
                add_w, add_h = label_new_border.get_size()
                screen.blit(label_new_border, (chip_x, chip_y))
                global new_label_rect
                if new_label_active_task == currently_editing:
                    inner_font2   = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen.get_height() * 0.045))
                    text_surface  = inner_font2.render(new_label_text, True, BLACK)  # type: ignore
                    tx            = chip_x + (add_w - text_surface.get_width()) // 2
                    ty            = chip_y + (add_h - text_surface.get_height()) // 2 - 1
                    if new_label_text:
                        screen.blit(text_surface, (tx, ty + 2))
                    if (pygame.time.get_ticks() // 400) % 2 == 0:
                        caret_x = tx + text_surface.get_width()
                        pygame.draw.line(screen, BLACK, (caret_x + 2, ty + 4), (caret_x + 2, ty + text_surface.get_height() - 2), 2)  # type: ignore
                    new_label_rect = chip_rect
                else:
                    inner_font2 = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen.get_height() * 0.045))
                    ts2         = inner_font2.render("+ New Label", True, BLACK)  # type: ignore
                    tx          = chip_x + (add_w - ts2.get_width()) // 2
                    ty          = chip_y + (add_h - ts2.get_height()) // 2 - 1
                    screen.blit(ts2, (tx, ty + 2))
                    new_label_buttons.append((chip_rect, currently_editing))
                continue

            screen.blit(lb, (chip_x, chip_y))
            ts = inner_font.render(lab, True, BLACK)  # type: ignore
            tx = chip_x + (lbw - ts.get_width()) // 2
            ty = chip_y + (lbh - ts.get_height()) // 2 - 1
            screen.blit(ts, (tx, ty + 2))

            original_idx = display_indices[disp_i]
            if original_idx is not None:
                label_chip_buttons.append((chip_rect, currently_editing, original_idx))

    # --- Draw spoons frames based on cost_val / done_val ---
    region_x = 138 + 297
    region_w = 450
    sp       = 10
    fw       = (region_w - (cost_val + 1) * sp) // max(cost_val, 1)
    extra    = (region_w - (cost_val * fw + (cost_val + 1) * sp)) // 2
    frame_h  = 2 + 34 + 2
    vpad     = (50 - frame_h) // 2

    for i in range(cost_val):
        fx = region_x + sp + extra + i * (fw + sp)
        fy = py + vpad
        if i < done_val:
            bg        = LIGHT_BROWN
            draw_icon = True
        else:
            bg        = DARK_BROWN
            draw_icon = False
        pygame.draw.rect(screen, bg, (fx + 2, fy + 4, fw - 4, frame_h - 8))
        screen.blit(siding_img, (fx, fy + 2))

        iw    = max(fw - 12, 0)
        tx    = fx + 6
        ty    = fy + 3
        dstep = 0
        while dstep + 10 <= iw:
            screen.blit(top_img, (tx + dstep, ty))
            dstep += 10
        if iw - dstep > 0:
            screen.blit(top_img, (tx + dstep, ty), pygame.Rect(0, 0, iw - dstep, 2))
        by2   = fy + 2 + 34 - 3
        dstep = 0
        while dstep + 10 <= iw:
            screen.blit(bottom_img, (tx + dstep, by2))
            dstep += 10
        if iw - dstep > 0:
            screen.blit(bottom_img, (tx + dstep, by2), pygame.Rect(0, 0, iw - dstep, 2))
        screen.blit(right_siding, (fx + fw - 6, fy + 2))
        if draw_icon:
            tmp       = icon_image.copy()
            tmp.set_alpha(255)
            iw2, ih2  = tmp.get_size()
            cx        = fx + 6 + iw // 2 - iw2 // 2
            cy        = fy + 2 + 17 - ih2 // 2
            screen.blit(tmp, (cx, cy))

    labels_open = (currently_editing in expanded_label_tasks)

    # --- Shared layout bases (used whether or not inputs are shown) ---
    h, sp, x0, x1 = 45, 20, 230, 330
    y0            = py + 50 + 37
    y1            = y0 + h + sp + 30

    # --- Inputs using input_boxes (only when labels dropdown is closed) ---
    if not labels_open:
        # Task name / cost / done
        name_rect = pygame.Rect(x0, y0, 300, h)
        cost_rect = pygame.Rect(name_rect.right + sp, y0, 100, h)
        done_rect = pygame.Rect(cost_rect.right + sp, y0, 100, h)

        screen.blit(header_font.render("Task Name:", True, WHITE), (name_rect.x + 87, y0 - 30))  # type: ignore
        screen.blit(header_font.render("Cost:", True, WHITE), (cost_rect.x + 25, y0 - 30))       # type: ignore
        screen.blit(header_font.render("Done:", True, WHITE), (done_rect.x + 20, y0 - 30))       # type: ignore

        input_boxes["task"].rect        = name_rect
        input_boxes["spoons_cost"].rect = cost_rect
        input_boxes["spoons_done"].rect = done_rect

        draw_input_box(screen, input_boxes["task"], LIGHT_GRAY, DARK_SLATE_GRAY, background_color=background_color, infill="light")         # type: ignore
        draw_input_box(screen, input_boxes["spoons_cost"], LIGHT_GRAY, DARK_SLATE_GRAY, background_color=background_color, infill="light")  # type: ignore
        draw_input_box(screen, input_boxes["spoons_done"], LIGHT_GRAY, DARK_SLATE_GRAY, background_color=background_color, infill="light")  # type: ignore

        # Description multiline box
        description_rect = pygame.Rect(325, 290, 350, 80)
        screen.blit(header_font.render("Description:", True, WHITE), (description_rect.x + 120, description_rect.y - 30))  # type: ignore
        input_boxes["description"].rect = description_rect
        draw_input_box(screen, input_boxes["description"], LIGHT_GRAY, DARK_SLATE_GRAY, background_color=background_color, infill="light")  # type: ignore

        # Year / Month / Day / Start Time
        due_horizontal_shift = 25
        y1                   = y0 + h + sp + 135
        x1_shifted           = x1 + due_horizontal_shift

        year_rect = pygame.Rect(x1_shifted - 120 - sp, y1, 120, h)
        mon_rect  = pygame.Rect(x1_shifted, y1, 160, h)
        day_rect  = pygame.Rect(mon_rect.right + sp, y1, 100, h)
        st_rect   = pygame.Rect(day_rect.right + sp, y1, 140, h)

        screen.blit(header_font.render("Due Year:", True, WHITE), (year_rect.x + 15, y1 - 30))    # type: ignore
        screen.blit(header_font.render("Due Month:", True, WHITE), (mon_rect.x + 30, y1 - 30))    # type: ignore
        screen.blit(header_font.render("Due Day:", True, WHITE), (day_rect.x + 10, y1 - 30))      # type: ignore
        screen.blit(header_font.render("Start Time:", True, WHITE), (st_rect.x + 4, y1 - 30))     # type: ignore

        input_boxes["year"].rect       = year_rect
        input_boxes["month"].rect      = mon_rect
        input_boxes["day"].rect        = day_rect
        input_boxes["start_time"].rect = st_rect

        draw_input_box(screen, input_boxes["year"], LIGHT_GRAY, DARK_SLATE_GRAY, background_color=background_color, infill="light")       # type: ignore
        draw_input_box(screen, input_boxes["month"], LIGHT_GRAY, DARK_SLATE_GRAY, background_color=background_color, infill="light")      # type: ignore
        draw_input_box(screen, input_boxes["day"], LIGHT_GRAY, DARK_SLATE_GRAY, background_color=background_color, infill="light")        # type: ignore
        draw_input_box(screen, input_boxes["start_time"], LIGHT_GRAY, DARK_SLATE_GRAY, background_color=background_color, infill="light") # type: ignore

        # --- Restore month/day if user clicked in then clicked off without typing ---
        if not input_boxes["month"].active:
            finalize_month_input(input_boxes["month"])

        # Spinner arrows
        arrow = font.render(">", True, arrow_color)
        up    = pygame.transform.rotate(arrow, 90)
        dn    = pygame.transform.rotate(arrow, 270)

        y_up  = pygame.Rect(year_rect.right - 23, year_rect.y + 5, 15, 15)
        y_dn  = pygame.Rect(year_rect.right - 23, year_rect.y + year_rect.height - 20, 15, 15)
        m_up  = pygame.Rect(mon_rect.right - 23, mon_rect.y + 5, 15, 15)
        m_dn  = pygame.Rect(mon_rect.right - 23, mon_rect.y + mon_rect.height - 20, 15, 15)
        d_up  = pygame.Rect(day_rect.right - 23, day_rect.y + 5, 15, 15)
        d_dn  = pygame.Rect(day_rect.right - 23, day_rect.y + day_rect.height - 20, 15, 15)
        st_up = pygame.Rect(st_rect.right - 23, st_rect.y + 5, 15, 15)
        st_dn = pygame.Rect(st_rect.right - 23, st_rect.y + st_rect.height - 20, 15, 15)

        for b in (y_up, y_dn, m_up, m_dn, d_up, d_dn, st_up, st_dn):
            pygame.draw.rect(screen, input_box_color, b)
        for u, drect in ((y_up, y_dn), (m_up, m_dn), (d_up, d_dn), (st_up, st_dn)):
            screen.blit(up, (u.left - 6, u.top + 3))
            screen.blit(dn, (drect.left - 9, drect.top - 3))

        # mark blocked regions so clicks here don't trigger text selection
        input_boxes["year"].blocked_regions       = [y_up, y_dn]
        input_boxes["month"].blocked_regions      = [m_up, m_dn]
        input_boxes["day"].blocked_regions        = [d_up, d_dn]
        input_boxes["start_time"].blocked_regions = [st_up, st_dn]

        # edit_buttons: spinner arrows first, then text boxes
        edit_buttons += [
            (y_up, "year_up"), (y_dn, "year_down"),
            (m_up, "month_up"), (m_dn, "month_down"),
            (d_up, "day_up"), (d_dn, "day_down"),
            (st_up, "start_time_up"), (st_dn, "start_time_down"),
        ]
        edit_buttons += [
            (input_boxes["task"].rect, "task"),
            (input_boxes["spoons_cost"].rect, "spoons_cost"),
            (input_boxes["spoons_done"].rect, "spoons_done"),
            (input_boxes["description"].rect, "description"),
            (input_boxes["year"].rect, "year"),
            (input_boxes["month"].rect, "month"),
            (input_boxes["day"].rect, "day"),
            (input_boxes["start_time"].rect, "start_time"),
        ]

    # Buttons (cancel / confirm)
    # Detect if this task appears to be part of a recurring series
    is_recurring = False
    recurring_indices = []
    if 0 <= currently_editing < len(task_list):
        orig = task_list[currently_editing]
        orig_name_l = orig[0].strip().lower()
        orig_desc_l = orig[1].strip().lower()
        orig_cost_i = int(orig[2])
        orig_st_h   = int(orig[6][0])
        orig_st_m   = int(orig[6][1])

        for i, t in enumerate(task_list):
            try:
                n, d, c, dn, dy, dt, st, et, lbs = t
            except:
                continue
            if (n.strip().lower() == orig_name_l and 
                d.strip().lower() == orig_desc_l and
                int(c) == orig_cost_i and 
                int(st[0]) == orig_st_h and 
                int(st[1]) == orig_st_m):
                recurring_indices.append(i)

        # 2 or more → recurring
        if len(recurring_indices) >= 2:
            is_recurring = True

    # Button layout
    yb = y1 + h + sp - 5

    if is_recurring:
        # Cancel left, then Confirm(One), Confirm(All)
        confirm_edit_button = toggleButtons['ConfirmButtonThick']
        cancel_button_rect = pygame.Rect(x1 - 130, yb, 120, 40)
        confirm_one_rect   = pygame.Rect(cancel_button_rect.right + 20, yb, 230, 40)
        confirm_all_rect   = pygame.Rect(confirm_one_rect.right + 20, yb, 230, 40)


        screen.blit(cancel_edit_button, cancel_button_rect.topleft)
        screen.blit(confirm_edit_button, confirm_one_rect.topleft)
        screen.blit(confirm_edit_button, confirm_all_rect.topleft)

        txt_cancel = font.render("cancel", True, WHITE)  # type: ignore
        txt_one    = font.render("confirm (one)", True, WHITE)  # type: ignore
        txt_all    = font.render("confirm (all)", True, WHITE)  # type: ignore

        screen.blit(txt_cancel, txt_cancel.get_rect(center=cancel_button_rect.center).topleft)
        screen.blit(txt_one,    txt_one.get_rect(center=confirm_one_rect.center).topleft)
        screen.blit(txt_all,    txt_all.get_rect(center=confirm_all_rect.center).topleft)

    else:
        # Original: cancel + confirm
        confirm_edit_button = toggleButtons['ConfirmButton']
        cancel_button_rect = pygame.Rect(x1, yb, 120, 40)
        done_button_rect   = pygame.Rect(x1 + 200 + sp, yb, 120, 40)

        screen.blit(cancel_edit_button, cancel_button_rect.topleft)
        screen.blit(confirm_edit_button, done_button_rect.topleft)

        txt_cancel  = font.render("cancel", True, WHITE)  # type: ignore
        txt_confirm = font.render("confirm", True, WHITE)  # type: ignore

        screen.blit(txt_cancel,  txt_cancel.get_rect(center=cancel_button_rect.center).topleft)
        screen.blit(txt_confirm, txt_confirm.get_rect(center=done_button_rect.center).topleft)

    # Dragged label chip overlay (unchanged)
    if dragging_label is not None:
        mx2, my2 = pygame.mouse.get_pos()
        chip_img = label_favorite_border if dragging_label.get("source") == "fav" else label_border
        lbw, lbh = chip_img.get_size()

        chip_x = mx2 - lbw // 2
        chip_y = my2 - lbh // 2

        outer_rect = dropdown_outer_rects.get(currently_editing)
        deleting   = outer_rect is not None and not outer_rect.collidepoint(mx2, my2)

        screen.blit(chip_img, (chip_x, chip_y))

        inner_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen.get_height() * 0.045))
        ts         = inner_font.render(dragging_label["text"], True, BLACK)  # type: ignore
        tx         = chip_x + (lbw - ts.get_width()) // 2
        ty         = chip_y + (lbh - ts.get_height()) // 2 - 1
        screen.blit(ts, (tx, ty + 2))

        if deleting:
            tw, th = trashcan_image.get_size()
            screen.blit(trashcan_image, (chip_x + lbw - tw, chip_y + lbh - th + 2))
    
def handle_task_scroll(event, scroll_offset_px, total_content_height):
    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 4:
            scroll_offset_px -= 40
        elif event.button == 5:
            scroll_offset_px += 40
    max_scroll = max(0, total_content_height - VIEWPORT_HEIGHT)
    return max(0, min(scroll_offset_px, max_scroll))

def handle_task_scroll(event, scroll_offset_px, total_content_height):
    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 4:
            scroll_offset_px -= 40
        elif event.button == 5:
            scroll_offset_px += 40
    max_scroll = max(0, total_content_height - VIEWPORT_HEIGHT)
    return max(0, min(scroll_offset_px, max_scroll))


def _apply_edit_to_one(task_list, idx, boxes, orig_et, orig_labels, preserve_date=False):
    # Read fields
    name_text  = boxes["task"].text or ""
    desc_text  = boxes["description"].text or ""
    cost_text  = boxes["spoons_cost"].text or ""
    done_text  = boxes["spoons_done"].text or ""
    year_text  = boxes["year"].text or ""
    month_text = boxes["month"].text or ""
    day_text   = boxes["day"].text or ""
    st_text    = boxes["start_time"].text or ""

    # Cost/done
    try: cost_val = int(cost_text) if cost_text.strip() != "" else 0
    except: cost_val = 0
    cost_val = max(0, min(10, cost_val))

    try: done_val = int(done_text) if done_text.strip() != "" else 0
    except: done_val = 0
    done_val = max(0, min(cost_val, done_val))

    # Original per-task values
    orig = task_list[idx]
    _, _, _, _, old_days, old_date, old_st, _, _ = orig

    # If preserving the date (Confirm-All), keep the original
    if preserve_date:
        new_date = old_date
        new_days = old_days
    else:
        # Compute new date normally (Confirm-One)
        try: year_val = int(year_text) if year_text.strip() != "" else old_date.year
        except: year_val = old_date.year

        def _month_to_int__(s, fallback):
            s = (s or "").strip()
            if s == "":
                return fallback
            if s.isdigit():
                try:
                    iv = int(s)
                    if 1 <= iv <= 12:
                        return iv
                except:
                    pass
            import calendar
            names = list(calendar.month_name)
            low = s.lower()
            for i in range(1, 13):
                if names[i].lower() == low:
                    return i
            return fallback

        month_val = _month_to_int__(month_text, old_date.month)

        import calendar
        max_day = calendar.monthrange(year_val, month_val)[1]
        try: day_val = int(day_text) if day_text.strip() != "" else old_date.day
        except: day_val = old_date.day
        day_val = max(1, min(max_day, day_val))

        try: new_date = datetime(year_val, month_val, day_val)
        except: new_date = old_date
        new_days = (new_date - datetime.now()).days + 1

    # Start time
    s = (st_text or "").strip()
    s = s.zfill(4)[:4] if s.isdigit() else ""
    try:
        if s:
            hh = int(s[:2])
            mm = int(s[2:])
        else:
            hh = int(old_st[0])
            mm = int(old_st[1])
        hh = max(0, min(23, hh))
        mm = max(0, min(59, mm))
    except:
        hh, mm = int(old_st[0]), int(old_st[1])
    new_st = [hh, mm, 0, 0]

    # Apply update
    task_list[idx] = [
        name_text,
        desc_text,
        cost_val,
        done_val,
        new_days,
        new_date,
        new_st,
        orig_et,
        orig_labels
    ]

def _exit_edit_mode():
    global currently_editing, input_active
    global expanded_label_tasks, dragging_label
    global hover_insert_index_per_task, dropdown_outer_rects, task_drop_rects
    global favorites_drop_rect, new_label_active_task, new_label_text, new_label_rect
    global input_boxes

    expanded_label_tasks.clear()
    dragging_label = None
    hover_insert_index_per_task.clear()
    dropdown_outer_rects.clear()
    task_drop_rects.clear()
    favorites_drop_rect = None
    new_label_active_task = None
    new_label_text = ""
    new_label_rect = None
    currently_editing = None
    input_active = None
    for b in input_boxes.values():
        b.active = False
        b.selecting = False

def logic_complete_tasks(task_list, spoons_debt_toggle, event, spoons, streak_dates, confetti_particles, level, spoons_used_today, page, time_per_spoon):
    """
    Handles clicks and key events for both list and edit form.
    Uses the shared `input_boxes` registry for the edit form (no edit_state).
    Also advances the per-task focus timer when focus mode is active.
    """
    global currently_editing, input_active, cancel_button_rect, done_button_rect
    global spoons_xp
    global dragging_label
    global new_label_active_task, new_label_text, new_label_rect, new_label_buttons
    global expanded_label_tasks, hover_insert_index_per_task, dropdown_outer_rects, task_drop_rects, favorites_drop_rect
    global add_task_button_rect, focus_task, focus_buttons
    global focus_timer_active, focus_timer_paused, focus_timer_start, focus_timer_last_update
    global focus_total_secs, focus_remaining_secs, focus_total_spoons, focus_spoons_spent
    global focus_popup_text, focus_popup_start, focus_warning_shown_for_debt
    global focus_start_rect, focus_pause_rect, focus_exit_rect
    global focus_visual_start_time, focus_pause_start_visual, focus_pause_accum_visual
    global label_buttons, label_chip_buttons, favorites_chip_buttons, favorites_labels
    global frame_buttons, remove_buttons
    global input_boxes

    # --- Focus mode top-level mouse handling ---
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if focus_task is not None:
            if focus_start_rect and focus_start_rect.collidepoint(event.pos):
                _start_focus_timer(task_list, time_per_spoon)
                return False, spoons, confetti_particles, streak_dates, level, spoons_used_today
            if focus_pause_rect and focus_pause_rect.collidepoint(event.pos):
                if focus_timer_active:
                    now = datetime.now()
                    if not focus_timer_paused:
                        focus_timer_paused       = True
                        focus_pause_start_visual = now
                    else:
                        focus_timer_paused = False
                        if focus_pause_start_visual is not None:
                            focus_pause_accum_visual += (now - focus_pause_start_visual).total_seconds()
                        focus_pause_start_visual = None
                return False, spoons, confetti_particles, streak_dates, level, spoons_used_today
            if focus_exit_rect and focus_exit_rect.collidepoint(event.pos):
                focus_task          = None
                focus_timer_active  = False
                focus_timer_paused  = False
                return False, spoons, confetti_particles, streak_dates, level, spoons_used_today

        if add_task_button_rect and add_task_button_rect.collidepoint(event.pos):
            folder_map = {
                "complete_homework_tasks": "homework",
                "complete_chores_tasks":   "chores",
                "complete_work_tasks":     "work",
                "complete_misc_tasks":     "misc",
                "complete_exams_tasks":    "exams",
                "complete_projects_tasks": "projects",
            }
            return (("input_tasks", folder_map.get(page, "homework")), spoons, confetti_particles, streak_dates, level, spoons_used_today

                   )

    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        if focus_task is not None:
            focus_task = None
            return False, spoons, confetti_particles, streak_dates, level, spoons_used_today
        if currently_editing is not None:
            currently_editing = None
            input_active      = None
            for box in input_boxes.values():
                box.active     = False
                box.selecting  = False
            return False, spoons, confetti_particles, streak_dates, level, spoons_used_today

    def _commit_new_label():
        global new_label_active_task, new_label_text
        if new_label_active_task is not None:
            t   = new_label_active_task
            txt = (new_label_text or "").strip()
            if txt:
                if txt not in task_list[t][8]:
                    task_list[t][8].append(txt)
            new_label_active_task = None
            new_label_text        = ""

    # --- Label drag start (for list and edit views) ---
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        for rect, t_idx in new_label_buttons:
            if rect.collidepoint(event.pos):
                new_label_active_task = t_idx
                new_label_text        = ""
                return False, spoons, confetti_particles, streak_dates, level, spoons_used_today
        if new_label_active_task is not None:
            if not (new_label_rect and new_label_rect.collidepoint(event.pos)):
                _commit_new_label()
                return False, spoons, confetti_particles, streak_dates, level, spoons_used_today

        for rect, t_idx, l_idx in label_chip_buttons:
            if rect.collidepoint(event.pos):
                lab_text      = task_list[t_idx][8][l_idx]
                dragging_label = {"source": "task", "task_idx": t_idx, "label_idx": l_idx, "text": lab_text}
                return False, spoons, confetti_particles, streak_dates, level, spoons_used_today
        for rect, fav_idx in favorites_chip_buttons:
            if rect.collidepoint(event.pos):
                lab_text      = favorites_labels[fav_idx]
                dragging_label = {"source": "fav", "fav_idx": fav_idx, "text": lab_text}
                return False, spoons, confetti_particles, streak_dates, level, spoons_used_today

    if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        if dragging_label is not None:
            mx, my         = event.pos
            open_task_idx  = next(iter(expanded_label_tasks), None)
            in_favorites   = favorites_drop_rect is not None and favorites_drop_rect.collidepoint(mx, my)
            in_task_area   = open_task_idx is not None and task_drop_rects.get(open_task_idx) and task_drop_rects[open_task_idx].collidepoint(mx, my)
            outer_rect     = dropdown_outer_rects.get(open_task_idx)
            outside_dropdown = outer_rect is not None and not outer_rect.collidepoint(mx, my)

            if dragging_label.get("source") == "task" and in_favorites:
                label_text = dragging_label["text"]
                if label_text not in favorites_labels:
                    favorites_labels.append(label_text)
                dragging_label = None
                return False, spoons, confetti_particles, streak_dates, level, spoons_used_today

            if dragging_label.get("source") == "fav" and in_task_area and open_task_idx is not None:
                label_text = dragging_label["text"]
                insert_i   = hover_insert_index_per_task.get(open_task_idx)
                labels_ref = task_list[open_task_idx][8]
                if insert_i == "END" or insert_i is None:
                    insert_pos = len(labels_ref)
                else:
                    insert_pos = int(insert_i)
                if label_text not in labels_ref:
                    labels_ref.insert(insert_pos, label_text)
                dragging_label = None
                return False, spoons, confetti_particles, streak_dates, level, spoons_used_today

            if dragging_label.get("source") == "task" and open_task_idx is not None and dragging_label.get("task_idx") == open_task_idx and in_task_area:
                label_text = dragging_label["text"]
                from_i     = dragging_label["label_idx"]
                insert_i   = hover_insert_index_per_task.get(open_task_idx)
                labels_ref = task_list[open_task_idx][8]

                if 0 <= from_i < len(labels_ref) and labels_ref[from_i] == label_text:
                    del labels_ref[from_i]
                if insert_i == "END" or insert_i is None:
                    insert_pos = len(labels_ref)
                else:
                    insert_pos = int(insert_i)
                    if from_i < insert_pos:
                        insert_pos -= 1
                labels_ref.insert(insert_pos, label_text)
                dragging_label = None
                return False, spoons, confetti_particles, streak_dates, level, spoons_used_today

            if dragging_label.get("source") == "task" and open_task_idx is not None and outside_dropdown:
                t_idx     = dragging_label.get("task_idx")
                l_idx     = dragging_label.get("label_idx")
                if t_idx is not None and l_idx is not None:
                    labels_ref = task_list[t_idx][8]
                    if 0 <= l_idx < len(labels_ref) and labels_ref[l_idx] == dragging_label.get("text"):
                        del labels_ref[l_idx]
                dragging_label = None
                return False, spoons, confetti_particles, streak_dates, level, spoons_used_today

            if dragging_label.get("source") == "fav" and outside_dropdown:
                f_idx = dragging_label.get("fav_idx")
                if f_idx is not None and 0 <= f_idx < len(favorites_labels) and favorites_labels[f_idx] == dragging_label.get("text"):
                    del favorites_labels[f_idx]
                dragging_label = None
                return False, spoons, confetti_particles, streak_dates, level, spoons_used_today

            dragging_label = None
            return False, spoons, confetti_particles, streak_dates, level, spoons_used_today

    # --- Edit mode (currently_editing) ---
    if currently_editing is not None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Toggle label dropdown for the edit view
            for rect, idx in label_buttons:
                if rect.collidepoint(event.pos) and idx == currently_editing:
                    if idx in expanded_label_tasks:
                        expanded_label_tasks.clear()
                    else:
                        expanded_label_tasks.clear()
                        expanded_label_tasks.add(idx)
                        input_active = None
                        for box in input_boxes.values():
                            box.active    = False
                            box.selecting = False
                        edit_buttons.clear()
                    return False, spoons, confetti_particles, streak_dates, level, spoons_used_today

            # Cancel edit
            if cancel_button_rect and cancel_button_rect.collidepoint(event.pos):
                currently_editing = None
                input_active      = None
                expanded_label_tasks.clear()
                dragging_label = None
                hover_insert_index_per_task.clear()
                dropdown_outer_rects.clear()
                task_drop_rects.clear()
                favorites_drop_rect  = None
                new_label_active_task = None
                new_label_text        = ""
                new_label_rect        = None
                for box in input_boxes.values():
                    box.active    = False
                    box.selecting = False
                return False, spoons, confetti_particles, streak_dates, level, spoons_used_today

            # Save edits
            # Save edits (supports confirm one / confirm all)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and currently_editing is not None:

                # Re-detect recurring (same logic)
                orig_task = task_list[currently_editing]
                orig_name_l = orig_task[0].strip().lower()
                orig_desc_l = orig_task[1].strip().lower()
                orig_cost_i = int(orig_task[2])
                orig_st_h   = int(orig_task[6][0])
                orig_st_m   = int(orig_task[6][1])

                recurring_indices = []
                for i, t in enumerate(task_list):
                    try:
                        tn, td, tc, tdn, tdy, tdate, tst, tet, tlb = t
                    except:
                        continue
                    if (tn.strip().lower() == orig_name_l and
                        td.strip().lower() == orig_desc_l and
                        int(tc) == orig_cost_i and
                        int(tst[0]) == orig_st_h and
                        int(tst[1]) == orig_st_m):
                        recurring_indices.append(i)

                is_recurring = len(recurring_indices) >= 2

                # Confirm one
                if is_recurring and confirm_one_rect and confirm_one_rect.collidepoint(event.pos):
                    orig_et    = orig_task[7]
                    orig_labels = orig_task[8]
                    _apply_edit_to_one(task_list, currently_editing, input_boxes, orig_et, orig_labels)
                    _exit_edit_mode()
                    return False, spoons, confetti_particles, streak_dates, level, spoons_used_today

                # Confirm all
                if is_recurring and confirm_all_rect and confirm_all_rect.collidepoint(event.pos):
                    orig_et    = orig_task[7]
                    orig_labels = orig_task[8]
                    for idx in recurring_indices:
                        _apply_edit_to_one(task_list, idx, input_boxes, orig_et, orig_labels, preserve_date=True)

                    _exit_edit_mode()
                    return False, spoons, confetti_particles, streak_dates, level, spoons_used_today

                # Non-recurring → normal confirm button
                if not is_recurring and done_button_rect and done_button_rect.collidepoint(event.pos):
                    orig_et    = orig_task[7]
                    orig_labels = orig_task[8]
                    _apply_edit_to_one(task_list, currently_editing, input_boxes, orig_et, orig_labels)
                    _exit_edit_mode()
                    return False, spoons, confetti_particles, streak_dates, level, spoons_used_today


            # Click on edit fields or spinner arrows
            clicked_any = False
            clicked_key = None
            for rect, key in edit_buttons:
                if rect.collidepoint(event.pos):
                    clicked_any = True
                    clicked_key = key
                    break

            if clicked_any:
                if clicked_key in ("task", "spoons_cost", "spoons_done", "description", "year", "month", "day", "start_time"):
                    input_active = clicked_key
                    for k, box in input_boxes.items():
                        box.active    = (k == input_active)
                        box.selecting = False
                elif clicked_key == "month_up":
                    t = input_boxes["month"].text or ""
                    def _month_to_int(s, fallback_month):
                        s = (s or "").strip()
                        if s == "":
                            return fallback_month
                        if s.isdigit():
                            try:
                                mv = int(s)
                                if 1 <= mv <= 12:
                                    return mv
                            except Exception:
                                pass
                        names = list(calendar.month_name)
                        low   = s.lower()
                        for i in range(1, 13):
                            if names[i].lower() == low:
                                return i
                        return fallback_month
                    cur  = _month_to_int(t, datetime.now().month)
                    nxt  = cur + 1 if cur < 12 else 1
                    input_boxes["month"].text = calendar.month_name[nxt]
                elif clicked_key == "month_down":
                    t = input_boxes["month"].text or ""
                    def _month_to_int(s, fallback_month):
                        s = (s or "").strip()
                        if s == "":
                            return fallback_month
                        if s.isdigit():
                            try:
                                mv = int(s)
                                if 1 <= mv <= 12:
                                    return mv
                            except Exception:
                                pass
                        names = list(calendar.month_name)
                        low   = s.lower()
                        for i in range(1, 13):
                            if names[i].lower() == low:
                                return i
                        return fallback_month
                    cur   = _month_to_int(t, datetime.now().month)
                    prev  = cur - 1 if cur > 1 else 12
                    input_boxes["month"].text = calendar.month_name[prev]
                elif clicked_key == "day_up":
                    ytxt = input_boxes["year"].text or ""
                    mtxt = input_boxes["month"].text or ""
                    try:
                        yv = int(ytxt) if ytxt.strip() != "" else datetime.now().year
                    except Exception:
                        yv = datetime.now().year
                    def _month_to_int(s, fallback_month):
                        s = (s or "").strip()
                        if s == "":
                            return fallback_month
                        if s.isdigit():
                            try:
                                mv = int(s)
                                if 1 <= mv <= 12:
                                    return mv
                            except Exception:
                                pass
                        names = list(calendar.month_name)
                        low   = s.lower()
                        for i in range(1, 13):
                            if names[i].lower() == low:
                                return i
                        return fallback_month
                    mv      = _month_to_int(mtxt, datetime.now().month)
                    maxd    = calendar.monthrange(yv, mv)[1]
                    dtxt    = input_boxes["day"].text or ""
                    try:
                        dv = int(dtxt) if dtxt.strip() != "" else 1
                    except Exception:
                        dv = 1
                    dv      = dv + 1 if dv < maxd else 1
                    input_boxes["day"].text = str(dv)
                elif clicked_key == "day_down":
                    ytxt = input_boxes["year"].text or ""
                    mtxt = input_boxes["month"].text or ""
                    try:
                        yv = int(ytxt) if ytxt.strip() != "" else datetime.now().year
                    except Exception:
                        yv = datetime.now().year
                    def _month_to_int(s, fallback_month):
                        s = (s or "").strip()
                        if s == "":
                            return fallback_month
                        if s.isdigit():
                            try:
                                mv = int(s)
                                if 1 <= mv <= 12:
                                    return mv
                            except Exception:
                                pass
                        names = list(calendar.month_name)
                        low   = s.lower()
                        for i in range(1, 13):
                            if names[i].lower() == low:
                                return i
                        return fallback_month
                    mv      = _month_to_int(mtxt, datetime.now().month)
                    maxd    = calendar.monthrange(yv, mv)[1]
                    dtxt    = input_boxes["day"].text or ""
                    try:
                        dv = int(dtxt) if dtxt.strip() != "" else maxd
                    except Exception:
                        dv = maxd
                    dv      = dv - 1 if dv > 1 else maxd
                    input_boxes["day"].text = str(dv)
                elif clicked_key == "year_up":
                    ytxt = input_boxes["year"].text or ""
                    try:
                        yv = int(ytxt) if ytxt.strip() != "" else datetime.now().year
                    except Exception:
                        yv = datetime.now().year
                    ny = min(2100, yv + 1)
                    input_boxes["year"].text = str(ny)
                elif clicked_key == "year_down":
                    ytxt = input_boxes["year"].text or ""
                    try:
                        yv = int(ytxt) if ytxt.strip() != "" else datetime.now().year
                    except Exception:
                        yv = datetime.now().year
                    ny = max(2000, yv - 1)
                    input_boxes["year"].text = str(ny)
                elif clicked_key in ("start_time_up", "start_time_down"):
                    s = (input_boxes["start_time"].text or "").zfill(4)[:4]
                    try:
                        hh = int(s[:2])
                        mm = int(s[2:])
                    except Exception:
                        now = datetime.now()
                        hh  = now.hour
                        mm  = now.minute
                    if clicked_key == "start_time_up":
                        mm += 15
                        if mm >= 60:
                            mm = 0
                            hh = (hh + 1) % 24
                    else:
                        mm -= 15
                        if mm < 0:
                            mm = 45
                            hh = (hh - 1) % 24
                    input_boxes["start_time"].text = f"{hh:02d}{mm:02d}"
            else:
                # Click away: if not on any edit button or labels or confirm/cancel, blur inputs
                any_hit = False
                for rect, key in edit_buttons:
                    if rect.collidepoint(event.pos):
                        any_hit = True
                        break
                if cancel_button_rect and cancel_button_rect.collidepoint(event.pos):
                    any_hit = True
                if done_button_rect and done_button_rect.collidepoint(event.pos):
                    any_hit = True
                for rect, idx in label_buttons:
                    if rect.collidepoint(event.pos):
                        any_hit = True
                        break
                if not any_hit:
                    input_active = None
                    for box in input_boxes.values():
                        box.active    = False
                        box.selecting = False

        # Tab navigation and letting InputBox handle events
        if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            tab_order = ["task", "spoons_cost", "spoons_done", "description", "year", "month", "day", "start_time"]
            try:
                idx = tab_order.index(input_active) if input_active in tab_order else -1
            except ValueError:
                idx = -1
            input_active = tab_order[(idx + 1) % len(tab_order)]
            for k, box in input_boxes.items():
                box.active    = (k == input_active)
                box.selecting = False
            return False, spoons, confetti_particles, streak_dates, level, spoons_used_today

        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP, pygame.KEYDOWN):
            for box in input_boxes.values():
                logic_input_box(event, box, pygame.display.get_surface())
            return False, spoons, confetti_particles, streak_dates, level, spoons_used_today

    # --- NEW label typing (list mode only) ---
    if new_label_active_task is not None and event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RETURN:
            _commit_new_label()
            return False, spoons, confetti_particles, streak_dates, level, spoons_used_today
        elif event.key == pygame.K_ESCAPE:
            new_label_active_task = None
            new_label_text        = ""
            return False, spoons, confetti_particles, streak_dates, level, spoons_used_today
        elif event.key == pygame.K_BACKSPACE:
            new_label_text = new_label_text[:-1]
            return False, spoons, confetti_particles, streak_dates, level, spoons_used_today
        else:
            ch = event.unicode
            if ch:
                lbw         = label_new_border.get_width()
                inner_font  = pygame.font.Font("fonts/Stardew_Valley.ttf", int(pygame.display.get_surface().get_height() * 0.045))
                test        = new_label_text + ch
                if inner_font.size(test)[0] <= (lbw - 12):
                    new_label_text = test
            return False, spoons, confetti_particles, streak_dates, level, spoons_used_today

    # --- List mode: focus activation, remove/edit, spoon frames ---
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        for rect, idx in focus_buttons:
            if rect.collidepoint(event.pos):
                focus_task = idx
                return False, spoons, confetti_particles, streak_dates, level, spoons_used_today

        for icon_rect, idx in remove_buttons:
            if icon_rect.collidepoint(event.pos):
                mid = icon_rect.y + icon_rect.height // 2
                if event.pos[1] < mid:
                    expanded_label_tasks.discard(idx)
                    if idx in expanded_label_tasks:
                        expanded_label_tasks.discard(idx)
                    task_list.pop(idx)
                else:
                    if 0 <= idx < len(task_list):
                        name, desc, cost, done_, days, date, st, et, labels = task_list[idx]
                    else:
                        name, desc, cost, done_, days, date, st, et, labels = "", "", 0, 0, 0, datetime.now(), [0, 0, 0, 0], None, []

                    def _st_to_digits(st_in):
                        try:
                            hh = int(st_in[0]) % 24
                            mm = int(st_in[1]) % 60
                            return f"{hh:02d}{mm:02d}"
                        except Exception:
                            return ""
                    input_boxes["task"].text        = name
                    input_boxes["description"].text = desc
                    input_boxes["spoons_cost"].text = str(cost)
                    input_boxes["spoons_done"].text = str(done_)
                    input_boxes["year"].text        = str(date.year)
                    input_boxes["month"].text       = calendar.month_name[date.month]
                    input_boxes["day"].text         = str(date.day)
                    input_boxes["start_time"].text  = _st_to_digits(st)

                    for box in input_boxes.values():
                        box.active    = False
                        box.selecting = False
                    input_active      = "task"
                    input_boxes["task"].active = True

                    expanded_label_tasks.clear()
                    currently_editing = idx
                return False, spoons, confetti_particles, streak_dates, level, spoons_used_today

        for rect, idx, frame_i in frame_buttons:
            if rect.collidepoint(event.pos):
                name, desc, cost, done_, days, date, st, et, labels = task_list[idx]
                new_done = frame_i + 1
                to_fill  = new_done - done_
                if to_fill < 1:
                    to_fill  = to_fill - 1
                    new_done = new_done - 1
                task_list[idx][3] = min(cost, new_done)
                spoons           -= to_fill
                spoons_used_today += to_fill
                if spoons_used_today < 0:
                    spoons_used_today = 0
                if spoons > 99:
                    spoons = 99
                break

    return False, spoons, confetti_particles, streak_dates, level, spoons_used_today