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

# Scrolling layout constants
CONTENT_TOP     = 148   # Where content starts
VIEWPORT_HEIGHT = 350   # Visible content height
SCROLL_X        = 910   # Scrollbar X
SCROLL_Y        = 140   # Scrollbar Y
TRACK_HEIGHT    = 330   # Scrollbar track height

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
    global edit_buttons, remove_buttons, frame_buttons
    edit_buttons.clear()
    remove_buttons.clear()
    buttons.clear()
    frame_buttons.clear()

    # If we're editing, draw the edit UI instead of the list
    if currently_editing is not None:
        _draw_edit_form(screen, background_color, icon_image, spoons)
        return scroll_offset_px, 0

    # --- existing drawing logic below ---
    border_img   = task_spoons_border
    siding_img   = progress_bar_spoon_siding
    top_img      = progress_bar_spoon_top
    bottom_img   = pygame.transform.flip(top_img, False, True)
    right_siding = pygame.transform.flip(siding_img, True, False)
    remove_edit  = remove_edit_icons

    DARK_BROWN      = (40, 25, 22)
    LIGHT_BROWN     = (85, 60, 53)
    VERY_DARK_BROWN = (20, 12, 10)
    t       = pygame.time.get_ticks() / 300.0
    pulse   = (math.sin(t) + 1) / 2.0
    def lerp(a, b, f):
        return (
            int(a[0] + (b[0] - a[0]) * f),
            int(a[1] + (b[1] - a[1]) * f),
            int(a[2] + (b[2] - a[2]) * f),
        )

    overdue, upcoming, completed = [], {}, []
    for idx, (name, cost, done, days, date, st, et) in enumerate(task_list):
        if done >= cost:
            completed.append((idx, name, cost, done, days, date, st, et))
        elif days < 0:
            overdue.append((idx, name, cost, done, days, date, st, et))
        else:
            upcoming.setdefault(days, []).append((idx, name, cost, done, days, date, st, et))
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

    total_content_height = y_cursor - CONTENT_TOP
    max_scroll = max(0, total_content_height - VIEWPORT_HEIGHT)
    scroll_offset_px = max(0, min(scroll_offset_px, max_scroll))

    # scrollbar
    screen.blit(scroll_bar, (SCROLL_X, SCROLL_Y))
    if total_content_height <= VIEWPORT_HEIGHT:
        slider_h, slider_y = TRACK_HEIGHT, SCROLL_Y
    else:
        slider_h = max(int((VIEWPORT_HEIGHT/total_content_height)*TRACK_HEIGHT), 20)
        slider_y = SCROLL_Y + int((scroll_offset_px/(total_content_height-VIEWPORT_HEIGHT))*(TRACK_HEIGHT-slider_h))
    slider_x = SCROLL_X + (20 - scroll_bar_slider.get_width())//2
    screen.blit(pygame.transform.scale(scroll_bar_slider, (scroll_bar_slider.get_width(), slider_h)),
                (slider_x, slider_y))

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

        for idx, name, cost, done, days, date, st, et in items:
            by = y_cur - scroll_offset_px
            if not (by+50 < CONTENT_TOP or by > CONTENT_TOP+VIEWPORT_HEIGHT):
                # border+name
                screen.blit(border_img, (138, by))
                ts = task_font.render(name, True, BLACK) #type: ignore
                screen.blit(ts, (148, by+12))

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

    return scroll_offset_px, total_content_height


def _draw_edit_form(screen, background_color, icon_image, spoons):
    """
    Draws the edit form for the selected task, including:
    - Live preview of the current task (header + task box with spoon slots & icons)
    - Input fields in three layers:
      * Task Name (400px)
      * Due Month / Due Day (200px each)
      * Cost / Done (100px each)
    """
    global edit_buttons, cancel_button_rect, done_button_rect
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
    # after: never let cost > 10, and never let done > cost
    raw_cost = int(edit_state.get("cost", "0") or 0)
    cost = max(0, min(10, raw_cost))
    raw_done = int(edit_state.get("done", "0") or 0)
    done = max(0, min(cost, raw_done))

    raw_month = edit_state.get("month", str(datetime.now().month)) or str(datetime.now().month)
    try:
        mon_int = int(raw_month)
    except ValueError:
        # month name → index in calendar.month_name
        mon_int = list(calendar.month_name).index(raw_month) or datetime.now().month
    mon = max(1, min(12, mon_int))

    raw_day = edit_state.get("day", str(datetime.now().day)) or str(datetime.now().day)
    try:
        day_int = int(raw_day)
    except ValueError:
        day_int = 1
    day = max(1, min(31, day_int))


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
    screen.blit(task_font.render(name, True, BLACK), (148, py+12)) #type: ignore

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

    # --- Inputs ---
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

    # Month/Day
    y1 = y0+h+sp + 30
    mon_rect=pygame.Rect(x1,y1,200,h)
    day_rect=pygame.Rect(x1+200+sp,y1,100,h)
    screen.blit(header_font.render("Due Month:",True,WHITE),(x1 +40,y1 - 30)) #type: ignore
    draw_input_box(screen,mon_rect,False,calendar.month_name[mon],LIGHT_GRAY,DARK_SLATE_GRAY,False,background_color,"light") #type: ignore
    screen.blit(header_font.render("Due Day:",True,WHITE),(x1+200+sp + 10,y1 - 30)) #type: ignore
    draw_input_box(screen,day_rect,False,str(day),LIGHT_GRAY,DARK_SLATE_GRAY,True,background_color,"light") #type: ignore
    # arrows
    arrow=font.render(">",True,arrow_color)
    up=pygame.transform.rotate(arrow,90)
    dn=pygame.transform.rotate(arrow,270)
    m_up=pygame.Rect(mon_rect.right-23,mon_rect.y+5,15,15)
    m_dn=pygame.Rect(mon_rect.right-23,mon_rect.y+mon_rect.height-20,15,15)
    d_up=pygame.Rect(day_rect.right-23,day_rect.y+5,15,15)
    d_dn=pygame.Rect(day_rect.right-23,day_rect.y+day_rect.height-20,15,15)
    for b in (m_up,m_dn,d_up,d_dn): pygame.draw.rect(screen,input_box_color,b)
    screen.blit(up,(m_up.left - 6, m_up.top + 3)); screen.blit(dn,(m_dn.left - 9, m_dn.top - 3))
    screen.blit(up,(d_up.left - 6, d_up.top + 3)); screen.blit(dn,(d_dn.left - 9, d_dn.top - 3))
    edit_buttons += [(m_up,"month_up"),(m_dn,"month_down"),(d_up,"day_up"),(d_dn,"day_down")]


    # Buttons
    yb=y1+h+sp
    cancel_button_rect=pygame.Rect(x1,yb,120,40)
    done_button_rect=pygame.Rect(x1+200+sp,yb,120,40)
    draw_rounded_button(screen,cancel_button_rect,RED,BLACK) #type: ignore
    draw_rounded_button(screen,done_button_rect,GREEN,BLACK) #type: ignore



    
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


