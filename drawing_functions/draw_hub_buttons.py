from config import *
import pygame
from datetime import datetime

button_widths = {}

# fonts: small for date, large for hover labels
_date_font  = pygame.font.SysFont("arial", 24, bold=True)
_label_font = pygame.font.SysFont("Impact", 30, bold=False)

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
    button_widths = button_widths_dict

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
    icon_size  = 64
    cal_size   = int(icon_size * 1.5)
    y_spacing  = 10
    total_h    = cal_size + y_spacing + (len(icon_buttons)-1)*(icon_size + y_spacing)
    start_y    = (screen.get_height() - total_h) // 2
    x_base     = 10

    button_rects = {}
    today = datetime.now().strftime("%m/%d")

    # --- Calendar icon + date ---
    cal_x = x_base - 10
    cal_y = start_y + 10
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
            button_widths,
            delta_time,
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
    button_widths,
    delta_time,
    padding    = 10,
    speed      = 8,
    selected   = False,
    bg_color   = (30,30,30)
):
    # key for this button
    rect_key = (rect.x, rect.y)

    # render label text once
    text_surface = font.render(label, True, BLACK) #type: ignore
    label_w, label_h = text_surface.get_size()

    # sliding offset logic
    max_offset = label_w + padding + 10
    if rect_key not in button_widths:
        button_widths[rect_key] = 0
    hover_rect = pygame.Rect(
        rect.x, rect.y,
        int(button_widths[rect_key]) + rect.width,
        rect.height
    )
    is_hover = hover_rect.collidepoint(pygame.mouse.get_pos())
    target = max_offset if is_hover else 0
    button_widths[rect_key] = lerp(button_widths[rect_key], target, speed, delta_time)
    x_offset = int(button_widths[rect_key])

      # draw circular gradient glow behind icon if selected
    if selected and icon_img:
        glow_scale = 1.3
        gw = int(rect.width  * glow_scale)
        gh = int(rect.height * glow_scale)

        glow_surf = pygame.Surface((gw, gh), pygame.SRCALPHA)
        glow_color = tuple(min(255, c + 60) for c in bg_color)
        center = (gw // 2, gh // 2)
        max_radius = gw // 2
        max_alpha  = 255  # peak at center

        # draw from outermost to innermost
        for r in range(max_radius, 0, -1):
            # invert alpha so center (r small) is strong, edge (r large) is weak
            alpha = int(max_alpha * (1 - (r / max_radius)))
            pygame.draw.circle(glow_surf, glow_color + (alpha,), center, r)

        gx = rect.x + x_offset - (gw - rect.width)//2
        gy = rect.y       - (gh - rect.height)//2
        screen.blit(glow_surf, (gx, gy))



    # draw the main icon
    if icon_img:
        icon_surf = pygame.transform.scale(icon_img, (rect.width, rect.height))
        screen.blit(icon_surf, (rect.x + x_offset, rect.y))

    # reveal label text as it slides
    revealed = max(0, x_offset - padding)
    if revealed > 0:
        clip_surf = pygame.Surface((revealed, label_h), pygame.SRCALPHA)
        clip_surf.blit(text_surface, (0,0), (0,0,revealed,label_h))
        screen.blit(
            clip_surf,
            (rect.x + padding, rect.y + (rect.height - label_h)//2)
        )

    return pygame.Rect(rect.x, rect.y, x_offset + rect.width, rect.height)


def draw_centered_text(screen, font, text, rect, color):
    surf = font.render(text, True, color)
    w, h = surf.get_size()
    x = rect.x + (rect.width - w)//2
    y = rect.y + 12 + (rect.height - h)//2
    screen.blit(surf, (x, y))


def lerp(a, b, t, delta_time):
    return a + (b - a) * min(t * delta_time, 1)


def reset_button_widths():
    global button_widths
    button_widths.clear()
