from config import *
from datetime import datetime
import pygame

def draw_manage_tasks_hub(
    screen,
    spoons,
    homework_tasks_list,
    chores_tasks_list,
    work_tasks_list,
    misc_tasks_list,
    exams_tasks_list,
    projects_tasks_list,
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
    # --- 1) Recompute "days left" and resort each list ---
    for lst in (homework_tasks_list, chores_tasks_list,
                work_tasks_list, misc_tasks_list,
                exams_tasks_list, projects_tasks_list):
        for task in lst:
            try:
                days_left = (task[4] - datetime.now()).days
                task[3] = days_left + 1
            except:
                pass
        # Sort: incomplete (done_count < cost) first, then by days_left
        lst.sort(key=lambda t: (t[2] >= t[1], t[3]))

    # --- 2) Summaries ---
    def summarize(lst):
        # Sum up how many spoons remain undone and how many tasks are not yet fully done
        total_spoons = sum((cost - done) for _, cost, done, *_ in lst if done < cost)
        total_tasks  = sum(1 for _, cost, done, *_ in lst if done < cost)
        return total_spoons, total_tasks

    hw_spoons, hw_tasks = summarize(homework_tasks_list)
    ch_spoons, ch_tasks = summarize(chores_tasks_list)
    wk_spoons, wk_tasks = summarize(work_tasks_list)
    mi_spoons, mi_tasks = summarize(misc_tasks_list)
    ex_spoons, ex_tasks = summarize(exams_tasks_list)
    pr_spoons, pr_tasks = summarize(projects_tasks_list)

    # --- 3) Layout & fonts ---
    folder_w, folder_h = 200, 150
    sx, sy = 60, 40
    start_x, start_y = 150, 145

    big_font   = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen.get_height() * 0.06))
    small_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen.get_height() * 0.04))

    full_img = pygame.transform.scale(manilla_folder_full, (folder_w, folder_h))

    folders = [
        (folder_one,   hw_spoons, hw_tasks),
        (folder_two,   ch_spoons, ch_tasks),
        (folder_three, wk_spoons, wk_tasks),
        (folder_four,  mi_spoons, mi_tasks),
        (folder_five,  ex_spoons, ex_tasks),
        (folder_six,   pr_spoons, pr_tasks),
    ]
    lists = [
        homework_tasks_list, chores_tasks_list,
        work_tasks_list, misc_tasks_list,
        exams_tasks_list, projects_tasks_list
    ]

    folder_rects = {}

    # --- 4) Draw the 2×3 grid ---
    for i, ((name, spoons_n, tasks_n), raw_list) in enumerate(zip(folders, lists)):
        col, row = i % 3, i // 3
        x = start_x + col * (folder_w + sx)
        y = start_y + row * (folder_h + sy)

        screen.blit(full_img, (x, y))

        # Folder title
        title_s = big_font.render(name, True, BLACK) #type: ignore
        screen.blit(title_s, (x + (folder_w - title_s.get_width())//2, y + 30))

        # Content
        if len(raw_list) == 0:
            msg = "No Tasks"
            surf = small_font.render(msg, True, BLACK) #type: ignore
            screen.blit(surf, (x + (folder_w - surf.get_width())//2,
                               y + (folder_h - surf.get_height())//2 + 5))

        elif tasks_n == 0:
            l1 = small_font.render("All Tasks", True, BLACK) #type: ignore
            l2 = small_font.render("Completed!", True, BLACK) #type: ignore
            total_h = l1.get_height() + l2.get_height()
            y1 = y + (folder_h - total_h)//2 + 10
            screen.blit(l1, (x + (folder_w - l1.get_width())//2, y1))
            screen.blit(l2, (x + (folder_w - l2.get_width())//2, y1 + l1.get_height() - 5))

        else:
            if spoons_n == 1:
                text1 = f"{spoons_n} Spoon For"
            else:
                text1 = f"{spoons_n} Spoons For"
            if tasks_n == 1:
                text2 = f"{tasks_n} Task Left"
            else:
                text2 = f"{tasks_n} Tasks Left"
            surf1 = small_font.render(text1, True, BLACK) #type: ignore
            surf2 = small_font.render(text2, True, BLACK) #type: ignore
            screen.blit(surf1, (x + (folder_w - surf1.get_width())//2, y + (folder_h - surf1.get_height())//2))
            screen.blit(surf2, (x + (folder_w - surf2.get_width())//2, y + surf1.get_height() + (folder_h - surf2.get_height())//2 - 5))

        # Clickable area
        rect = pygame.Rect(x, y, folder_w, folder_h)
        folder_rects[i+1] = rect

    return folder_rects


def logic_manage_tasks_hub(event, old_page, folder_rects):
    page = old_page
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
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
