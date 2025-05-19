from config import *
import pygame

button_widths = {}

def draw_hub_buttons(screen, page, tool_tips, background_color, add_spoons_color, add_tasks_color,
                     manage_tasks_color, study_color, calendar_color, store_color,
                     stats_color, button_widths, hub_closing, delta_time):
    global hub_buttons_showing
    hub_buttons_showing = True

    icon_buttons = [
        ("input_spoons", loaded_images.get("add_spoons_icon"), "Add Spoons"),
        ("input_tasks", loaded_images.get("add_task_icon"), "Add Tasks"),
        ("manage_tasks", loaded_images.get("manage_task_icon"), "Manage Tasks"),
        ("study", loaded_images.get("study_icon"), "Study"),
        ("calendar", loaded_images.get("calendar_icon"), "Calendar"),
        ("store", loaded_images.get("store_icon"), "Store"),
        ("stats", loaded_images.get("settings_icon"), "Statistics")
    ]

    y_spacing = 10
    start_y = (screen.get_height() - (64 * len(icon_buttons) + y_spacing * (len(icon_buttons) - 1))) // 2
    x_base = 10

    button_rects = {}

    for i, (page_key, image, label) in enumerate(icon_buttons):
        y_pos = start_y + i * (64 + y_spacing)
        rect = pygame.Rect(x_base, y_pos, 64, 64)
        # Draw and get updated clickable rect (icon_rect)
        icon_rect = draw_icon_button(screen, rect, image, label, font, button_widths, delta_time)
        button_rects[page_key] = icon_rect

    return button_rects

def draw_icon_button(screen, rect, icon_img, label, font, button_widths, delta_time, padding=10, speed=8):
    rect_key = (rect.x, rect.y)

    # Render label once
    text_surface = font.render(label, True, BLACK)#type: ignore
    label_width = text_surface.get_width()
    label_height = text_surface.get_height()
    max_offset = label_width + padding + 10

    # Initialize offset if needed
    if rect_key not in button_widths:
        button_widths[rect_key] = 0

    x_offset = int(button_widths[rect_key])

    # Hover detection: only over current visible area (label + icon width so far)
    hover_rect = pygame.Rect(rect.x, rect.y, x_offset + 64, 64)
    is_hover = hover_rect.collidepoint(pygame.mouse.get_pos())

    # Animate icon
    target_offset = max_offset if is_hover else 0
    button_widths[rect_key] = lerp(button_widths[rect_key], target_offset, speed, delta_time)
    x_offset = int(button_widths[rect_key])  # Recalculate after lerp

    # Draw icon at offset
    icon_x = rect.x + x_offset
    icon_y = rect.y
    if icon_img:
        screen.blit(pygame.transform.scale(icon_img, (64, 64)), (icon_x, icon_y))

    # Draw cropped label to the left of the icon
    revealed_width = max(0, x_offset - padding)
    text_x = rect.x + padding
    text_y = rect.y + (64 - label_height) // 2

    if revealed_width > 0:
        revealed_text = pygame.Surface((revealed_width, label_height), pygame.SRCALPHA)
        revealed_text.blit(text_surface, (0, 0), area=pygame.Rect(0, 0, revealed_width, label_height))
        screen.blit(revealed_text, (text_x, text_y))

    # Clickable area matches real-time extent of the label + icon
    click_width = x_offset + 64
    icon_rect = pygame.Rect(rect.x, rect.y, click_width, 64)

    return icon_rect

def draw_centered_text(screen, font, text, rect, color):
    text_surface = font.render(text, True, color)
    text_width, text_height = text_surface.get_size()
    text_x = rect.x + (rect.width - text_width) // 2
    text_y = rect.y + (rect.height - text_height) // 2
    screen.blit(text_surface, (text_x, text_y))

def lerp(a, b, t, delta_time):
    return a + (b - a) * min(t * delta_time, 1)

def is_hovered(rect):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    return rect.collidepoint(mouse_x, mouse_y)

def reset_button_widths():
    global button_widths
    button_widths.clear()
