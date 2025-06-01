from config import *
from datetime import datetime
import pygame

# Global storage for clickable rects (if you still want globals; optional)
manage_folder_1 = manage_folder_2 = manage_folder_3 = None
manage_folder_4 = manage_folder_5 = manage_folder_6 = None

def draw_manage_tasks_hub(
    screen,
    spoons,
    homework_tasks_list,
    chores_tasks_list,
    work_tasks_list,
    misc_tasks_list,
    complete_tasks_hub_folder_color,
    icon_image,
    spoon_name_input,
    folder_one,
    folder_two,
    folder_three,
    folder_four,
    folder_five,
    folder_six
):
    # 1) Update "days left" and sort lists
    for lst in (homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list):
        for task in lst:
            try:
                days_left = (task[4] - datetime.now()).days
                task[3] = days_left + 1
            except:
                pass
    for lst in (homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list):
        lst.sort(key=lambda t: t[3])              # soonest first
        lst.sort(key=lambda t: t[2], reverse=True)  # undone ("❌") first

    # 2) Summarize each list
    def summarize(lst):
        total_spoons = sum(s for _, s, done, *_ in lst if done == "❌")
        total_tasks  = sum(1      for *_, done, _ in lst if done == "❌")
        return total_spoons, total_tasks

    hw_spoons, hw_tasks = summarize(homework_tasks_list)
    ch_spoons, ch_tasks = summarize(chores_tasks_list)
    wk_spoons, wk_tasks = summarize(work_tasks_list)
    mi_spoons, mi_tasks = summarize(misc_tasks_list)
    f5_spoons, f5_tasks = 0, 0
    f6_spoons, f6_tasks = 0, 0

    # 3) Grid layout config
    folder_width   = 200
    folder_height  = 150
    spacing_x      = 60
    spacing_y      = 40
    start_x        = 150
    start_y        = 145

    # 4) Font for text
    font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen.get_height() * 0.06))
    small_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen.get_height() * 0.04))

    # 5) Scale the folder image once for all
    full_img = pygame.transform.scale(manilla_folder_full, (folder_width, folder_height))

    # 6) Folder definitions
    folders = [
        ("folder_one",   folder_one,   hw_spoons,  hw_tasks),
        ("folder_two",   folder_two,   ch_spoons,  ch_tasks),
        ("folder_three", folder_three, wk_spoons,  wk_tasks),
        ("folder_four",  folder_four,  mi_spoons,  mi_tasks),
        ("folder_five",  folder_five,  f5_spoons,  f5_tasks),
        ("folder_six",   folder_six,   f6_spoons,  f6_tasks),
    ]

    # 7) Prepare a dict to store rects by 1-based index
    folder_rects = {}

    # 8) Draw 2×3 grid using the folder image
    for i, (key, name, spoons_n, tasks_n) in enumerate(folders):
        col = i % 3
        row = i // 3
        x = start_x + col * (folder_width  + spacing_x)
        y = start_y + row * (folder_height + spacing_y)

        # Blit the full folder image (including tab)
        screen.blit(full_img, (x, y))

        # Folder name centered in the tab area
        name_surf = font.render(name, True, BLACK)  # type: ignore
        name_x = x + (folder_width - name_surf.get_width()) // 2
        name_y = y + (name_surf.get_height() // 2) + 10
        screen.blit(name_surf, (name_x, name_y))

        # Summary text centered in the folder body
        summary = f"{spoons_n} spoons for {tasks_n} tasks"
        summ_surf = small_font.render(summary, True, BLACK)  # type: ignore
        summ_x = x + (folder_width - summ_surf.get_width()) // 2
        summ_y = y + (folder_height - summ_surf.get_height()) // 2
        screen.blit(summ_surf, (summ_x, summ_y))

        # Clickable rect covers the entire folder image
        click_rect = pygame.Rect(x, y, folder_width, folder_height)
        # Store in our dict as 1-based index
        folder_rects[i + 1] = click_rect

        # (Optional) Still keep the globals if other code depends on them
        globals()[f"manage_{key}"] = click_rect

    # 9) Return the dict of rects
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
            5: "complete_exams_tasks",
            6: "complete_projects_tasks",
        }
        for idx, rect in folder_rects.items():
            if rect.collidepoint(event.pos):
                page = page_map[idx]
                break
    return page
