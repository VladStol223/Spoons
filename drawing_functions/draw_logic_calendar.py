import pygame
from datetime import datetime
import calendar
from config import *
from drawing_functions.draw_rounded_button import draw_rounded_button


day_mode_button   = pygame.Rect(120, 25,  120, 30)
week_mode_button  = pygame.Rect(260, 25,  120, 30)
month_mode_button = pygame.Rect(665, 25,  120, 30)
year_mode_button  = pygame.Rect(805, 25,  120, 30)

def blend(c1, c2):
    """Return the midpoint blend of two RGB colors."""
    return (
        (c1[0] + c2[0]*3) // 4,
        (c1[1] + c2[1]*3) // 4,
        (c1[2] + c2[2]*3) // 4,)


def draw_calendar(screen, spoon_name_input,
                  homework_tasks_list, chores_tasks_list, work_tasks_list,
                  misc_tasks_list, exams_tasks_list, projects_tasks_list,
                  displayed_month, displayed_year, background_color,
                  homework_fol_color, chores_fol_color, work_fol_color,
                  misc_fol_color, calendar_month_color,
                  calendar_previous_day_header_color, calendar_next_day_header_color,
                  calendar_current_day_header_color,
                  calendar_previous_day_color, calendar_current_day_color,
                  calendar_next_day_color,
                  folder_one, folder_two, folder_three, folder_four,
                  folder_five, folder_six,
                  streak_dates):

    screen_width, screen_height = screen.get_size()
    bigger_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen_height * 0.075))
    smaller_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen_height * 0.033))
    font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen_height * 0.035))
    r, g, b = background_color
    darker_background = (max(r - 40, 0), max(g - 40, 0), max(b - 40, 0))
    lighter_background = (min(r + 20, 255), min(g + 20, 255), min(b + 20, 255))

    # —— draw your mode buttons ——  
    for btn, label in [
        (day_mode_button,   "day"),
        (week_mode_button,  "week"),
        (month_mode_button, "month"),
        (year_mode_button,  "year"),
    ]:
        pygame.draw.rect(screen, darker_background, btn)      # button bg
        txt = font.render(label, True, BLACK) #type: ignore
        txt_rect = txt.get_rect(center=btn.center)
        screen.blit(txt, txt_rect)

    if calendar_mode == "day":
        draw_day_mode()

    elif calendar_mode == "week":
        draw_week_mode(screen, font, bigger_font, smaller_font, 
                        homework_tasks_list, chores_tasks_list, work_tasks_list,
                        misc_tasks_list, exams_tasks_list, projects_tasks_list,
                        displayed_month, displayed_year, background_color,
                        calendar_previous_day_header_color, calendar_next_day_header_color,
                        calendar_current_day_header_color,
                        calendar_previous_day_color, calendar_current_day_color,
                        calendar_next_day_color, streak_dates,
                        lighter_background, darker_background)

    elif calendar_mode == "month":
        draw_month_mode(screen, font, bigger_font, smaller_font,
                        darker_background, lighter_background,
                        homework_tasks_list, chores_tasks_list,
                        work_tasks_list, misc_tasks_list,
                        exams_tasks_list, projects_tasks_list,
                        displayed_month, displayed_year, background_color,
                        calendar_previous_day_header_color,
                        calendar_next_day_header_color,
                        calendar_current_day_header_color,
                        calendar_previous_day_color,
                        calendar_current_day_color,
                        calendar_next_day_color,
                        streak_dates)

    elif calendar_mode == "year":
        draw_year_mode(screen, font, smaller_font, bigger_font,
                        darker_background, lighter_background,
                        displayed_year, background_color)

def draw_day_mode():
    pass

