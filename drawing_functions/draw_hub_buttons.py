from config import *
import pygame
from datetime import datetime

button_widths = {}  # no longer used, but left to avoid breaking interfaces

# fonts: small for date, large for static labels
_date_font  = pygame.font.SysFont("fonts/Stardew_Valley.ttf", 24, bold=True)
_label_font = pygame.font.SysFont("fonts/Stardew_Valley.ttf", 30, bold=False)

def draw_hub_buttons(
    screen,
    page,
    tool_tips,
    background_color,
    add_spoons_color,
    add_tasks_color,
    manage_tasks_color,
    study_color,
    calendar_color,
    store_color,
    stats_color,
    button_widths_dict,
    hub_closing,
    delta_time
):
    global hub_buttons_showing, button_widths
    hub_buttons_showing = True

    # icon definitions
    icon_buttons = [
        ("calendar",     loaded_images.get("calendar_icon"),     "Calendar"),
        ("input_spoons", loaded_images.get("add_spoons_icon"),   "Add Spoons"),
        ("input_tasks",  loaded_images.get("add_task_icon"),     "Add Tasks"),
        ("manage_tasks", loaded_images.get("manage_task_icon"),  "Manage Tasks"),
        ("study",        loaded_images.get("study_icon"),        "Study"),
        ("store",        loaded_images.get("store_icon"),        "Store"),
        ("stats",        loaded_images.get("settings_icon"),     "Statistics")
    ]

    # sizes and spacing
    icon_size  = 56
    cal_size   = int(icon_size * 1.5)
    y_spacing  = 10
    total_h    = cal_size + y_spacing + (len(icon_buttons)-1)*(icon_size + y_spacing)
    start_y    = (screen.get_height() - total_h) // 2
    x_base     = 23

    button_rects = {}
    today = datetime.now().strftime("%m/%d")

    # --- Calendar icon + date ---
    cal_x = x_base - 13
    cal_y = start_y + 5
    cal_rect = pygame.Rect(cal_x, cal_y, cal_size, cal_size)
    img = icon_buttons[0][1]
    if img:
        screen.blit(pygame.transform.scale(img, (cal_size, cal_size)), cal_rect)
    draw_centered_text(screen, _date_font, today, cal_rect, BLACK) #type: ignore
    button_rects["calendar"] = cal_rect

    # --- Other icons ---
    for idx, (page_key, image, label) in enumerate(icon_buttons[1:], start=1):
        y_pos = start_y + cal_size + y_spacing + (idx-1)*(icon_size + y_spacing)
        rect = pygame.Rect(x_base, y_pos, icon_size, icon_size)
        icon_rect = draw_icon_button(
            screen,
            rect,
            image,
            label,
            _label_font,
            selected = (page_key == page),
            bg_color = background_color
        )
        button_rects[page_key] = icon_rect

    return button_rects


def draw_icon_button(
    screen,
    rect,
    icon_img,
    label,
    font,
    selected   = False,
    bg_color   = (30,30,30)
):
    # draw circular gradient glow behind icon if selected
    if selected and icon_img:
        glow_scale = 1.3
        gw = int(rect.width  * glow_scale)
        gh = int(rect.height * glow_scale)

        glow_surf = pygame.Surface((gw, gh), pygame.SRCALPHA)
        glow_color = tuple(min(255, c + 60) for c in bg_color)
        center = (gw // 2, gh // 2)
        max_radius = gw // 2
        max_alpha  = 255

        # fade out toward edges
        for r in range(max_radius, 0, -1):
            frac  = (1 - (r / max_radius))**2
            alpha = int(max_alpha * frac)
            pygame.draw.circle(glow_surf, glow_color + (alpha,), center, r)

        gx = rect.x - (gw - rect.width)//2
        gy = rect.y - (gh - rect.height)//2
        screen.blit(glow_surf, (gx, gy))

    # draw the main icon (always at rect.x, rect.y)
    if icon_img:
        icon_surf = pygame.transform.scale(icon_img, (rect.width, rect.height))
        screen.blit(icon_surf, (rect.x, rect.y))

    # no label reveal, so return the icon rect only
    return rect


def draw_centered_text(screen, font, text, rect, color):
    surf = font.render(text, True, color)
    w, h = surf.get_size()
    x = rect.x + (rect.width - w)//2
    y = rect.y + 12 + (rect.height - h)//2
    screen.blit(surf, (x, y))
