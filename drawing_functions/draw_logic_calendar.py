import pygame
from datetime import datetime, timedelta
import calendar
import random
from config import *
from drawing_functions.draw_rounded_button import draw_rounded_button


day_mode_button   = pygame.Rect(120, 25,  120, 30)
week_mode_button  = pygame.Rect(260, 25,  120, 30)
month_mode_button = pygame.Rect(665, 25,  120, 30)
year_mode_button  = pygame.Rect(805, 25,  120, 30)

# the discrete steps you want to cycle through
day_ranges = [
    ("Day",   1), ("Day",   2), ("Day",   3),
    ("Day",   4), ("Day",   5), ("Day",   6),
    ("Week",  1), ("Week",  2), ("Week",  3),
    ("Month", 1), ("Month", 2), ("Month", 4),
    ("Month", 6), ("Month", 9), ("Year",  1)
]

def blend(c1, c2):
    """Return the midpoint blend of two RGB colors ."""
    return (
        (c1[0] + c2[0]*3) // 4,
        (c1[1] + c2[1]*3) // 4,
        (c1[2] + c2[2]*3) // 4,)

NO_TASK_MESSAGES = [
    "No tasks... relax!",
    "Clear skies on your schedule.",
    "Nothing on deck. breathe easy.",
    "Free day. treat yourself!",
    "Quiet calendar. Cozy vibes.",
    "You did it! nothing for today!",
    "Open lane. follow your curiosity.",
    "Blank slate. Paint it how you like.",
    "Cruise mode engaged.",
    "Rest is productive too."
]

def _weekly_message_picker(week_start_date, spoon_name=""):
    """
    Returns a function(day_index) -> message that is stable for the given ISO week.
    Ensures each weekday gets a unique message from the pool.
    """
    iso_year, iso_week, _ = week_start_date.isocalendar()
    seed_val = hash((iso_year, iso_week, spoon_name)) & 0xFFFFFFFF
    rng = random.Random(seed_val)
    order = list(range(len(NO_TASK_MESSAGES)))
    rng.shuffle(order)

    def pick(day_index_0_to_6):
        return NO_TASK_MESSAGES[order[day_index_0_to_6 % len(NO_TASK_MESSAGES)]]
    return pick

def draw_calendar(screen, spoon_name_input, displayed_week_offset, day_range_index, 
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

    left_border = 390
    right_border = 626
    pygame.draw.rect(screen, lighter_background, (left_border, 0, right_border - left_border + 18, 50))

    # —— draw your mode buttons ——  
    for btn, label in [
        (day_mode_button,   "Range"),
        (week_mode_button,  "Week"),
        (month_mode_button, "Month"),
        (year_mode_button,  "Year"),
    ]:
        pygame.draw.rect(screen, darker_background, btn)      # button bg
        txt = font.render(label, True, BLACK) #type: ignore
        txt_rect = txt.get_rect(center=btn.center)
        screen.blit(txt, txt_rect)

    if calendar_mode == "Range":
        draw_range_mode(screen, font, bigger_font, smaller_font, day_range_index,
                        homework_tasks_list, chores_tasks_list, work_tasks_list,
                        misc_tasks_list, exams_tasks_list, projects_tasks_list,
                        lighter_background, darker_background)

    elif calendar_mode == "Week":
        draw_week_mode(screen, font, bigger_font, smaller_font, displayed_week_offset,
                        homework_tasks_list, chores_tasks_list, work_tasks_list,
                        misc_tasks_list, exams_tasks_list, projects_tasks_list,
                        displayed_month, displayed_year, background_color,
                        calendar_previous_day_header_color, calendar_next_day_header_color,
                        calendar_current_day_header_color,
                        calendar_previous_day_color, calendar_current_day_color,
                        calendar_next_day_color, streak_dates,
                        lighter_background, darker_background,
                        folder_one, folder_two, folder_three, folder_four, folder_five, folder_six)

    elif calendar_mode == "Month":
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

    elif calendar_mode == "Year":
        draw_year_mode(screen, font, smaller_font, bigger_font, darker_background, lighter_background, displayed_year, background_color, homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list, exams_tasks_list, projects_tasks_list)

def draw_range_mode(
    screen, font, bigger_font, smaller_font, day_range_index,
    homework_tasks_list, chores_tasks_list, work_tasks_list,
    misc_tasks_list, exams_tasks_list, projects_tasks_list,
    lighter_background, darker_background):

    sw, sh = screen.get_size()
    today = datetime.now().date()

    # figure out which unit & count we're on (after the initial list, keep increasing years)
    if day_range_index < len(day_ranges):
        unit, count = day_ranges[day_range_index]
    else:
        unit   = "Year"
        count  = day_range_index - len(day_ranges) + 1

    # convert that into a timedelta (approximate months as 30 days)
    if   unit == "Day":   delta = timedelta(days=count)
    elif unit == "Week":  delta = timedelta(weeks=count)
    elif unit == "Month": delta = timedelta(days=30*count)
    else:                 delta = timedelta(days=365*count)

    # ----- HEADER: draw “–”, “X Unit(s)”, “+” -----
    # draw navigation buttons and header
    draw_rounded_button(screen, previous_month_button, lighter_background, lighter_background, 0)
    draw_rounded_button(screen, next_month_button, lighter_background, lighter_background, 0)
    right_arrow = bigger_font.render(">", True, darker_background)
    left_arrow = pygame.transform.rotate(right_arrow, 180)
    screen.blit(left_arrow, (414, 2))
    screen.blit(right_arrow, (611, 5))

    # week-range header
    range_str = f"{count} {unit}{'s' if count>1 else ''}"
    range_text = big_font.render(range_str, True, BLACK) #type: ignore
    screen.blit(range_text, range_text.get_rect(midtop=(530, 7)))

        # — after you blit your range_text —
    txt_rect = range_text.get_rect(midtop=(530, 7))

    # compute a x/y for the control glyph (left of the text)
    control_x = txt_rect.left - 20
    # size of the “arms” of the plus/minus
    arm = 6
    # vertical center of the plus
    mid_y = txt_rect.top + txt_rect.height // 2 - 10

    # 1) PLUS sign (horizontal + vertical)
    pygame.draw.line(screen, BLACK, #type: ignore
                     (control_x - arm, mid_y),
                     (control_x + arm, mid_y), 3)
    pygame.draw.line(screen, BLACK, #type: ignore
                     (control_x, mid_y - arm),
                     (control_x, mid_y + arm), 3)

    # 2) LONG dash (the “range” line)  
    dash_y = mid_y + arm + 5
    pygame.draw.line(screen, BLACK, #type: ignore
                     (control_x - arm*2, dash_y + 2),
                     (control_x + arm*2, dash_y - 2), 3)

    # 3) SHORT dash (the “minus”)
    minus_y = dash_y + arm + 2
    pygame.draw.line(screen, BLACK, #type: ignore
                     (control_x - arm, minus_y),
                     (control_x + arm, minus_y), 3)


    # ----- COLUMN HEADERS -----
    col_w = (sw - 100) / 3
    start_y =  bigger_font.get_height() + 25
    columns = ["Overdue", "To-Do", "Completed"]
    for i, title in enumerate(columns):
        hsurf = bigger_font.render(title, True, BLACK) #type: ignore
        hrect = hsurf.get_rect(midtop=(col_w*i + col_w/2 + 40, start_y))
        screen.blit(hsurf, hrect)
        pygame.draw.line(screen, BLACK, #type: ignore
                     (hrect.left, hrect.bottom - 3),
                     (hrect.right, hrect.bottom - 3), 3)

    # ----- GATHER + FILTER TASKS -----
    start_date = today - delta
    end_date   = today + delta

    all_tasks = []
    for lst in (homework_tasks_list, chores_tasks_list, work_tasks_list,
                misc_tasks_list, exams_tasks_list, projects_tasks_list):
        all_tasks.extend(lst)

    buckets = {"Overdue": [], "To-Do": [], "Completed": []}
    for t in all_tasks:
        try:
            if isinstance(t, dict):
                name = t.get("task_name", "")
                spoons = int(t.get("spoons_needed", 0))
                done = int(t.get("done", 0))
                due_date = t.get("due_date", None)
            else:
                name = t[0]
                spoons = int(t[2]) if len(t) > 2 else 0
                done = int(t[3]) if len(t) > 3 else 0
                due_date = t[5] if len(t) > 5 else None

            # Normalize due_date
            if isinstance(due_date, datetime):
                d = due_date.date()
            elif isinstance(due_date, str):
                try:
                    d = datetime.fromisoformat(due_date).date()
                except ValueError:
                    continue
            elif isinstance(due_date, date): #type: ignore
                d = due_date
            else:
                continue

            if not (start_date <= d <= end_date):
                continue

            if done >= spoons and spoons > 0:
                buckets["Completed"].append(name)
            elif d < today:
                buckets["Overdue"].append(name)
            else:
                buckets["To-Do"].append(name)
        except Exception:
            continue

    # ----- RENDER TASK NAMES IN EACH COLUMN -----
    text_y = start_y + font.get_height() + 30
    line_h = smaller_font.get_height() + 4
    for i, title in enumerate(columns):
        x0 = col_w*i + 130
        y0 = text_y
        for task_name in buckets[title]:
            tsurf = smaller_font.render(task_name, True, BLACK) #type: ignore
            screen.blit(tsurf, (x0, y0))
            y0 += line_h


def draw_week_mode(screen, font, bigger_font, smaller_font, displayed_week_offset,
    homework_tasks_list, chores_tasks_list, work_tasks_list,
    misc_tasks_list, exams_tasks_list, projects_tasks_list,
    displayed_month, displayed_year, background_color,
    prev_hdr_col, next_hdr_col, curr_hdr_col,
    prev_col, curr_col, next_col, streak_dates,
    lighter_background, darker_background,
    folder_one, folder_two, folder_three, folder_four, folder_five, folder_six):

    global week_folder_rects
    week_folder_rects = []

    def wrap_text(text, font, max_width):
        words = text.split()
        lines = []
        current_line = []
        current_width = 0

        space_width = font.size(' ')[0]
        for word in words:
            word_width = font.size(word)[0]
            # Start new line if current word doesn't fit
            if current_width + word_width > max_width and current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_width = word_width
            # Break word if it's too long for a new line
            elif word_width > max_width:
                # Break word into characters
                chars = list(word)
                part = ""
                for char in chars:
                    char_width = font.size(char)[0]
                    if current_width + char_width > max_width:
                        if part:
                            current_line.append(part)
                        lines.append(' '.join(current_line))
                        current_line = []
                        current_width = 0
                        part = char
                    else:
                        part += char
                        current_width += char_width
                if part:
                    current_line.append(part)
            else:
                # Add word to current line
                if current_line:
                    current_width += space_width
                current_line.append(word)
                current_width += word_width
        
        if current_line:
            lines.append(' '.join(current_line))
        return lines
    
    def wrap_text_two_widths(text, font, first_width, rest_width):
        """
        Wrap `text` so that the FIRST line uses `first_width`,
        and all subsequent lines use `rest_width`.
        """
        words = text.split()
        lines = []
        space_w = font.size(' ')[0]

        def wrap_with_width(words_iter, max_w):
            line_words = []
            cur_w = 0
            for w in words_iter:
                ww = font.size(w)[0]
                if line_words:
                    if cur_w + space_w + ww > max_w:
                        # emit this line and keep the word for the next pass
                        return ' '.join(line_words), [w] + list(words_iter)
                    else:
                        cur_w += space_w + ww
                        line_words.append(w)
                else:
                    if ww > max_w:
                        # hard-break ultra-long word into characters to fit in max_w
                        chars = list(w)
                        part = ""
                        width = 0
                        for ch in chars:
                            cw = font.size(ch)[0]
                            if width + cw > max_w and part:
                                # emit the piece so farokay 
                                return part, [w[len(part):]] + list(words_iter)
                            part += ch
                            width += cw
                        # whole word fits as one part
                        line_words.append(part)
                        cur_w = width
                    else:
                        line_words.append(w)
                        cur_w = ww
            # finished all words
            return ' '.join(line_words), []

        # first line
        if not words:
            return ['']
        line, leftover = wrap_with_width(iter(words), first_width)
        lines.append(line)

        # remaining lines
        rest = leftover
        while rest:
            line, rest = wrap_with_width(iter(rest), rest_width)
            lines.append(line if line else '')
        return lines

    def extract_start_time(task):
        """
        Returns 'HH:MM' (24h) or '' if no/zero time.
        Supports both dict and tuple/list task shapes.
        """
        try:
            if isinstance(task, dict):
                # Accept a few shapes: 'start_time' as 'HHMM' or [HH,MM,...]
                st = task.get('start_time', '')
                if isinstance(st, (list, tuple)) and len(st) >= 2:
                    hh, mm = int(st[0]), int(st[1])
                elif isinstance(st, str) and st.isdigit():
                    s = st.zfill(4)[:4]; hh, mm = int(s[:2]), int(s[2:])
                else:
                    return ''
            else:
                # tuple/list: index 5 is start_time like [hh, mm, ...] in your model
                st = task[6] if len(task) > 5 else None
                if isinstance(st, (list, tuple)) and len(st) >= 2:
                    hh, mm = int(st[0]), int(st[1])
                else:
                    return ''
            if hh == 0 and mm == 0:
                return ''
            return f"{hh:02d}:{mm:02d}"
        except Exception:
            return ''

    # calculate current week start/end based on offset
    today = datetime.now().date()
    mid = today + timedelta(weeks=displayed_week_offset)
    days_from_sunday = (mid.weekday() + 1) % 7
    week_start = mid - timedelta(days=days_from_sunday)
    week_end = week_start + timedelta(days=6)

    # Stable, non-duplicated "no tasks" messages for this week
    pick_msg = _weekly_message_picker(week_start, spoon_name_input or "")

    # draw navigation buttons and header
    draw_rounded_button(screen, previous_month_button, lighter_background, lighter_background, 0)
    draw_rounded_button(screen, next_month_button, lighter_background, lighter_background, 0)
    right_arrow = bigger_font.render(">", True, darker_background)
    left_arrow = pygame.transform.rotate(right_arrow, 180)
    screen.blit(left_arrow, (414, 2))
    screen.blit(right_arrow, (611, 5))

    # week-range header
    week_str = f"{calendar.month_abbr[week_start.month]} {week_start.day}-{calendar.month_abbr[week_end.month]} {week_end.day}"
    week_text = header_font.render(week_str, True, BLACK) #type: ignore
    screen.blit(week_text, week_text.get_rect(midtop=(522, 7)))

    # layout
    day_box_width, day_box_height = 105, 120
    margin = 0
    start_x, start_y = 160, 74

    # day-of-week labels
    days = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
    for i, d in enumerate(days):
        hdr_txt = font.render(d, True, BLACK) #type: ignore
        screen.blit(hdr_txt, (start_x + i*(day_box_width + margin) + 20, 72))

    # single row of date-boxes
    body_y = start_y + font.get_height() + 5
    for i in range(7):
        current = week_start + timedelta(days=i)
        x = start_x + i*(day_box_width + margin)
        y = body_y

        # choose colors
        if current < today:
            hdr_c, box_c = prev_hdr_col, prev_col
        elif current > today:
            hdr_c, box_c = next_hdr_col, next_col
        else:
            hdr_c, box_c = curr_hdr_col, curr_col

        # header & body rects
        pygame.draw.rect(screen, hdr_c, (x, y, day_box_width, day_box_height//4))
        pygame.draw.rect(screen, BLACK, (x, y, day_box_width, day_box_height//4), 1) #type: ignore
        body_rect_y = y + day_box_height//4
        pygame.draw.rect(screen, box_c, (x, body_rect_y, day_box_width, day_box_height*3))
        pygame.draw.rect(screen, BLACK, (x, body_rect_y, day_box_width, day_box_height*3), 1) #type: ignore

        # day number
        dn = font.render(str(current.day), True, BLACK) #type: ignore
        screen.blit(dn, (x + day_box_width - 20, y + 2))

        # streak indicator
        date_str = current.strftime("%Y-%m-%d")
        if any(start <= date_str <= end for start, end in streak_dates):
            s = font.render("S", True, BLACK) #type: ignore
            screen.blit(s, (x + day_box_width - 35, y + 2))

        # tasks grouped by folder
        line_height = smaller_font.get_height() - 2
        ty = body_rect_y + 2
        indent = 3
        folder_map = [
            (folder_one, homework_tasks_list),
            (folder_two, chores_tasks_list),
            (folder_three, work_tasks_list),
            (folder_four, misc_tasks_list),
            (folder_five, exams_tasks_list),
            (folder_six, projects_tasks_list),
        ]
        any_tasks_today = False
        for folder_label, lst in folder_map:
            # Filter tasks for current day - handle both dict and list formats
            day_tasks = []
            for t in lst:
                try:
                    # Try dictionary access first
                    due_date = t['due_date'] if isinstance(t, dict) else (t[5] if len(t) > 5 else None)
                    if isinstance(due_date, str):
                        if due_date[:10] == current.strftime("%Y-%m-%d"):
                            day_tasks.append(t)
                    elif hasattr(due_date, 'date'):  # Handle datetime objects
                        if due_date.date() == current:
                            day_tasks.append(t)
                except (TypeError, IndexError, KeyError):
                    continue

            if not day_tasks:
                continue
            any_tasks_today = True
                
            # ----- FOLDER HEADER AREA -----
            label_surf = smaller_font.render(f"{folder_label}:", True, BLACK) #type: ignore
            lw, lh = label_surf.get_width(), label_surf.get_height()
            cx = x + day_box_width // 2
            label_rect = label_surf.get_rect(midtop=(cx, ty))

            screen.blit(label_surf, label_rect)

            # Determine folder section bounding box
            section_top = label_rect.top
            section_left = x
            section_w = day_box_width
            section_h_start = ty       # start height marker

            # Centered underline
            underline_y = label_rect.bottom - 3
            pygame.draw.line(
                screen, BLACK, #type: ignore
                (cx - lw // 2, underline_y),
                (cx + lw // 2, underline_y),
                1
            )  # type: ignore
            ty = label_rect.bottom + 2

            # Create temporary folder-section rect
            folder_section_rect = pygame.Rect(
                section_left,
                section_top,
                section_w,
                0  # we will fill actual height after drawing tasks
            )

            # finalize folder section height
            folder_section_rect.height = ty - section_top

            # record clickable rect for logic
            week_folder_rects.append((folder_section_rect, lst, folder_label, current))

            mouse_x, mouse_y = pygame.mouse.get_pos()

            if folder_section_rect.collidepoint(mouse_x, mouse_y):
                icon = hubIcons["manage_task_icon"]
                scaled_icon = pygame.transform.scale(icon, (28, 28))
                scaled_icon.set_alpha(256)  # subtle overlay behind text
                # blit centered behind the folder label
                ix = label_rect.left - 27
                iy = label_rect.centery - 11
                screen.blit(scaled_icon, (ix, iy))
            
            # Render each task with line wrapping
            max_width = day_box_width - 15  # Allow padding on both sides
            for task in day_tasks:
                # Get task name + completion, then time
                try:
                    if isinstance(task, dict):
                        name = task['task_name']
                        is_complete = task['done'] >= task['spoons_needed']
                    else:
                        name = task[0]
                        is_complete = task[3] >= task[2]
                except (TypeError, IndexError, KeyError):
                    continue

                time_text = extract_start_time(task)

                # Layout: time pill (if present) right-aligned; name wraps to left area
                left_pad = indent
                right_pad = 4
                gap = 6

                pill_w = pill_h = 0
                if time_text:
                    pill_surf = smaller_font.render(time_text, True, BLACK)  # type: ignore
                    pill_w = pill_surf.get_width() + 8   # horizontal padding inside pill
                    pill_h = pill_surf.get_height() - 2  # slight tuck so it fits the row

                # Compute widths:
                first_line_w = day_box_width - left_pad - right_pad
                rest_lines_w = first_line_w

                if time_text:
                    # subtract the pill + gap ONLY for the first line
                    first_line_w = max(20, first_line_w - (pill_w + gap))

                # Wrap with two widths
                wrapped_lines = wrap_text_two_widths(name, smaller_font, first_line_w, rest_lines_w)
                if not wrapped_lines:
                    wrapped_lines = ['']

                # If a time pill exists, draw it on the FIRST line only
                if time_text:
                    pill_x = x + day_box_width - right_pad - pill_w
                    pill_y = ty  # align with first line
                    # simple rounded pill: rect + text
                    pygame.draw.rect(
                        screen, (255, 255, 255),  # pill bg; tweak if you want theme-aware
                        (pill_x, pill_y, pill_w, pill_h),
                        border_radius=6
                    )
                    pygame.draw.rect(
                        screen, BLACK,  #type: ignore
                        (pill_x, pill_y, pill_w, pill_h),
                        1, border_radius=6
                    )
                    pill_text_rect = pill_surf.get_rect(center=(pill_x + pill_w // 2, (pill_y + pill_h // 2) + 1))
                    screen.blit(pill_surf, pill_text_rect.topleft)

                # Draw wrapped name lines
                for li, line in enumerate(wrapped_lines):
                    if ty + line_height > body_rect_y + day_box_height * 3 - 5:
                        break

                    text_color = BLACK  # type: ignore
                    line_surf = smaller_font.render(line, True, text_color)  # type: ignore

                    # horizontally: keep left aligned in its area
                    screen.blit(line_surf, (x + left_pad, ty))

                    # strike through completed task lines
                    if is_complete:
                        lw = line_surf.get_width()
                        strike_y = ty + line_height // 2
                        pygame.draw.line(
                            screen, text_color,
                            (x + left_pad, strike_y - 2),
                            (x + left_pad + lw, strike_y + 2),
                            2
                        )

                    ty += line_height


        if not any_tasks_today:
            # Center a stable, unique weekly message in the body area — with wrapping
            msg = pick_msg(i)  # i is 0..6 for weekday column
            max_width = day_box_width - 14
            lines = wrap_text(msg, smaller_font, max_width)

            line_height = smaller_font.get_height() - 2
            total_h = len(lines) * line_height

            body_top = body_rect_y
            body_h = day_box_height * 3
            cx = x + day_box_width // 2

            # vertically center the block of wrapped lines
            start_y = body_top + (body_h - total_h) // 2

            for line in lines:
                surf = smaller_font.render(line, True, BLACK)  # type: ignore
                # horizontally center each line
                rect = surf.get_rect(midtop=(cx, start_y))
                screen.blit(surf, rect.topleft)
                start_y += line_height

def draw_month_mode(screen, font, bigger_font, smaller_font, darker_background, lighter_background,
                  homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list, exams_tasks_list, projects_tasks_list,
                  displayed_month, displayed_year, background_color,
                  calendar_previous_day_header_color, calendar_next_day_header_color, calendar_current_day_header_color,
                  calendar_previous_day_color, calendar_current_day_color, calendar_next_day_color,
                  streak_dates):
    global month_day_rects
    month_day_rects = []

    # Calendar grid settings
    day_box_width = 105
    margin = 0
    start_x = 160
    start_y = 97
    top_padding = 30
    days_of_week = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
    today = datetime.now().date()

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
    screen.blit(left_arrow, (414, 2))
    screen.blit(right_arrow, (611, 5))
    # Determine header string: full month if current year, else abbreviated + year
    if displayed_year == today.year:
        header_str = calendar.month_name[displayed_month]
    else:
        header_str = f"{calendar.month_abbr[displayed_month]} {displayed_year}"
    header_text = bigger_font.render(header_str, True, BLACK) #type: ignore
    screen.blit(header_text, header_text.get_rect(midtop=(522, 5)))

    # Day-of-week labels
    for i, day_name in enumerate(days_of_week):
        day_text = font.render(day_name, True, BLACK) #type: ignore
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
            disp_day = prev_num_days + day_offset
            slot_date = datetime(prev_year, prev_month, disp_day)
            hdr_col = blend(calendar_previous_day_header_color, background_color)
            box_col = blend(calendar_previous_day_color, background_color)
        elif day_offset > num_days:
            disp_day = day_offset - num_days
            slot_date = datetime(next_year, next_month, disp_day)
            hdr_col = blend(calendar_next_day_header_color, background_color)
            box_col = blend(calendar_next_day_color, background_color)
        else:
            disp_day = day_offset
            slot_date = datetime(displayed_year, displayed_month, disp_day)
            slot_day = slot_date.date()
            if slot_day < today:
                hdr_col = calendar_previous_day_header_color
                box_col = calendar_previous_day_color
            elif slot_day > today:
                hdr_col = calendar_next_day_header_color
                box_col = calendar_next_day_color
            else:
                hdr_col = calendar_current_day_header_color
                box_col = calendar_current_day_color

        # Save rectangle + actual date for click logic
        day_rect = pygame.Rect(x, y, day_box_width, day_box_height)
        month_day_rects.append((day_rect, slot_date.month, slot_date.day))

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
        screen.blit(day_text, (tx, y - 1))

        #draw the add task icon next to the day number on hover
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if x <= mouse_x <= x + day_box_width and y <= mouse_y <= y + day_box_height:
            #scale hubIcons{add_task_icon} to 16x16
            icon_size = 32
            scaled_icon = pygame.transform.scale(add_task_icon, (icon_size, icon_size))
            #make opacity 50%
            scaled_icon.set_alpha(128)
            screen.blit(scaled_icon, (x + 38, y + 23))

        # Draw streak indicator if needed
        date_str = slot_date.strftime("%Y-%m-%d")
        if any(start <= date_str <= end for start, end in streak_dates):
            s_text = smaller_font.render("S", True, BLACK) #type: ignore
            screen.blit(s_text, (x + day_box_width - 33, y + 1))

        # Task listing
        line_height = smaller_font.get_height() - 2
        text_y = slice_top + 2
        folders = [
            (homework_tasks_list, BLACK), #type: ignore
            (chores_tasks_list,   BLACK), #type: ignore
            (work_tasks_list,     BLACK), #type: ignore
            (misc_tasks_list,     BLACK), #type: ignore
            (exams_tasks_list,    BLACK), #type: ignore
            (projects_tasks_list, BLACK), #type: ignore
        ]

        # Gather all due tasks for this day (name, color, is_complete)
        all_due = []
        for lst, col in folders:
            for t in lst:
                try:
                    # Support both dict and tuple formats
                    due_dt = (t['due_date'] if isinstance(t, dict) else (t[5] if len(t) > 5 else None))
                    if isinstance(due_dt, datetime):
                        is_same_day = (due_dt.date() == slot_date.date())
                    else:
                        # if it's already a date/datetime aligned to midnight
                        is_same_day = (due_dt == slot_date)
                    if not is_same_day:
                        continue

                    if isinstance(t, dict):
                        name = t['task_name']
                        is_complete = t['done'] >= t['spoons_needed']
                    else:
                        name = t[0]
                        # tuple/list: done >= spoons_needed
                        is_complete = t[3] >= t[2]
                    all_due.append((name, col, is_complete))
                except Exception:
                    continue

        total = len(all_due)
        def _blit_task_line(name, col, is_complete, x_left, y_top):
            surf = smaller_font.render(name, True, col)  # type: ignore
            screen.blit(surf, (x_left, y_top))
            if is_complete:
                # strike through the rendered text (slight angle)
                lw = surf.get_width()
                mid_y = y_top + line_height // 2
                pygame.draw.line(screen, col, (x_left, mid_y - 2), (x_left + lw, mid_y + 2), 2)

        if total <= 3:
            for name, col, done_flag in all_due:
                _blit_task_line(name, col, done_flag, x + 5, text_y)
                text_y += line_height
        else:
            for name, col, done_flag in all_due[:2]:
                _blit_task_line(name, col, done_flag, x + 5, text_y)
                text_y += line_height
            more = smaller_font.render(f"{total-2} other tasks", True, BLACK)  # type: ignore
            screen.blit(more, (x + 5, text_y))

def draw_year_mode(
    screen, font, smaller_font, bigger_font,
    darker_background, lighter_background,
    displayed_year, background_color,
    homework_tasks_list=[], chores_tasks_list=[],
    work_tasks_list=[], misc_tasks_list=[],
    exams_tasks_list=[], projects_tasks_list=[]
):
    global year_month_rects
    year_month_rects = []  # store clickable zones for each month

    screen_w, screen_h = screen.get_size()
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
    screen.blit(left_arrow, (414, 2))
    screen.blit(right_arrow, (611, 5))

    cols, rows = 4, 3
    gap_x, gap_y = 10, 10
    cell_w = (region_w - gap_x*(cols-1)) / cols
    cell_h = (region_h - gap_y*(rows-1)) / rows

    # gather all tasks with due dates
    all_tasks = []
    for lst in (homework_tasks_list, chores_tasks_list, work_tasks_list,
                misc_tasks_list, exams_tasks_list, projects_tasks_list):
        all_tasks.extend(lst)

    # precompute all task dates for this year
    task_dates = set()
    for t in all_tasks:
        try:
            due = t['due_date'] if isinstance(t, dict) else (t[5] if len(t) > 5 else None)
            if isinstance(due, datetime):
                d = due.date()
            elif isinstance(due, str):
                d = datetime.fromisoformat(due).date()
            else:
                continue
            if d.year == displayed_year:
                task_dates.add(d)
        except Exception:
            continue

    for month in range(1, 13):
        col = (month - 1) % cols
        row = (month - 1) // cols
        x = region_x + col*(cell_w + gap_x)
        y = region_y + row*(cell_h + gap_y)
        rect = pygame.Rect(x, y, cell_w, cell_h)
        year_month_rects.append((rect, month))

        pygame.draw.rect(screen, lighter_background, rect)
        name_surf = font.render(calendar.month_name[month], True, BLACK) #type: ignore
        tx = x + (cell_w - name_surf.get_width()) / 2
        ty = y + 5
        screen.blit(name_surf, (tx, ty))
        ul_y = ty + name_surf.get_height() + 2
        pygame.draw.line(screen, BLACK, (tx, ul_y), (tx + name_surf.get_width(), ul_y), 2) #type: ignore

        first_wd, num_days = calendar.monthrange(displayed_year, month)
        first_wd = (first_wd + 1) % 7
        days_y0 = ul_y + 8
        grid_h = cell_h - (days_y0 - y) - 5
        weeks = 6
        day_h = grid_h / weeks
        day_w = cell_w / 7

        for day in range(1, num_days + 1):
            idx = first_wd + (day - 1)
            wd = idx % 7
            wk = idx // 7
            cx = x + wd * day_w
            cy = days_y0 + wk * day_h

            # render day number
            day_surf = smaller_font.render(str(day), True, BLACK)  # type: ignore
            dr = day_surf.get_rect(center=(cx + day_w / 2, cy + day_h / 2 - 2))
            screen.blit(day_surf, dr)

            # draw dot if a task exists
            day_date = datetime(displayed_year, month, day).date()
            if day_date in task_dates:
                dot_x = dr.centerx + 11 if day >= 10 else dr.centerx + 7
                dot_y = dr.top+ 3
                pygame.draw.circle(screen, LIGHT_GRAY, (int(dot_x), int(dot_y)), 2)  # type: ignore

def logic_calendar(event, day_range_index, displayed_week_offset, displayed_month, displayed_year, page, month, day, homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list, exams_tasks_list, projects_tasks_list):
    global calendar_mode, year_month_rects

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        # mode switching
        if day_mode_button.collidepoint(event.pos):
            calendar_mode = "Range"
        elif week_mode_button.collidepoint(event.pos):
            calendar_mode = "Week"
        elif month_mode_button.collidepoint(event.pos):
            calendar_mode = "Month"
        elif year_mode_button.collidepoint(event.pos):
            calendar_mode = "Year"

        # Range navigation
        if calendar_mode == "Range":
            if previous_month_button.collidepoint(event.pos):
                day_range_index = max(0, day_range_index - 1)
            elif next_month_button.collidepoint(event.pos):
                day_range_index += 1

        # Week navigation
        if calendar_mode == "Week":
            if previous_month_button.collidepoint(event.pos):
                displayed_week_offset -= 1
            elif next_month_button.collidepoint(event.pos):
                displayed_week_offset += 1

        # Month navigation
        if calendar_mode == "Month":
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

        # Year navigation and month clicks
        if calendar_mode == "Year":
            if previous_month_button.collidepoint(event.pos):
                displayed_year -= 1
            elif next_month_button.collidepoint(event.pos):
                displayed_year += 1
            else:
                # detect month click
                if "year_month_rects" in globals():
                    for rect, month in year_month_rects:
                        if rect.collidepoint(event.pos):
                            displayed_month = month
                            calendar_mode = "Month"
                            break

        # --- Click on a day in Month mode to go to input tasks page---
        if calendar_mode == "Month":
            if "month_day_rects" in globals():
                for rect, m, d in month_day_rects:
                    if rect.collidepoint(event.pos):
                        page = "input_tasks"
                        task_month = m
                        task_day   = d
                        return day_range_index, displayed_week_offset, displayed_month, displayed_year, page, task_month, task_day

        # --- Folder section click in Week Mode ---
        if calendar_mode == "Week":
            if "week_folder_rects" in globals():
                for rect, task_list_ref, folder_label, day_date in week_folder_rects:
                    if rect.collidepoint(event.pos):

                        # Map the actual list reference to the correct page
                        if task_list_ref is homework_tasks_list:
                            page = "complete_homework_tasks"
                        elif task_list_ref is chores_tasks_list:
                            page = "complete_chores_tasks"
                        elif task_list_ref is work_tasks_list:
                            page = "complete_work_tasks"
                        elif task_list_ref is misc_tasks_list:
                            page = "complete_misc_tasks"
                        elif task_list_ref is exams_tasks_list:
                            page = "complete_exams_tasks"
                        elif task_list_ref is projects_tasks_list:
                            page = "complete_projects_tasks"

    return day_range_index, displayed_week_offset, displayed_month, displayed_year, page, month, day
