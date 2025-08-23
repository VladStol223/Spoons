from config import *
import pygame

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