def logic_complete_tasks(task_list, buttons, event, spoons, streak_dates, confetti_particles):
    """
    Handles clicks and key events for both list and edit form.
    """
    global currently_editing, edit_state, input_active, cancel_button_rect, done_button_rect

    # --- Edit mode ---
    if currently_editing is not None:
        # Mouse events
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Cancel edit
            if cancel_button_rect and cancel_button_rect.collidepoint(event.pos):
                currently_editing = None
                input_active = None
                return False, spoons, confetti_particles, streak_dates

            # Save edits
            if done_button_rect and done_button_rect.collidepoint(event.pos):
                # Extract values
                name  = edit_state.get("name", "")
                cost  = int(edit_state.get("cost", "0") or 0)
                done_ = int(edit_state.get("done", "0") or 0)
                # Month stored as name or number
                raw_month = edit_state.get("month", str(datetime.now().month))
                if raw_month.isdigit():
                    mon = int(raw_month)
                else:
                    mon = list(calendar.month_name).index(raw_month) or 1
                day = int(edit_state.get("day", "1") or 1)

                # Update task   
                orig = task_list[currently_editing]
                new_date = orig[4].replace(month=mon, day=day)
                new_days = (new_date - datetime.now()).days + 1
                task_list[currently_editing] = [name, cost, done_, new_days, new_date, orig[5], orig[6]]

                currently_editing = None
                input_active = None
                return False, spoons, confetti_particles, streak_dates

            # Clicked on a field or arrow
            for rect, key in edit_buttons:
                if rect.collidepoint(event.pos):
                    # Activate text input
                    if key in ("name", "cost", "done"):
                        input_active = key
                    # Month up/down
                    elif key == "month_up":
                        raw = edit_state.get("month", str(datetime.now().month))
                        cur = int(raw) if raw.isdigit() else list(calendar.month_name).index(raw) or 1
                        nxt = cur + 1 if cur < 12 else 1
                        edit_state["month"] = calendar.month_name[nxt]
                    elif key == "month_down":
                        raw = edit_state.get("month", str(datetime.now().month))
                        cur = int(raw) if raw.isdigit() else list(calendar.month_name).index(raw) or 1
                        prev = cur - 1 if cur > 1 else 12
                        edit_state["month"] = calendar.month_name[prev]
                    # Day up/down
                    elif key == "day_up":
                        d = int(edit_state.get("day", "1") or 1)
                        edit_state["day"] = str(min(d+1, 31))
                    elif key == "day_down":
                        d = int(edit_state.get("day", "1") or 1)
                        edit_state["day"] = str(max(d-1, 1))
                    break

        # Keyboard events for active field
        if event.type == pygame.KEYDOWN and input_active:
            # Backspace
            if event.key == pygame.K_BACKSPACE:
                edit_state[input_active] = edit_state.get(input_active, "")[:-1]
            # Append character
            elif input_active == "name":
                edit_state[input_active] = edit_state.get(input_active, "") + event.unicode
            elif input_active in ("cost", "done") and event.unicode.isdigit():
                edit_state[input_active] = edit_state.get(input_active, "") + event.unicode

        return False, spoons, confetti_particles, streak_dates

    # --- List mode: handle remove/edit icon and spoon-frame clicks ---
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        # Remove or enter edit
        for icon_rect, idx in remove_buttons:
            if icon_rect.collidepoint(event.pos):
                mid = icon_rect.y + icon_rect.height//2
                if event.pos[1] < mid:
                    # Remove task
                    task_list.pop(idx)
                else:
                    # Enter edit
                    name, cost, done_, days, date, st, et = task_list[idx]
                    edit_state = {
                        "name":  name,
                        "cost":  str(cost),
                        "done":  str(done_),
                        "month": str(date.month),
                        "day":   str(date.day)
                    }
                    currently_editing = idx
                return False, spoons, confetti_particles, streak_dates

        # Spoon-frame clicks
        for rect, idx, frame_i in frame_buttons:
            if rect.collidepoint(event.pos):
                name, cost, done_, days, date, st, et = task_list[idx]
                new_done = frame_i + 1
                to_fill  = new_done - done_
                if to_fill > 0 and spoons >= to_fill:
                    task_list[idx][2] = min(cost, new_done)
                    spoons -= to_fill
                break

    return False, spoons, confetti_particles, streak_dates
