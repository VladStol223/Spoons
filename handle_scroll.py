from config import *

import pygame

def handle_task_scroll(event, scroll_offset, total_content_height, scroll_multiplier=40):
    """
    Args:
      event: pygame.event.Event
      scroll_offset: current y-offset in pixels
      total_content_height: height of everything inside the scrolling region
      scroll_multiplier: how many pixels to move per wheel tick
    Returns:
      new scroll_offset (clamped).
    """
    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 4:     # scroll up
            scroll_offset -= scroll_multiplier
        elif event.button == 5:   # scroll down
            scroll_offset += scroll_multiplier

    max_scroll = max(0, total_content_height)
    scroll_offset = max(0, min(scroll_offset, max_scroll))
    return scroll_offset
