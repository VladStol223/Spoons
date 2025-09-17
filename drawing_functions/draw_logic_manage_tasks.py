# draw_logic_manage_tasks.py
from config import *
from drawing_functions.draw_rounded_button import draw_rounded_button
from drawing_functions.draw_input_box import draw_input_box

import pygame
import math
import calendar
from datetime import datetime, timedelta

# Globals for click handling
remove_buttons     = []  # (pygame.Rect, idx)
frame_buttons      = []  # (pygame.Rect, task_index, frame_index)

# Globals for click handling
edit_buttons       = []  # (pygame.Rect, field_name)
cancel_button_rect = None
done_button_rect   = None

# State
currently_editing = None  # index of the task being edited
edit_state = {}

spoons_xp = 0

# Dropdown state + click targets
expanded_label_tasks = set()  # indices of tasks whose label dropdown is open
label_buttons = []            # (pygame.Rect, task_index)

# Label chip hitboxes + drag state
label_chip_buttons = []   # (pygame.Rect, task_index, label_index)
dragging_label = None     # {"task_idx": int, "label_idx": int, "text": str}

# Temporary favorites (will be saved to data.json later)
favorites_labels = []  # this will be rebound per page

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
CONTENT_TOP     = 148   # Where content starts
VIEWPORT_HEIGHT = 350   # Visible content height
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
    spoon_name,
    folder_one,
    folder_two,
    folder_three,
    folder_four,
    folder_five,
    folder_six
):
    """
    Draws the manage-tasks page, or the edit form if currently_editing is set.
    """
    global edit_buttons, remove_buttons, frame_buttons, label_buttons, label_chip_buttons, dragging_label
    global favorites_chip_buttons, favorites_drop_rect, task_drop_rects, hover_insert_index_per_task
    global dropdown_outer_rects, new_label_rect, new_label_buttons
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

    # If we're editing, draw the edit UI instead of the list
    if currently_editing is not None:
        _draw_edit_form(screen, background_color, icon_image, spoons, task_list)
        return scroll_offset_px, 0


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

    t       = pygame.time.get_ticks() / 300.0
    pulse   = (math.sin(t) + 1) / 2.0
    def lerp(a, b, f):
        return (
            int(a[0] + (b[0] - a[0]) * f),
            int(a[1] + (b[1] - a[1]) * f),
            int(a[2] + (b[2] - a[2]) * f),
        )

    overdue, upcoming, completed = [], {}, []
    for idx, (name, cost, done, days, date, st, et, labels) in enumerate(task_list):
        if done >= cost:
            completed.append((idx, name, cost, done, days, date, st, et, labels))
        elif days < 0:
            overdue.append((idx, name, cost, done, days, date, st, et, labels))
        else:
            upcoming.setdefault(days, []).append((idx, name, cost, done, days, date, st, et, labels))
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

        for idx, name, cost, done, days, date, st, et, labels in items:
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
                    time_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen.get_height() * 0.055))
                    t_str = f"{hh:02d}:{mm:02d}"
                    ts = time_font.render(t_str, True, BLACK)  # type: ignore
                    tx = time_x + (tw - ts.get_width()) // 2 - 26
                    ty = time_y + (th - ts.get_height()) // 2 - 1
                    screen.blit(ts, (tx, ty + 2))
                # NOTE: no label button (and no label_buttons.append) in list view anymore

                name_x = 148
                name_y = by + 12

                if show_time:
                    # left edge of the time badge
                    x_limit = time_x - 26
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
                    if i < done:
                        bg, draw_icon = LIGHT_BROWN, True
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
                        tmp = icon_image.copy()
                        tmp.set_alpha(255 if i<done else 128)
                        iw2, ih2 = tmp.get_size()
                        cx = fx+6 + iw//2 - iw2//2
                        cy = fy+2 + 17 - ih2//2
                        screen.blit(tmp, (cx, cy))

                # click target
                btn = pygame.Rect(138, by, 750, 50)
                buttons.append((btn, idx))

                # remove/edit icon
                ix, iy = remove_edit.get_size()
                remove_rect = pygame.Rect(118, by+5, ix, iy)
                if remove_rect.collidepoint(mx,my) or btn.collidepoint(mx,my):
                    screen.blit(remove_edit, remove_rect.topleft)
                    remove_buttons.append((remove_rect, idx))

            y_cur += 60
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


    return scroll_offset_px, total_content_height

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
    - Input fields in three layers:
      * Task Name (400px)
      * Due Month / Due Day (200px each)
      * Cost / Done (100px each)
    """
    global edit_buttons, cancel_button_rect, done_button_rect
    global dragging_label
    edit_buttons.clear()

    DARK_BROWN      = (40, 25, 22)
    LIGHT_BROWN     = (85, 60, 53)
    r, g, b = background_color
    arrow_color = (max(0, r-20), max(0, g-20), max(0, b-20))
    input_box_color = (max(0, r+20), max(0, g+20), max(0, b+20))

    # --- Live Preview ---
    screen_h = screen.get_height()
    header_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen_h * 0.05))
    task_font   = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen_h * 0.06))

    # Gather state
    name = edit_state.get("name", "")
    label = edit_state.get("labels", "")
    # after: never let cost > 10, and never let done > cost
    raw_cost = int(edit_state.get("cost", "0") or 0)
    cost = max(0, min(10, raw_cost))
    raw_done = int(edit_state.get("done", "0") or 0)
    done = max(0, min(cost, raw_done))

    def _safe_month_to_int(val, fallback_month):
        # accepts int, "3", or full month name (any case). otherwise fallback.
        try:
            if isinstance(val, int):
                return max(1, min(12, val))
            s = str(val).strip()
            if s.isdigit():
                return max(1, min(12, int(s)))
            # try exact full month name (case-insensitive)
            names = list(calendar.month_name)  # ["", "January", ...]
            for i in range(1, 13):
                if names[i].lower() == s.lower():
                    return i
        except Exception:
            pass
        return fallback_month

    now = datetime.now()

    # if the month field is currently being typed, use the original (committed) month for calculations
    raw_month_for_draw = edit_state.get("month", str(now.month)) or str(now.month)
    if input_active == "month" and edit_state.get("_month_orig_pretty"):
        raw_month_for_draw = edit_state["_month_orig_pretty"]

    mon = _safe_month_to_int(raw_month_for_draw, now.month)

    # similar idea for day: if actively typing and empty, fall back to original
    raw_day_for_draw = edit_state.get("day", str(now.day)) or str(now.day)
    if input_active == "day" and (edit_state.get("day", "") == ""):
        raw_day_for_draw = edit_state.get("_day_orig", str(now.day))

    try:
        day = max(1, min(31, int(str(raw_day_for_draw).strip())))
    except Exception:
        day = now.day

    # compute date/status
    now = datetime.now()
    try:
        due = datetime(now.year, mon, day)
    except:
        due = now
    days_left = (due - now).days + 1

    if cost > 0 and done >= cost:
        header = "Completed"
    elif days_left < 0:
        header = "Overdue"
    elif days_left == 0:
        header = "Due Today"
    elif days_left == 1:
        header = "Due in 1 Day"
    else:
        header = f"Due in {days_left} Days"

    # draw header
    hdr_s = header_font.render(header, True, BLACK) #type: ignore
    screen.blit(hdr_s, (140, 140))

    # prepare images
    border_img   = task_spoons_border
    siding_img   = progress_bar_spoon_siding
    top_img      = progress_bar_spoon_top
    bottom_img   = pygame.transform.flip(top_img, False, True)
    right_siding = pygame.transform.flip(siding_img, True, False)

    # preview container
    py = 135 + hdr_s.get_height() + 10
    screen.blit(border_img, (138, py))

    # --- In EDIT view we show the label button + dropdown (moved from list) ---
    label_img        = task_label_border
    label_img_blank  = task_label_border_blank
    label_img_hover  = task_label_border_hover
    label_img_hover_blank = task_label_border_hover_blank

    # Draw the label button in the same place as list preview UI
    edit_label_x, edit_label_y = 395, py + 7
    lw, lh = label_img.get_size()
    edit_label_rect = pygame.Rect(edit_label_x, edit_label_y, lw, lh)

    # ---- task name (fit so it stops before the label button) ----
    name_x = 148
    name_y = py + 12
    x_limit = edit_label_x  # left edge of the label button
    base_px = int(screen.get_height() * 0.06)  # same size as task_font
    _blit_task_name_fit(screen, name, name_x, name_y, x_limit, base_px)

    # Current task labels are edited directly on the live task_list
    labels_ref = task_list[currently_editing][7] if (isinstance(currently_editing, int) and 0 <= currently_editing < len(task_list)) else []

    mx2, my2 = pygame.mouse.get_pos()
    if len(labels_ref) > 0:
        if edit_label_rect.collidepoint(mx2, my2): screen.blit(label_img_hover, (edit_label_x, edit_label_y))
        else:                                      screen.blit(label_img,        (edit_label_x, edit_label_y))
    else:
        if edit_label_rect.collidepoint(mx2, my2): screen.blit(label_img_hover_blank, (edit_label_x, edit_label_y))
        else:                                      screen.blit(label_img_blank,       (edit_label_x, edit_label_y))

    # Reuse global label_buttons as the click target in EDIT view
    label_buttons.append((edit_label_rect, currently_editing))

    # If the edit task's dropdown is open, render it directly under the preview
    if currently_editing in expanded_label_tasks:
        border_w = border_img.get_width()
        attach_x = 145
        attach_y = py + 49
        attach_w = border_w - 14

        # --- Compute dropdown inner height based on task labels and favorites (same rules) ---
        LABEL_COLS = 3
        ROW_H = max(28, label_border.get_height() + 8)

        labels_count_for_layout = max(1, len(labels_ref) + 1)  # +1 for add chip
        label_rows = math.ceil(labels_count_for_layout / LABEL_COLS)
        labels_h_px = label_rows * ROW_H

        FAV_COLS = 2
        fav_chip_h = label_favorite_border.get_height() - 2
        FAV_GAP_Y = 4
        fav_rows = max(1, math.ceil(len(favorites_labels) / FAV_COLS))
        favorites_h_px = fav_rows * (fav_chip_h + FAV_GAP_Y)

        inner_needed_px = max(labels_h_px, favorites_h_px)
        rows_count = max(1, math.ceil(inner_needed_px / ROW_H))

        # Build dropdown outer and remember its rect for drag-delete
        content_x, content_y, content_w, content_h = _draw_label_dropdown(screen, attach_x, attach_y, attach_w, rows_count)
        tc_h = drop_down_top_corners.get_height()
        bc_h = drop_down_corner.get_height()
        dropdown_outer_rects[currently_editing] = pygame.Rect(attach_x, attach_y, attach_w, tc_h + content_h + bc_h)

        # Favorites panel (right-docked)
        _draw_favorites_panel(screen, attach_x, attach_y, attach_w, content_y, content_h, favorites_labels)

        # Task labels area (left of favorites)
        task_labels_rect = pygame.Rect(content_x, content_y, attach_w - 260, content_h + 30)
        task_drop_rects[currently_editing] = task_labels_rect

        # Draw label chips + add-chip (same as list, but bound to labels_ref)
        inner_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen.get_height() * 0.045))
        lb = label_border
        lbw, lbh = lb.get_size()
        row_h = max(28, lbh + 8)
        PAD_X = 12
        GAP_X = 7
        COLS = 3

        # Build working lists respecting drag reordering (same logic as list)
        orig_labels   = labels_ref
        orig_indices  = list(range(len(orig_labels)))
        working_labels  = orig_labels[:]
        working_indices = orig_indices[:]

        is_drag_from_this_task = (
            dragging_label is not None
            and dragging_label.get("source") == "task"
            and dragging_label.get("task_idx") == currently_editing
        )
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
            drag_txt = dragging_label.get("text", "")
            is_reorder = (dragging_label.get("source") == "task" and dragging_label.get("task_idx") == currently_editing)
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
                    last = slot_rects[-1]
                    right_tail = pygame.Rect(last.right, task_labels_rect.top,
                                            max(0, task_labels_rect.right - last.right),
                                            task_labels_rect.height)
                    below_tail = pygame.Rect(task_labels_rect.left, last.bottom,
                                            task_labels_rect.width,
                                            max(0, task_labels_rect.bottom - last.bottom))
                    if right_tail.collidepoint(mx3, my3) or below_tail.collidepoint(mx3, my3):
                        hover_insert_index = len(working_labels) - 1
            else:
                hover_insert_index = None

        display_labels  = working_labels[:]
        display_indices = working_indices[:]
        is_end_slot = (hover_insert_index == len(working_labels) - 1) if hover_insert_index is not None else False
        if hover_insert_index is not None:
            display_labels.insert(hover_insert_index, "Temporary Label")
            display_indices.insert(hover_insert_index, None)
        hover_insert_index_per_task[currently_editing] = ("END" if is_end_slot else hover_insert_index)

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
                # Reuse the inline new-label editor already handled by logic_complete_tasks
                global new_label_rect
                if new_label_active_task == currently_editing:
                    inner_font2 = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen.get_height() * 0.045))
                    text_surface = inner_font2.render(new_label_text, True, BLACK)  # type: ignore
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
                    ts2 = inner_font2.render("+ New Label", True, BLACK)  # type: ignore
                    tx = chip_x + (add_w - ts2.get_width()) // 2
                    ty = chip_y + (add_h - ts2.get_height()) // 2 - 1
                    screen.blit(ts2, (tx, ty + 2))
                    new_label_buttons.append((chip_rect, currently_editing))
                continue

            # regular label chip
            screen.blit(lb, (chip_x, chip_y))
            ts = inner_font.render(lab, True, BLACK)  # type: ignore
            tx = chip_x + (lbw - ts.get_width()) // 2
            ty = chip_y + (lbh - ts.get_height()) // 2 - 1
            screen.blit(ts, (tx, ty + 2))

            original_idx = display_indices[disp_i]
            if original_idx is not None:
                label_chip_buttons.append((chip_rect, currently_editing, original_idx))


    # draw spoons frames
    region_x = 138 + 297
    region_w = 450
    sp = 10
    fw = (region_w - (cost+1)*sp)//max(cost,1)
    extra = (region_w - (cost*fw + (cost+1)*sp))//2
    frame_h = 2 + 34 + 2
    vpad = (50 - frame_h)//2

    for i in range(cost):
        fx = region_x + sp + extra + i*(fw+sp)
        fy = py + vpad
        # bg color
        if i < done:
            bg = LIGHT_BROWN
            draw_icon = True
        else:
            bg = DARK_BROWN
            draw_icon = False
        pygame.draw.rect(screen, bg, (fx+2, fy+4, fw-4, frame_h-8))
        screen.blit(siding_img, (fx, fy+2))
        # tile top/bottom
        iw = max(fw-12,0)
        tx, ty = fx+6, fy+3
        d=0
        while d+10<=iw:
            screen.blit(top_img,(tx+d,ty)); d+=10
        if iw-d>0:
            screen.blit(top_img,(tx+d,ty),pygame.Rect(0,0,iw-d,2))
        by2 = fy+2+34-3; d=0
        while d+10<=iw:
            screen.blit(bottom_img,(tx+d,by2)); d+=10
        if iw-d>0:
            screen.blit(bottom_img,(tx+d,by2),pygame.Rect(0,0,iw-d,2))
        screen.blit(right_siding,(fx+fw-6,fy+2))
        if draw_icon:
            tmp = icon_image.copy(); tmp.set_alpha(255)
            iw2, ih2 = tmp.get_size()
            cx = fx+6 + iw//2 - iw2//2
            cy = fy+2 + 17 - ih2//2
            screen.blit(tmp,(cx,cy))

    labels_open = (currently_editing in expanded_label_tasks)

    # --- Shared layout bases (used whether or not inputs are shown) ---
    h, sp, x0, x1 = 50, 20, 230, 330
    y0 = py + 50 + 45           # baseline under the preview box
    y1 = y0 + h + sp + 30

    # --- Inputs ---
    if not labels_open:
        y0 = py + 50 + 45
        h, sp, x0, x1 = 50, 20, 230, 330

        # Task name
        name_rect = pygame.Rect(x0, y0, 300, h)
        cost_rect=pygame.Rect(name_rect.right + sp,y0,100,h)
        done_rect=pygame.Rect(cost_rect.right + sp,y0,100,h)

        screen.blit(header_font.render("Task Name:",True,WHITE),(x0 + 87,y0 - 30)) #type: ignore
        draw_input_box(screen,name_rect,input_active == "name",name,LIGHT_GRAY,DARK_SLATE_GRAY,False,background_color,"light") #type: ignore
        edit_buttons.append((name_rect,"name"))

        screen.blit(header_font.render("Cost:",True,WHITE),(cost_rect.left + 25,y0 - 30)) #type: ignore
        draw_input_box(screen,cost_rect,input_active == "cost",str(cost),LIGHT_GRAY,DARK_SLATE_GRAY,True,background_color,"light") #type: ignore
        screen.blit(header_font.render("Done:",True,WHITE),(done_rect.left + 20,y0 - 30)) #type: ignore
        draw_input_box(screen,done_rect,input_active == "done",str(done),LIGHT_GRAY,DARK_SLATE_GRAY,True,background_color,"light") #type: ignore
        edit_buttons.append((cost_rect,"cost")); edit_buttons.append((done_rect,"done"))

        # Month/Day + Start Time
        due_horizontal_shift = 65
        y1 = y0 + h + sp + 30

        x1_shifted = x1 - due_horizontal_shift
        mon_rect = pygame.Rect(x1_shifted, y1, 200, h)
        day_rect = pygame.Rect(x1_shifted + 200 + sp, y1, 100, h)
        st_rect  = pygame.Rect(day_rect.right + sp, y1, 140, h)  # start time to the right

        # Labels (aligned with shifted rects)
        screen.blit(header_font.render("Due Month:", True, WHITE), (x1_shifted + 40, y1 - 30))       # type: ignore
        screen.blit(header_font.render("Due Day:",   True, WHITE), (day_rect.x + 10,   y1 - 30))     # type: ignore
        screen.blit(header_font.render("Start Time:",True, WHITE), (st_rect.x  + 4,    y1 - 30))     # type: ignore


        # Month/Day display values (pretty when inactive, raw when active)
        raw_mon = str(edit_state.get("month", calendar.month_name[mon]))
        raw_day = str(edit_state.get("day", day))
        mon_display = raw_mon if input_active == "month" else calendar.month_name[mon]
        day_display = raw_day if input_active == "day"   else str(day)

        # Inputs
        draw_input_box(screen, mon_rect, input_active == "month", mon_display,
                    LIGHT_GRAY, DARK_SLATE_GRAY, False, background_color, "light")  # type: ignore
        draw_input_box(screen, day_rect, input_active == "day", day_display,
                    LIGHT_GRAY, DARK_SLATE_GRAY, True,  background_color, "light")  # type: ignore

        # Start time: HH:MM when not editing; raw digits while editing
        raw_st = edit_state.get("start_time", "")
        def _fmt_st_display(s):
            if input_active == "start_time":
                return s  # raw digits (no colon)
            if s and s.isdigit():
                s = s.zfill(4)[:4]
                return f"{s[:2]}:{s[2:]}"
            return "HH:MM"
        draw_input_box(screen, st_rect, input_active == "start_time", _fmt_st_display(raw_st),
                    LIGHT_GRAY, DARK_SLATE_GRAY, False, background_color, "light")  # type: ignore

        # -------- month ghost-autocomplete rendering (only while typing) --------
        if input_active == "month":
            typed = edit_state.get("month", "")
            # find completion (case-insensitive) from full month names
            month_names = [calendar.month_name[i] for i in range(1, 13)]
            comp = ""
            if typed:
                for mname in month_names:
                    if mname.lower().startswith(typed.lower()):
                        comp = mname[len(typed):]
                        # stash the full suggestion so logic can commit on blur/tab
                        edit_state["_month_suggestion_full"] = mname
                        break
                else:
                    edit_state["_month_suggestion_full"] = None
            else:
                edit_state["_month_suggestion_full"] = None

            # draw the completion at 50% opacity right after the typed text
            if comp:
                typed_surf = font.render(typed, True, LIGHT_GRAY)   # type: ignore
                comp_surf  = font.render(comp,  True, LIGHT_GRAY)   # type: ignore
                comp_surf.set_alpha(128)

                # left padding similar to other chips: ~12px, vertically centered
                tx = mon_rect.x + 5
                ty = mon_rect.y + (mon_rect.height - typed_surf.get_height()) // 2 - 1 + 6
                screen.blit(typed_surf, (tx, ty))
                screen.blit(comp_surf,  (tx + typed_surf.get_width(), ty))

        # --- Click hitboxes ---
        # text-area rects are 24px narrower on the right (so arrows don't grab focus)
        mon_text_rect = pygame.Rect(mon_rect.x, mon_rect.y, mon_rect.w - 24, mon_rect.h)
        day_text_rect = pygame.Rect(day_rect.x, day_rect.y, day_rect.w - 24, day_rect.h)
        st_text_rect  = pygame.Rect(st_rect.x,  st_rect.y,  st_rect.w  - 24, st_rect.h)

        # only these text-area rects activate typing focus
        edit_buttons.append((mon_text_rect, "month"))
        edit_buttons.append((day_text_rect, "day"))
        edit_buttons.append((st_text_rect,  "start_time"))

        # spinner arrows (Month, Day, Start Time)
        arrow = font.render(">", True, arrow_color)
        up    = pygame.transform.rotate(arrow, 90)
        dn    = pygame.transform.rotate(arrow, 270)

        m_up = pygame.Rect(mon_rect.right - 23, mon_rect.y + 5,                  15, 15)
        m_dn = pygame.Rect(mon_rect.right - 23, mon_rect.y + mon_rect.height-20, 15, 15)
        d_up = pygame.Rect(day_rect.right - 23, day_rect.y + 5,                  15, 15)
        d_dn = pygame.Rect(day_rect.right - 23, day_rect.y + day_rect.height-20, 15, 15)
        st_up = pygame.Rect(st_rect.right - 23, st_rect.y + 5,                   15, 15)
        st_dn = pygame.Rect(st_rect.right - 23, st_rect.y + st_rect.height - 20, 15, 15)

        for b in (m_up, m_dn, d_up, d_dn, st_up, st_dn):
            pygame.draw.rect(screen, input_box_color, b)

        screen.blit(up, (m_up.left - 6,  m_up.top + 3));  screen.blit(dn, (m_dn.left - 9,  m_dn.top - 3))
        screen.blit(up, (d_up.left - 6,  d_up.top + 3));  screen.blit(dn, (d_dn.left - 9,  d_dn.top - 3))
        screen.blit(up, (st_up.left - 6, st_up.top + 3)); screen.blit(dn, (st_dn.left - 9, st_dn.top - 3))

        edit_buttons += [
            (m_up, "month_up"), (m_dn, "month_down"),
            (d_up, "day_up"),   (d_dn, "day_down"),
            (st_up, "start_time_up"), (st_dn, "start_time_down")
        ]

    # Buttons (image-backed with text, robust to name collisions)
    yb = y1 + h + sp + 15
    cancel_button_rect = pygame.Rect(x1, yb, 120, 40)
    done_button_rect   = pygame.Rect(x1 + 200 + sp, yb, 120, 40)

    screen.blit(cancel_edit_button, cancel_button_rect.topleft)
    screen.blit(confirm_edit_button,   done_button_rect.topleft)

    # overlay labels
    cancel_text  = font.render("cancel",  True, WHITE)  # type: ignore
    confirm_text = font.render("confirm", True, WHITE)  # type: ignore

    # center text on buttons
    screen.blit(cancel_text,  cancel_text.get_rect(center=cancel_button_rect.center).topleft)
    screen.blit(confirm_text, confirm_text.get_rect(center=done_button_rect.center).topleft)


    # --- Dragged label chip overlay (edit view) ---
    if dragging_label is not None:
        mx2, my2 = pygame.mouse.get_pos()
        chip_img = label_favorite_border if dragging_label.get("source") == "fav" else label_border
        lbw, lbh = chip_img.get_size()

        chip_x = mx2 - lbw // 2
        chip_y = my2 - lbh // 2

        # Is cursor outside this task's dropdown? (show trash can)
        outer_rect = dropdown_outer_rects.get(currently_editing)
        deleting = (outer_rect is not None and not outer_rect.collidepoint(mx2, my2))

        screen.blit(chip_img, (chip_x, chip_y))

        inner_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen.get_height() * 0.045))
        ts = inner_font.render(dragging_label["text"], True, BLACK)  # type: ignore
        tx = chip_x + (lbw - ts.get_width()) // 2
        ty = chip_y + (lbh - ts.get_height()) // 2 - 1
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


def logic_complete_tasks(task_list, buttons, event, spoons, streak_dates, confetti_particles, level):
    """
    Handles clicks and key events for both list and edit form.
    """
    global currently_editing, edit_state, input_active, cancel_button_rect, done_button_rect
    global spoons_xp
    global dragging_label
    global new_label_active_task, new_label_text, new_label_rect, new_label_buttons
    global expanded_label_tasks, hover_insert_index_per_task, dropdown_outer_rects, task_drop_rects, favorites_drop_rect

    def _commit_new_label():
        global new_label_active_task, new_label_text
        if new_label_active_task is not None:
            t = new_label_active_task
            txt = (new_label_text or "").strip()
            if txt:
                # append to the end (it is drawn after all labels)
                if txt not in task_list[t][7]:  # avoid duplicate labels; remove this line if dupes allowed
                    task_list[t][7].append(txt)
            # reset state
            new_label_active_task = None
            new_label_text = ""

    def _begin_month_typing():
        """Start month typing: clear field, remember original pretty month."""
        raw = edit_state.get("month", str(datetime.now().month))
        if str(raw).isdigit():
            cur_mon = calendar.month_name[int(raw)]
        else:
            # if not a full valid name, fall back to current pretty month
            names = list(calendar.month_name)
            cur_mon = raw if raw in names else calendar.month_name[datetime.now().month]
        edit_state["_month_orig_pretty"] = cur_mon
        edit_state["_month_suggestion_full"] = None
        edit_state["month"] = ""  # clear visible text

    def _commit_month_on_exit():
        """Commit suggestion if present, else revert to original pretty month."""
        sugg = edit_state.get("_month_suggestion_full")
        orig = edit_state.get("_month_orig_pretty")
        if sugg:
            edit_state["month"] = sugg
        elif orig:
            edit_state["month"] = orig
        edit_state.pop("_month_suggestion_full", None)
        edit_state.pop("_month_orig_pretty", None)

    def _begin_day_typing():
        """Start day typing: clear field, remember original."""
        edit_state.setdefault("_day_orig", edit_state.get("day", ""))  # remember once
        edit_state["day"] = ""

    def _commit_day_on_exit():
        """If empty or invalid, revert to original; else keep typed."""
        val = str(edit_state.get("day", "")).strip()
        if not val.isdigit():
            # revert if empty or invalid
            edit_state["day"] = edit_state.get("_day_orig", "")
        # cleanup
        edit_state.pop("_day_orig", None)

    def _begin_start_time_typing():
        """Start start_time typing: clear field, remember original raw digits."""
        edit_state.setdefault("_st_orig", edit_state.get("start_time", ""))
        edit_state["start_time"] = ""

    def _commit_start_time_on_exit():
        """If empty, revert to original; else keep typed HHMM digits as-is (validated on save/format)."""
        val = str(edit_state.get("start_time", "")).strip()
        if val == "":
            edit_state["start_time"] = edit_state.get("_st_orig", "")
        edit_state.pop("_st_orig", None)

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        # 0) Click on a "new label" chip -> start editing
        for rect, t_idx in new_label_buttons:
            if rect.collidepoint(event.pos):
                # activate the inline editor for that task
                new_label_active_task = t_idx
                new_label_text = ""
                return False, spoons, confetti_particles, streak_dates, level
        # 0b) If we were typing and clicked somewhere else (not on the active chip), commit
        if new_label_active_task is not None:
            # If there's an active chip, and we clicked outside it, commit
            if not (new_label_rect and new_label_rect.collidepoint(event.pos)):
                _commit_new_label()
                return False, spoons, confetti_particles, streak_dates, level

        # 1) Start dragging a label chip (check this BEFORE other click targets)
        for rect, t_idx, l_idx in label_chip_buttons:
            if rect.collidepoint(event.pos):
                # Start drag: store the chip info; it will be hidden from its slot while dragging
                lab_text = task_list[t_idx][7][l_idx]  # labels list at index 7
                dragging_label = {"source": "task", "task_idx": t_idx, "label_idx": l_idx, "text": lab_text}
                return False, spoons, confetti_particles, streak_dates, level
        # 1b) Start dragging from Favorites panel
        for rect, fav_idx in favorites_chip_buttons:
            if rect.collidepoint(event.pos):
                lab_text = favorites_labels[fav_idx]
                dragging_label = {"source": "fav", "fav_idx": fav_idx, "text": lab_text}
                return False, spoons, confetti_particles, streak_dates, level

    if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        if dragging_label is not None:
            mx, my = event.pos

            open_task_idx = next(iter(expanded_label_tasks), None)  # single-open policy
            in_favorites  = (favorites_drop_rect is not None and favorites_drop_rect.collidepoint(mx, my))
            in_task_area  = (open_task_idx is not None and task_drop_rects.get(open_task_idx) and task_drop_rects[open_task_idx].collidepoint(mx, my))

            # NEW: outside whole dropdown?
            outer_rect = dropdown_outer_rects.get(open_task_idx)
            outside_dropdown = (outer_rect is not None and not outer_rect.collidepoint(mx, my))

            # A) task -> favorites
            if dragging_label.get("source") == "task" and in_favorites:
                label_text = dragging_label["text"]
                if label_text not in favorites_labels:
                    favorites_labels.append(label_text)
                dragging_label = None
                return False, spoons, confetti_particles, streak_dates, level

            # B) favorites -> task
            if dragging_label.get("source") == "fav" and in_task_area and open_task_idx is not None:
                label_text = dragging_label["text"]
                insert_i = hover_insert_index_per_task.get(open_task_idx)
                labels_ref = task_list[open_task_idx][7]
                if insert_i == "END" or insert_i is None:
                    insert_pos = len(labels_ref)  # append
                else:
                    insert_pos = int(insert_i)

                if label_text not in labels_ref:
                    labels_ref.insert(insert_pos, label_text)
                dragging_label = None
                return False, spoons, confetti_particles, streak_dates, level

            # C) reorder within same task
            if (dragging_label.get("source") == "task"
                and open_task_idx is not None
                and dragging_label.get("task_idx") == open_task_idx
                and in_task_area):
                label_text = dragging_label["text"]
                from_i = dragging_label["label_idx"]
                insert_i = hover_insert_index_per_task.get(open_task_idx)
                labels_ref = task_list[open_task_idx][7]

                # remove first
                if 0 <= from_i < len(labels_ref) and labels_ref[from_i] == label_text:
                    del labels_ref[from_i]

                # map end-slot to append *after* removal (length has changed)
                if insert_i == "END" or insert_i is None:
                    insert_pos = len(labels_ref)
                else:
                    insert_pos = int(insert_i)
                    # if we removed an earlier index, and target was after it, shift left by 1
                    if from_i < insert_pos:
                        insert_pos -= 1

                labels_ref.insert(insert_pos, label_text)

                dragging_label = None
                return False, spoons, confetti_particles, streak_dates, level

            # NEW D1) delete from TASK if dropped outside dropdown
            if dragging_label.get("source") == "task" and open_task_idx is not None and outside_dropdown:
                t_idx = dragging_label.get("task_idx")
                l_idx = dragging_label.get("label_idx")
                if t_idx is not None and l_idx is not None:
                    labels_ref = task_list[t_idx][7]
                    if 0 <= l_idx < len(labels_ref) and labels_ref[l_idx] == dragging_label.get("text"):
                        del labels_ref[l_idx]
                dragging_label = None
                return False, spoons, confetti_particles, streak_dates, level

            # NEW D2) delete from FAVORITES if dropped outside dropdown
            if dragging_label.get("source") == "fav" and outside_dropdown:
                f_idx = dragging_label.get("fav_idx")
                if f_idx is not None and 0 <= f_idx < len(favorites_labels) and favorites_labels[f_idx] == dragging_label.get("text"):
                    del favorites_labels[f_idx]
                dragging_label = None
                return False, spoons, confetti_particles, streak_dates, level

            # Fallback: cancel drag
            dragging_label = None
            return False, spoons, confetti_particles, streak_dates, level

    # --- Edit mode ---
    if currently_editing is not None:
        # Mouse events
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Edit-view label button toggles dropdown
            for rect, idx in label_buttons:
                if rect.collidepoint(event.pos) and idx == currently_editing:
                    if idx in expanded_label_tasks:
                        expanded_label_tasks.clear()
                    else:
                        expanded_label_tasks.clear()
                        expanded_label_tasks.add(idx)
                        # hide inputs → drop focus so typing doesn’t go to hidden fields
                        input_active = None
                        edit_buttons.clear()
                    return False, spoons, confetti_particles, streak_dates, level
            # Cancel edit
            if cancel_button_rect and cancel_button_rect.collidepoint(event.pos):
                currently_editing = None
                edit_state.pop("_month_suggestion_full", None)
                edit_state.pop("_month_orig_pretty", None)
                input_active = None

                # close any open dropdowns + reset drag UI
                expanded_label_tasks.clear()
                dragging_label = None
                hover_insert_index_per_task.clear()
                dropdown_outer_rects.clear()
                task_drop_rects.clear()
                favorites_drop_rect = None
                new_label_active_task = None
                new_label_text = ""
                new_label_rect = None

                return False, spoons, confetti_particles, streak_dates, level

            # Save edits
            if done_button_rect and done_button_rect.collidepoint(event.pos):
                # Extract values
                name  = edit_state.get("name", "")
                cost  = int(edit_state.get("cost", "0") or 0)
                done_ = int(edit_state.get("done", "0") or 0)
                # finalize special fields in case we're saving straight from focus
                if input_active == "month":
                    _commit_month_on_exit()
                elif input_active == "day":
                    _commit_day_on_exit()
                elif input_active == "start_time":
                    _commit_start_time_on_exit()

                raw_month = str(edit_state.get("month", datetime.now().month))
                if raw_month.isdigit():
                    mon = max(1, min(12, int(raw_month)))
                else:
                    try:
                        # accept only full month names; otherwise default to current month
                        mon = list(calendar.month_name).index(raw_month)
                        if mon == 0:
                            mon = datetime.now().month
                    except ValueError:
                        mon = datetime.now().month

                try:
                    day = int(str(edit_state.get("day", "1")).strip() or "1")
                    day = max(1, min(31, day))
                except Exception:
                    day = 1

                # Update task + SAVE START TIME
                orig = task_list[currently_editing]
                new_date = orig[4].replace(month=mon, day=day)
                new_days = (new_date - datetime.now()).days + 1

                # parse HHMM digits to hh/mm
                s = (edit_state.get("start_time", "") or "").strip()
                s = s.zfill(4)[:4] if s.isdigit() else ""
                try:
                    hh = int(s[:2]) if s else int(orig[5][0])  # fallback to existing
                    mm = int(s[2:]) if s else int(orig[5][1])
                    hh = max(0, min(23, hh))
                    mm = max(0, min(59, mm))
                except Exception:
                    # last-resort fallback to 00:00
                    hh, mm = 0, 0

                # keep original container shape if possible
                if isinstance(orig[5], (list, tuple)) and len(orig[5]) >= 2:
                    new_st = list(orig[5])
                    new_st[0] = hh
                    new_st[1] = mm
                else:
                    new_st = [hh, mm, 0, 0]

                # close any open dropdowns + reset drag UI
                expanded_label_tasks.clear()
                dragging_label = None
                hover_insert_index_per_task.clear()
                dropdown_outer_rects.clear()
                task_drop_rects.clear()
                favorites_drop_rect = None
                new_label_active_task = None
                new_label_text = ""
                new_label_rect = None

                task_list[currently_editing] = [name, cost, done_, new_days, new_date, new_st, orig[6], orig[7]]


                currently_editing = None
                edit_state.pop("_month_suggestion_full", None)
                edit_state.pop("_month_orig_pretty", None)
                input_active = None
                return False, spoons, confetti_particles, streak_dates, level

            # Clicked on a field or arrow
            for rect, key in edit_buttons:
                if rect.collidepoint(event.pos):
                    # Text-area focus only (month/day/start_time text rects, name/cost/done)
                    if key in ("name", "cost", "done", "month", "day", "start_time"):
                        # commit the field we're leaving, if it is one of the special clears
                        if input_active == "month" and key != "month":
                            _commit_month_on_exit()
                        if input_active == "day" and key != "day":
                            _commit_day_on_exit()
                        if input_active == "start_time" and key != "start_time":
                            _commit_start_time_on_exit()

                        input_active = key

                        # entering fields: clear-on-focus behavior
                        if key == "month":
                            _begin_month_typing()
                        elif key == "day":
                            _begin_day_typing()
                        elif key == "start_time":
                            _begin_start_time_typing()
                    # Spinners (do not change focus)
                    elif key == "month_up":
                        raw = edit_state.get("month", str(datetime.now().month))
                        cur = int(raw) if raw.isdigit() else (list(calendar.month_name).index(raw) or 1)
                        nxt = cur + 1 if cur < 12 else 1
                        edit_state["month"] = calendar.month_name[nxt]
                    elif key == "month_down":
                        raw = edit_state.get("month", str(datetime.now().month))
                        cur = int(raw) if raw.isdigit() else (list(calendar.month_name).index(raw) or 1)
                        prev = cur - 1 if cur > 1 else 12
                        edit_state["month"] = calendar.month_name[prev]
                    elif key == "day_up":
                        d = int(edit_state.get("day", "1") or 1)
                        edit_state["day"] = str(min(d + 1, 31))
                    elif key == "day_down":
                        d = int(edit_state.get("day", "1") or 1)
                        edit_state["day"] = str(max(d - 1, 1))
                    elif key in ("start_time_up", "start_time_down"):
                        s = (edit_state.get("start_time", "") or "").zfill(4)[:4]
                        try:
                            hh = int(s[:2]); mm = int(s[2:])
                        except Exception:
                            now = datetime.now(); hh, mm = now.hour, now.minute
                        if key == "start_time_up":
                            mm += 15
                            if mm >= 60: mm = 0; hh = (hh + 1) % 24
                        else:
                            mm -= 15
                            if mm < 0:  mm = 45; hh = (hh - 1) % 24
                        edit_state["start_time"] = f"{hh:02d}{mm:02d}"
                    break


            # --- click-away blur (if click not on any control) ---
            hit_any = False
            for rect, key in edit_buttons:
                if rect.collidepoint(event.pos):
                    hit_any = True
                    break
            if (cancel_button_rect and cancel_button_rect.collidepoint(event.pos)) or \
            (done_button_rect   and done_button_rect.collidepoint(event.pos)):
                hit_any = True
            if key in ("name", "cost", "done", "month", "day", "start_time"):
                # commit the field we're leaving, if it is one of the special clears
                if input_active == "month" and key != "month":
                    _commit_month_on_exit()
                if input_active == "day" and key != "day":
                    _commit_day_on_exit()
                if input_active == "start_time" and key != "start_time":
                    _commit_start_time_on_exit()

                input_active = key

                # entering fields: clear-on-focus behavior
                if key == "month":
                    _begin_month_typing()
                elif key == "day":
                    _begin_day_typing()
                elif key == "start_time":
                    _begin_start_time_typing()

        # Keyboard events for active field
        if event.type == pygame.KEYDOWN and input_active:
            # Tab order
            if event.key == pygame.K_TAB:
                # commit the field we are leaving
                if input_active == "month":
                    _commit_month_on_exit()
                elif input_active == "day":
                    _commit_day_on_exit()
                elif input_active == "start_time":
                    _commit_start_time_on_exit()

                tab_order = ["name", "cost", "done", "month", "day", "start_time"]
                try:
                    i = tab_order.index(input_active)
                except ValueError:
                    i = -1
                input_active = tab_order[(i + 1) % len(tab_order)]

                # begin clear-on-focus for the field we enter
                if input_active == "month":
                    _begin_month_typing()
                elif input_active == "day":
                    _begin_day_typing()
                elif input_active == "start_time":
                    _begin_start_time_typing()

                return False, spoons, confetti_particles, streak_dates, level

            # Enter does nothing
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return False, spoons, confetti_particles, streak_dates, level

            cur = edit_state.get(input_active, "")

            if event.key == pygame.K_BACKSPACE:
                edit_state[input_active] = cur[:-1]
                return False, spoons, confetti_particles, streak_dates, level

            ch = event.unicode or ""
            if input_active == "name":
                if ch:
                    candidate = cur + ch
                    if font.size(candidate)[0] <= MAX_TASK_PIXEL_WIDTH:
                        edit_state["name"] = candidate

            elif input_active in ("cost", "done"):
                if ch.isdigit():
                    edit_state[input_active] = cur + ch

            elif input_active == "month":
                # raw typed text; draw layer handles ghost suggestion & commit on blur/tab
                if ch.isalpha():
                    edit_state["month"] = cur + ch

            elif input_active == "day":
                if ch.isdigit() and len(cur) < 2:
                    edit_state["day"] = cur + ch

            elif input_active == "start_time":
                if ch.isdigit() and len(cur) < 4:
                    edit_state["start_time"] = cur + ch

    
    # Typing for NEW label (only in list mode)
    if new_label_active_task is not None and event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RETURN:
            _commit_new_label()
            return False, spoons, confetti_particles, streak_dates, level
        elif event.key == pygame.K_ESCAPE:
            # cancel
            new_label_active_task = None
            new_label_text = ""
            return False, spoons, confetti_particles, streak_dates, level
        elif event.key == pygame.K_BACKSPACE:
            new_label_text = new_label_text[:-1]
            return False, spoons, confetti_particles, streak_dates, level
        else:
            ch = event.unicode
            if ch:
                # prevent overflow: ensure rendered width fits inside label_new_border
                lbw = label_new_border.get_width()
                inner_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(pygame.display.get_surface().get_height() * 0.045))
                test = new_label_text + ch
                if inner_font.size(test)[0] <= (lbw - 12):  # light padding
                    new_label_text = test
            return False, spoons, confetti_particles, streak_dates, level

    # --- List mode: handle remove/edit icon and spoon-frame clicks ---
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        # No label button in LIST view anymore (time badge only) — do nothing here
        pass

        # Remove or enter edit
        for icon_rect, idx in remove_buttons:
            if icon_rect.collidepoint(event.pos):
                mid = icon_rect.y + icon_rect.height//2
                if event.pos[1] < mid:
                    # Remove task
                    expanded_label_tasks.discard(idx)
                    if idx in expanded_label_tasks: expanded_label_tasks.discard(idx)
                    task_list.pop(idx)
                else:
                    # Enter edit
                    name, cost, done_, days, date, st, et, labels = task_list[idx]
                    expanded_label_tasks.clear()
                    # make a HHMM digits string from task start_time [hh,mm,*,*] if present
                    def _st_to_digits(st):
                        try:
                            hh = int(st[0]) % 24
                            mm = int(st[1]) % 60
                            return f"{hh:02d}{mm:02d}"
                        except Exception:
                            return ""

                    edit_state = {
                        "name":   name,
                        "cost":   str(cost),
                        "done":   str(done_),
                        "month":  str(date.month),
                        "day":    str(date.day),
                        "labels": labels[:],
                        "start_time": _st_to_digits(st),
                    }
                    currently_editing = idx
                return False, spoons, confetti_particles, streak_dates, level

        # Spoon-frame clicks
        for rect, idx, frame_i in frame_buttons:
            if rect.collidepoint(event.pos):
                name, cost, done_, days, date, st, et, labels = task_list[idx]
                new_done = frame_i + 1
                to_fill  = new_done - done_
                if to_fill > 0 and spoons >= to_fill:
                    task_list[idx][2] = min(cost, new_done)
                    spoons -= to_fill

                    # Fractional level-up: each spoon gives 1/threshold
                    for _ in range(to_fill):
                        base_lvl = int(level)             # e.g. 0, 1, 2, ...
                        threshold = 10 + 2 * base_lvl     # 10, 12, 14, ...
                        level += 1.0 / threshold

                break

    return False, spoons, confetti_particles, streak_dates, level
