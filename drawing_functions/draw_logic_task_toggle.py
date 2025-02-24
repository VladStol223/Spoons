from config import *
import pygame
from drawing_functions.draw_rounded_button import draw_rounded_button

def draw_task_toggle(screen, page):
    """ Draws the toggle buttons and highlights the active one based on the page. """

    TASK_PAGES = {
    "complete": [
        "complete_homework_tasks",
        "complete_chores_tasks",
        "complete_work_tasks",
        "complete_misc_tasks"
    ],
    "edit": [
        "edit_homework_tasks",
        "edit_chores_tasks",
        "edit_work_tasks",
        "edit_misc_tasks"
    ],
    "remove": [
        "remove_homework_tasks",
        "remove_chores_tasks",
        "remove_work_tasks",
        "remove_misc_tasks"
    ]
}


    draw_rounded_button(screen, task_toggle_cover, LIGHT_GRAY, BLACK, 3, 2)# type: ignore

    draw_rounded_button(screen, complete_tasks_toggle, GREEN if page in TASK_PAGES["complete"] else LIGHT_GRAY, BLACK, 3, 1)# type: ignore

    draw_rounded_button(screen, edit_tasks_toggle, YELLOW if page in TASK_PAGES["edit"] else LIGHT_GRAY, BLACK, 3, 1)# type: ignore

    draw_rounded_button(screen, remove_tasks_toggle, RED if page in TASK_PAGES["remove"] else LIGHT_GRAY, BLACK, 3, 1)# type: ignore


    screen.blit(complete_toggle_icon, (complete_tasks_toggle.x + 5, complete_tasks_toggle.y + 5))
    screen.blit(edit_toggle_icon, (edit_tasks_toggle.x + 5, edit_tasks_toggle.y + 5))
    screen.blit(remove_toggle_icon, (remove_tasks_toggle.x + 5, remove_tasks_toggle.y + 5))



def logic_task_toggle(event, page):
    """ Handles logic for switching task modes when toggles are clicked. """

    if event.type == pygame.MOUSEBUTTONDOWN:
        mouse_pos = pygame.mouse.get_pos()

        # Extract current folder from the page name (e.g., "complete_homework_tasks" → "homework")
        for folder in ["homework", "chores", "work", "misc"]:
            if folder in page:
                current_folder = folder
                break
        else:
            return page  # If no folder is found, return the same page

        # Determine the new mode based on the clicked toggle button
        if complete_tasks_toggle.collidepoint(mouse_pos):
            return f"complete_{current_folder}_tasks"
        elif edit_tasks_toggle.collidepoint(mouse_pos):
            return f"edit_{current_folder}_tasks"
        elif remove_tasks_toggle.collidepoint(mouse_pos):
            return f"remove_{current_folder}_tasks"

    return page  # Return the same page if no button was clicked