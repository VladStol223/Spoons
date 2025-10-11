from config import *
import pygame
from datetime import datetime

button_widths = {}  # no longer used, but left to avoid breaking interfaces

# fonts: small for date, large for static labels
_label_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen_height * 0.06))
calendar_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen_height * 0.05))

calendar_icon     = hubIcons['calendar_icon']
add_spoons_icon   = hubIcons['add_spoons_icon']
add_task_icon     = hubIcons['add_task_icon']
manage_task_icon  = hubIcons['manage_task_icon']
inventory_icon    = hubIcons['inventory_icon']
shop_icon         = hubIcons['shop_icon']
settings_icon     = hubIcons['settings_icon']

# icon definitions
icon_buttons = [
    ("calendar",     calendar_icon,     "Calendar"),
    ("input_spoons", add_spoons_icon,   "Add Spoons"),
    ("input_tasks",  add_task_icon,     "Add Tasks"),
    ("manage_tasks", manage_task_icon,  "Manage Tasks"),
    ("inventory",    inventory_icon,    "Inventory"),
    ("shop",         shop_icon,         "Shop"),
    ("settings",        settings_icon,     "Settings"),
]

def draw_hub_buttons(
    screen,
    page,
    tool_tips,
    background_color,
    button_widths_dict,
    hub_closing,
    delta_time,
    is_maximized,
    scale_factor
):
    global hub_buttons_showing, button_widths
    hub_buttons_showing = True



    # sizes and spacing
    icon_size  = 112 if is_maximized else 56
    cal_size   = int(icon_size * 1.5)
    y_spacing  = 20 if is_maximized else 10
    total_h    = cal_size + y_spacing + (len(icon_buttons)-1)*(icon_size + y_spacing)
    start_y    = (screen.get_height() - total_h) // 2
    x_base     = 50 if is_maximized else 25

    button_rects = {}
    today = datetime.now().strftime("%m/%d")

    # --- Calendar icon + date ---
    cal_x = x_base - 25 if is_maximized else x_base - 13
    cal_y = start_y + 5
    cal_rect = pygame.Rect(cal_x, cal_y, cal_size, cal_size)
    img = icon_buttons[0][1]
    if img:
        screen.blit(pygame.transform.scale(img, (cal_size, cal_size)), cal_rect)
    draw_centered_text(screen, today, cal_rect, BLACK) #type: ignore
    button_rects["calendar"] = cal_rect

    # --- Other icons ---
    for idx, (page_key, image, label) in enumerate(icon_buttons[1:], start=1):
        y_pos = start_y + cal_size + y_spacing + (idx-1)*(icon_size + y_spacing)
        rect = pygame.Rect(x_base, y_pos, icon_size, icon_size)

        # treat any "complete_..." page as selecting manage_tasks
        is_manage_glow = (page_key == "manage_tasks"
                          and (page == "manage_tasks" or page.startswith("complete_")))

        icon_rect = draw_icon_button(
            screen,
            rect,
            image,
            label,
            _label_font,
            selected = (page_key == page) or is_manage_glow,
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
        max_radius = gw // 2 + 15
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


def draw_centered_text(screen,  text, rect, color):
    surf = calendar_font.render(text, True, color)
    w, h = surf.get_size()
    x = rect.x + (rect.width - w)//2
    y = rect.y + 12 + (rect.height - h)//2
    screen.blit(surf, (x, y))
