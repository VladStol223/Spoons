import pygame
from config import *
from drawing_functions.draw_rounded_button import draw_rounded_button
from drawing_functions.draw_input_box import draw_input_box

# ---------------------------------------------------------------------
# SOCIAL (FRIENDS) TAB
# ---------------------------------------------------------------------

def draw_social(screen, tool_tips, spoon_name_input, icon_image, input_active, hub_background_color,
                folder_one, folder_two, folder_three, folder_four, folder_five, folder_six):
    sw, sh = screen.get_size()
    mouse_pos = pygame.mouse.get_pos()
    font_title = pygame.font.Font("fonts/Stardew_Valley.ttf", int(sh * 0.07))
    font_small = pygame.font.Font("fonts/Stardew_Valley.ttf", int(sh * 0.045))
    font_tiny = pygame.font.Font("fonts/Stardew_Valley.ttf", int(sh * 0.035))

    # --- Header Title ---
    title = font_title.render("Friends", True, (0, 0, 0))
    screen.blit(title, (sw * 0.15, sh * 0.25))

    # --- Search Bar ---
    search_rect = pygame.Rect(sw * 0.15, sh * 0.33, sw * 0.6, sh * 0.07)
    draw_input_box(screen, search_rect, False, "", (220, 220, 220), (150, 150, 150), True, hub_background_color, "light", 12, 0.045)
    search_txt = font_small.render("Search friends...", True, (100, 100, 100))
    screen.blit(search_txt, (search_rect.x + 15, search_rect.y + (search_rect.height - search_txt.get_height()) // 2))

    # --- Add Friend (+) and Settings (⚙) Icons ---
    add_friend_rect = pygame.Rect(sw - sh * 0.13, sh * 0.27, sh * 0.06, sh * 0.06)
    settings_rect = pygame.Rect(sw - sh * 0.13, sh * 0.35, sh * 0.06, sh * 0.06)
    pygame.draw.circle(screen, (90, 160, 90), add_friend_rect.center, add_friend_rect.width // 2)
    pygame.draw.circle(screen, (100, 100, 100), settings_rect.center, settings_rect.width // 2)
    plus = font_small.render("+", True, (255, 255, 255))
    gear = font_small.render("-", True, (255, 255, 255))
    screen.blit(plus, (add_friend_rect.centerx - plus.get_width() // 2, add_friend_rect.centery - plus.get_height() // 2))
    screen.blit(gear, (settings_rect.centerx - gear.get_width() // 2, settings_rect.centery - gear.get_height() // 2))

    # --- Example Friend List ---
    friend_entries = [
        {"name": "@jason", "privacy": "Semi-Private"},
        {"name": "@olivia", "privacy": "Private"},
        {"name": "@dylan", "privacy": "Public"},
    ]

    start_y = sh * 0.43
    row_h = sh * 0.12
    pad_x = sw * 0.13
    box_w = sw * 0.75

    for i, friend in enumerate(friend_entries):
        y = start_y + i * (row_h + 10)
        row_rect = pygame.Rect(pad_x, y, box_w, row_h)
        draw_rounded_button(screen, row_rect, (240, 240, 240), (50, 50, 50), 10, 4)

        # Avatar placeholder
        avatar_rect = pygame.Rect(row_rect.x + 15, row_rect.y + 10, int(row_h * 0.65), int(row_h * 0.65))
        pygame.draw.ellipse(screen, (180, 180, 200), avatar_rect)

        # Name & privacy
        name_text = font_small.render(friend["name"], True, (0, 0, 0))
        privacy_text = font_tiny.render(friend["privacy"], True, (80, 80, 80))
        screen.blit(name_text, (avatar_rect.right + 15, row_rect.y + 12))
        screen.blit(privacy_text, (avatar_rect.right + 15, row_rect.y + name_text.get_height() + 8))

        # Buttons (View / Add Task)
        btn_w, btn_h = sw * 0.13, row_h * 0.5
        gap = sw * 0.015
        view_rect = pygame.Rect(row_rect.right - (btn_w * 2 + gap + 20), row_rect.centery - btn_h / 2, btn_w, btn_h)
        add_rect = pygame.Rect(row_rect.right - (btn_w + 20), row_rect.centery - btn_h / 2, btn_w, btn_h)
        draw_rounded_button(screen, view_rect, (100, 140, 200), (40, 40, 40), 8, 3)
        draw_rounded_button(screen, add_rect, (120, 180, 100), (40, 40, 40), 8, 3)

        view_txt = font_tiny.render("View", True, (255, 255, 255))
        add_txt = font_tiny.render("Add Task", True, (255, 255, 255))
        screen.blit(view_txt, (view_rect.centerx - view_txt.get_width() / 2, view_rect.centery - view_txt.get_height() / 2))
        screen.blit(add_txt, (add_rect.centerx - add_txt.get_width() / 2, add_rect.centery - add_txt.get_height() / 2))

def logic_social(event, tool_tips, spoon_name_input, input_active, current_theme, icon_image,
                 folder_one, folder_two, folder_three, folder_four, folder_five, folder_six):
    return tool_tips, spoon_name_input, input_active, current_theme, icon_image, folder_one, folder_two, folder_three, folder_four, folder_five, folder_six