def draw_week_mode(screen, font, bigger_font, smaller_font,
    homework_tasks_list, chores_tasks_list, work_tasks_list,
    misc_tasks_list, exams_tasks_list, projects_tasks_list,
    displayed_month, displayed_year, background_color,
    prev_hdr_col, next_hdr_col, curr_hdr_col,
    prev_col, curr_col, next_col, streak_dates,
    lighter_background, darker_background):

    draw_rounded_button(screen, previous_month_button, lighter_background, lighter_background, 0)
    draw_rounded_button(screen, next_month_button, lighter_background, lighter_background, 0)
    right_arrow = bigger_font.render(">", True, darker_background)
    left_arrow = pygame.transform.rotate(right_arrow, 180)
    screen.blit(left_arrow, (419, 2))
    screen.blit(right_arrow, (606, 5))

    today = datetime.now()
    # box dimensions & positions
    day_box_width  = 105
    day_box_height = 120
    margin         = 0
    start_x        = 160
    start_y        = 74

    # compute month boundaries
    prev_month = displayed_month - 1 or 12
    prev_year  = displayed_year - (1 if displayed_month == 1 else 0)
    next_month = displayed_month + 1 if displayed_month < 12 else 1
    next_year  = displayed_year + (1 if displayed_month == 12 else 0)

    first_wd, num_days = calendar.monthrange(displayed_year, displayed_month)
    first_wd = (first_wd + 1) % 7            # convert Mon=0 → Sun=0
    _, prev_days      = calendar.monthrange(prev_year, prev_month)

    # 1) Day‐of‐week headers
    days = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]
    for i, d in enumerate(days):
        hdr_txt = big_font.render(d, True, (0,0,0))
        screen.blit(hdr_txt, (start_x + i*(day_box_width+margin) + 25, 67))
    # 2) The single row of date‐boxes
    y = start_y + font.get_height() + 5
    for col in range(7):
        x = start_x + col*(day_box_width + margin)
        offset = col - first_wd + 1

        # pick which month/day
        if offset < 1:
            day   = prev_days + offset
            slot  = datetime(prev_year, prev_month, day)
            hdr_c = blend(prev_hdr_col, background_color)
            box_c = blend(prev_col,      background_color)
        elif offset > num_days:
            day   = offset - num_days
            slot  = datetime(next_year, next_month, day)
            hdr_c = blend(next_hdr_col, background_color)
            box_c = blend(next_col,     background_color)
        else:
            day  = offset
            slot = datetime(displayed_year, displayed_month, day)
            if   slot.date() < today.date():  hdr_c, box_c = prev_hdr_col, prev_col
            elif slot.date() > today.date():  hdr_c, box_c = next_hdr_col, next_col
            else:                              hdr_c, box_c = curr_hdr_col, curr_col

        # header rectangle
        pygame.draw.rect(screen, hdr_c, (x, y, day_box_width, day_box_height//4))
        pygame.draw.rect(screen, (0,0,0), (x, y, day_box_width, day_box_height//4), 1)
        # body rectangle
        body_y = y + day_box_height//4
        pygame.draw.rect(screen, box_c, (x, body_y, day_box_width, day_box_height*3))
        pygame.draw.rect(screen, (0,0,0), (x, body_y, day_box_width, day_box_height*3), 1)

        # day number
        dn = font.render(str(day), True, (0,0,0))
        screen.blit(dn, (x + day_box_width - 20, y + 2))

        # streak indicator
        date_str = slot.strftime("%Y-%m-%d")
        if any(start <= date_str <= end for start, end in streak_dates):
            s = font.render("S", True, (0,0,0))
            screen.blit(s, (x + day_box_width - 35, y + 2))

        # tasks due that day
        tasks = []
        for lst, col in [
            (homework_tasks_list, (0,0,0)),
            (chores_tasks_list,   (0,0,0)),
            (work_tasks_list,     (0,0,0)),
            (misc_tasks_list,     (0,0,0)),
            (exams_tasks_list,    (0,0,0)),
            (projects_tasks_list, (0,0,0)),
        ]:
            for t in lst:
                if t[4] == slot:
                    tasks.append((t[0], col))

        ty = body_y + 5
        # show up to 3 tasks, then “+N more”
        for name, col in tasks[:3]:
            surf = smaller_font.render(name, True, col)
            screen.blit(surf, (x + 5, ty))
            ty += smaller_font.get_height() - 2
        if len(tasks) > 3:
            more = smaller_font.render(f"+{len(tasks)-3} more", True, (0,0,0))
            screen.blit(more, (x + 5, ty))

def draw_month_mode(screen, font, bigger_font, smaller_font, darker_background, lighter_background,
                  homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list, exams_tasks_list, projects_tasks_list,
                  displayed_month, displayed_year, background_color,
                  calendar_previous_day_header_color, calendar_next_day_header_color, calendar_current_day_header_color,
                  calendar_previous_day_color, calendar_current_day_color, calendar_next_day_color,
                  streak_dates):
    # Calendar grid settings
    day_box_width = 105
    margin = 0
    start_x = 160
    start_y = 97
    top_padding = 30
    days_of_week = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    today_date = datetime.now()

    # Compute month boundaries
    prev_month = displayed_month - 1 or 12
    prev_year = displayed_year - (1 if displayed_month == 1 else 0)
    next_month = displayed_month + 1 if displayed_month < 12 else 1
    next_year = displayed_year + (1 if displayed_month == 12 else 0)

    first_weekday, num_days = calendar.monthrange(displayed_year, displayed_month)
    first_weekday = (first_weekday + 1) % 7
    _, prev_num_days = calendar.monthrange(prev_year, prev_month)

    total_days = first_weekday + num_days
    day_box_height = 65
    folder_box_height = 12

    # Draw month header and navigation
    draw_rounded_button(screen, previous_month_button, lighter_background, lighter_background, 0)
    draw_rounded_button(screen, next_month_button, lighter_background, lighter_background, 0)
    right_arrow = bigger_font.render(">", True, darker_background)
    left_arrow = pygame.transform.rotate(right_arrow, 180)
    screen.blit(left_arrow, (419, 2))
    screen.blit(right_arrow, (606, 5))
    month_str = calendar.month_name[displayed_month]
    month_text = big_font.render(month_str, True, BLACK) #type: ignore
    screen.blit(month_text, month_text.get_rect(midtop=(522, 7)))

    # Day-of-week labels
    for i, day_name in enumerate(days_of_week):
        day_text = big_font.render(day_name, True, BLACK) #type: ignore
        screen.blit(day_text, (start_x + i * (day_box_width + margin) + 25, start_y - top_padding))

    # Draw 6x7 grid of days
    for idx in range(42):
        row = idx // 7
        col = idx % 7
        x = start_x + col * (day_box_width + margin)
        y = start_y + row * (day_box_height + margin)

        # Determine which day to display
        day_offset = idx - first_weekday + 1
        if day_offset < 1:
            # previous month
            disp_day = prev_num_days + day_offset
            slot_date = datetime(prev_year, prev_month, disp_day)
            hdr_col = blend(calendar_previous_day_header_color, background_color)
            box_col = blend(calendar_previous_day_color, background_color)
        elif day_offset > num_days:
            # next month
            disp_day = day_offset - num_days
            slot_date = datetime(next_year, next_month, disp_day)
            hdr_col = blend(calendar_next_day_header_color, background_color)
            box_col = blend(calendar_next_day_color, background_color)
        else:
            # current month
            disp_day = day_offset
            slot_date = datetime(displayed_year, displayed_month, disp_day)
            if slot_date < today_date:
                hdr_col = calendar_previous_day_header_color
                box_col = calendar_previous_day_color
            elif slot_date > today_date:
                hdr_col = calendar_next_day_header_color
                box_col = calendar_next_day_color
            else:
                hdr_col = calendar_current_day_header_color
                box_col = calendar_current_day_color

        # Header rectangle
        pygame.draw.rect(screen, hdr_col, (x, y, day_box_width, day_box_height))
        pygame.draw.rect(screen, BLACK, (x, y, day_box_width, day_box_height), 1) #type: ignore

        # Body slice
        slice_top = y + (14 if total_days > 35 else 16)
        slice_h = day_box_height - (14 if total_days > 35 else 16)
        pygame.draw.rect(screen, box_col, (x, slice_top, day_box_width, slice_h))
        pygame.draw.rect(screen, BLACK, (x, slice_top, day_box_width, slice_h), 1) #type: ignore

        # Day number
        day_text = smaller_font.render(str(disp_day), True, BLACK) #type: ignore
        tx = x + day_box_width - (19 if disp_day > 9 else 11)
        screen.blit(day_text, (tx, y + 1))

        # Draw streak indicator if needed
        date_str = slot_date.strftime("%Y-%m-%d")
        if any(start <= date_str <= end for start, end in streak_dates):
            s_text = smaller_font.render("S", True, BLACK) #type: ignore
            screen.blit(s_text, (x + day_box_width - 33, y + 1))

                # — instead of folder rectangles, render up to 3 lines of text — 
        line_height = smaller_font.get_height()
        text_y = slice_top + 2

                # — build list of (task_list, display_color) in the order you want —
        folders = [
            (homework_tasks_list, BLACK), #type: ignore
            (chores_tasks_list,   BLACK), #type: ignore
            (work_tasks_list,     BLACK), #type: ignore
            (misc_tasks_list,     BLACK), #type: ignore
            (exams_tasks_list,    BLACK), #type: ignore
            (projects_tasks_list, BLACK), #type: ignore
        ]

        all_due = []
        for lst, col in folders:
            for t in lst:
                if t[4] == slot_date:
                    all_due.append((t[0], col))

        total = len(all_due)
        text_y = slice_top + 2
        line_h = smaller_font.get_height() - 2

        if total <= 3:
            # show every single task (up to 3)
            for name, col in all_due:
                surf = smaller_font.render(name, True, col)
                screen.blit(surf, (x + 5, text_y))
                text_y += line_h
        else:
            # show first two tasks
            for name, col in all_due[:2]:
                surf = smaller_font.render(name, True, col)
                screen.blit(surf, (x + 5, text_y))
                text_y += line_h
            # then “+N” for the rest
            more = smaller_font.render(f"{total-2} other tasks", True, BLACK) #type: ignore
            screen.blit(more, (x + 5, text_y))

def draw_year_mode(
    screen, font, smaller_font, bigger_font,
    darker_background, lighter_background,
    displayed_year, background_color
):
    screen_w, screen_h = screen.get_size()
    # region bounds
    region_x, region_y = 115, 70
    region_w = screen_w - region_x - 25
    region_h = screen_h - region_y - 25

    year_str = str(displayed_year)
    year_text = big_font.render(year_str, True, BLACK) #type: ignore
    screen.blit(year_text, year_text.get_rect(midtop=(522, 7)))

    draw_rounded_button(screen, previous_month_button, lighter_background, lighter_background, 0)
    draw_rounded_button(screen, next_month_button, lighter_background, lighter_background, 0)
    right_arrow = bigger_font.render(">", True, darker_background)
    left_arrow = pygame.transform.rotate(right_arrow, 180)
    screen.blit(left_arrow, (419, 2))
    screen.blit(right_arrow, (606, 5))

    # grid settings
    cols, rows = 4, 3
    gap_x, gap_y = 10, 10  # space between month‐cells

    cell_w = (region_w - gap_x*(cols-1)) / cols
    cell_h = (region_h - gap_y*(rows-1)) / rows

    for month in range(1, 13):
        col = (month - 1) % cols
        row = (month - 1) // cols

        x = region_x + col*(cell_w + gap_x)
        y = region_y + row*(cell_h + gap_y)

        # draw month frame
        pygame.draw.rect(screen, lighter_background, (x, y, cell_w, cell_h))

        # month name + underline
        name_surf = font.render(calendar.month_name[month], True, BLACK) #type: ignore
        tx = x + (cell_w - name_surf.get_width()) / 2
        ty = y + 5
        screen.blit(name_surf, (tx, ty))
        ul_y = ty + name_surf.get_height() + 2
        pygame.draw.line(screen, BLACK, (tx, ul_y), (tx + name_surf.get_width(), ul_y), 2) #type: ignore

        # days grid inside this cell
        first_wd, num_days = calendar.monthrange(displayed_year, month)
        first_wd = (first_wd + 1) % 7  # convert Mon=0 → Sun=0

        # reserve space below underline for day numbers
        days_y0 = ul_y + 8
        grid_h = cell_h - (days_y0 - y) - 5
        weeks = 6
        day_h = grid_h / weeks
        day_w = cell_w / 7

        for day in range(1, num_days + 1):
            idx = first_wd + (day - 1)
            wd = idx % 7   # column 0–6
            wk = idx // 7  # row 0–5

            cx = x + wd * day_w
            cy = days_y0 + wk * day_h

            day_surf = smaller_font.render(str(day), True, BLACK) #type: ignore
            dr = day_surf.get_rect(center=(cx + day_w/2, cy + day_h/2))
            screen.blit(day_surf, dr)

def logic_calendar(event, displayed_month, displayed_year):
    global calendar_mode

    if event.type == pygame.MOUSEBUTTONDOWN:
        # —— mode switching ——  
        if day_mode_button.collidepoint(event.pos):
            calendar_mode = "day"
        elif week_mode_button.collidepoint(event.pos):
            calendar_mode = "week"
        elif month_mode_button.collidepoint(event.pos):
            calendar_mode = "month"
        elif year_mode_button.collidepoint(event.pos):
            calendar_mode = "year"

        # —— existing month nav ——  
        if calendar_mode == "month":
            if previous_month_button.collidepoint(event.pos):
                displayed_month -= 1
                if displayed_month < 1:
                    displayed_month = 12
                    displayed_year -= 1

            elif next_month_button.collidepoint(event.pos):
                displayed_month += 1
                if displayed_month > 12:
                    displayed_month = 1
                    displayed_year += 1

        if calendar_mode == "year":
            if previous_month_button.collidepoint(event.pos):
                displayed_year -= 1

            elif next_month_button.collidepoint(event.pos):
                displayed_year += 1

    return displayed_month, displayed_year