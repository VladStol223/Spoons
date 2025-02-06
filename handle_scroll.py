from config import *

import pygame

"""
Handles the scroll event for task pages.

Args:
    event (pygame.event.Event): The current Pygame event.
    scroll_offset (int): The current scroll offset.
    scroll_limit (int): The maximum scroll limit.
    scroll_multiplier (int): How many items to scroll per wheel action.

Returns:
    int: The updated scroll offset.
"""

def handle_task_scroll(event, scroll_offset, scroll_limit, scroll_multiplier=1):
    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 4:  # Scroll up
            scroll_offset = max(scroll_offset - (1 * scroll_multiplier), 0)
        elif event.button == 5:  # Scroll down
            scroll_offset = min(scroll_offset + (1 * scroll_multiplier), scroll_limit)

    return scroll_offset

def handle_daily_schedule_scroll():
    pass