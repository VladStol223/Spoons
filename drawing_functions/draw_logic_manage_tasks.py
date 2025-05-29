from config import *
from datetime import datetime

import pygame

def draw_manage_tasks_hub(screen, spoons,
                          homework_tasks_list, chores_tasks_list,
                          work_tasks_list, misc_tasks_list,
                          complete_tasks_hub_folder_color,
                          icon_image, spoon_name_input,
                          folder_one, folder_two, folder_three,
                          folder_four, folder_five, folder_six):

    global hub_buttons_showing
    folder_rects = {}
    # 1) Calculate days-left and sort (unchanged)
    for lst in (homework_tasks_list, chores_tasks_list,
                work_tasks_list,   misc_tasks_list):
        for task in lst:
            try:
                days_left = (task[4] - datetime.now()).days
                task[3] = days_left + 1
            except:
                pass
    for lst in (homework_tasks_list, chores_tasks_list,
                work_tasks_list,   misc_tasks_list):
        lst.sort(key=lambda t: t[3])            # soonest first
        lst.sort(key=lambda t: t[2], reverse=True)  # undone ("❌") first

    # 3) Compute summary numbers
    def summarize(lst):
        total_spoons = sum(s for _, s, done, *_ in lst if done == "❌")
        total_tasks  = sum(1      for *_, done, _ in lst if done == "❌")
        return total_spoons, total_tasks

    hw_spoons, hw_tasks = summarize(homework_tasks_list)
    ch_spoons, ch_tasks = summarize(chores_tasks_list)
    wk_spoons, wk_tasks = summarize(work_tasks_list)
    mi_spoons, mi_tasks = summarize(misc_tasks_list)
    # for folder five & six we’ll default to zero
    f5_spoons, f5_tasks = 0, 0
    f6_spoons, f6_tasks = 0, 0

    # 4) GRID LAYOUT CONFIG — tweak these!
    folder_width   = 250
    folder_height  = 160
    tab_width      = 130
    tab_height     = 26
    tab_indent     = 15
    border_width   = 2

    spacing_x      = 30   # horizontal gutter
    spacing_y      = 56   # vertical gutter

    start_x        = 160
    start_y        = 120

    font           = pygame.font.SysFont("arial", 18, bold=True)
    BLACK          = (0,0,0)

    # 5) Build per-folder data
    folders = [
        # key name unused here, but kept for consistency
        ("folder_one",   folder_one,   hw_spoons,  hw_tasks),
        ("folder_two",   folder_two,   ch_spoons,  ch_tasks),
        ("folder_three", folder_three, wk_spoons,  wk_tasks),
        ("folder_four",  folder_four,  mi_spoons,  mi_tasks),
        ("folder_five",  folder_five,  f5_spoons,  f5_tasks),
        ("folder_six",   folder_six,   f6_spoons,  f6_tasks),
    ]

    # 6) Draw the 2×3 grid of folders
    for i, (_, name, spoons_n, tasks_n) in enumerate(folders):
        col = i % 3
        row = i // 3
        x = start_x + col * (folder_width  + spacing_x)
        y = start_y + row * (folder_height + spacing_y)

        # choose color based on whether there's any tasks
        has_tasks = tasks_n > 0
        color     = complete_tasks_hub_folder_color if has_tasks else LIGHT_GRAY #type: ignore

        # --- Tab polygon ---
        tab_pts = [
            (x,            y),
            (x + tab_indent,        y - tab_height),
            (x + tab_width - tab_indent, y - tab_height),
            (x + tab_width,        y)
        ]
        pygame.draw.polygon(screen, color, tab_pts)
        pygame.draw.polygon(screen, BLACK, tab_pts, width=border_width)

        # --- Folder body ---
        body_rect = pygame.Rect(x, y, folder_width, folder_height)
        pygame.draw.rect(screen, color, body_rect)
        pygame.draw.rect(screen, BLACK, body_rect, width=border_width)

        # --- Folder name in tab ---
        txt = font.render(name, True, BLACK)
        txt_r = txt.get_rect(center=(x + tab_width//2, y - tab_height//2))
        screen.blit(txt, txt_r)

        # --- Summary text on folder face ---
        summary = f"{spoons_n} spoons for {tasks_n} tasks"
        summ_surf = font.render(summary, True, BLACK)
        summ_r    = summ_surf.get_rect(center=body_rect.center)
        screen.blit(summ_surf, summ_r)

        # --- Expose clickable rects for your main.py ---
        click_rect = pygame.Rect(x,
                                 y - tab_height,
                                 folder_width,
                                 folder_height + tab_height)
        # assign into globals manage_folder_one…manage_folder_six
        globals()[f"manage_folder_{i+1}"] = click_rect

        click_rect = pygame.Rect(x,y - tab_height,folder_width,folder_height + tab_height)
        folder_rects[i+1] = click_rect
    return folder_rects

def logic_manage_tasks_hub(event, old_page, folder_rects):
    page = old_page
    if event.type == pygame.MOUSEBUTTONDOWN:
        # map folder index → page name
        page_map = {
            1: "complete_homework_tasks",
            2: "complete_chores_tasks",
            3: "complete_work_tasks",
            4: "complete_misc_tasks",
            5: "complete_exams_tasks",    # ← only if you handle these later!
            6: "complete_projects_tasks",
        }
        for idx, rect in folder_rects.items():
            if rect.collidepoint(event.pos):
                page = page_map[idx]
                break
    return page
