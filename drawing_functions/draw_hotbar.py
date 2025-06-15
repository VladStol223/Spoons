import pygame
from datetime import datetime
from config import *
import math

# pre-create font so you’re not reloading every frame
font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen_height * 0.06))
coin_scale = 1.8
xp_scale = 1.4

def get_day_alpha():
    """
    Returns an alpha 0–255 that is 0 at midnight (0:00), 255 at noon (12:00),
    and falls off linearly before/after.
    """
    now = datetime.now()
    # turn hour+minute into a float 0.0–24.0
    h = now.hour + now.minute / 60.0
    # compute “distance” from noon
    dist = abs(h - 12.0)
    # normalized brightness: 1.0 at noon, 0.0 at midnight
    brightness = max(0.0, 1.0 - dist / 12.0)
    return int(brightness * 255)

def get_day_color():
    """
    Returns an (r,g,b) tuple that is darkest at midnight (0:00),
    lightest at noon (12:00), and falls off linearly in between.
    """
    now = datetime.now()
    # convert current time to a float 0.0–24.0
    h = now.hour + now.minute/60.0
    # distance from noon
    dist = abs(h - 12.0)
    # normalized [0.0–1.0], 1 at noon, 0 at midnight
    t = max(0.0, 1.0 - dist / 12.0)

    # define your darkest and lightest blues:
    dark_blue  = (  0,   0,  80)  # midnight navy
    light_blue = (173, 216, 230)  # pale sky blue

    # linearly interpolate each channel
    r = int(dark_blue[0]  + (light_blue[0]  - dark_blue[0])  * t)
    g = int(dark_blue[1]  + (light_blue[1]  - dark_blue[1])  * t)
    b = int(dark_blue[2]  + (light_blue[2]  - dark_blue[2])  * t)

    return (r, g, b)

def draw_hotbar(screen, spoons, icon_image, spoon_name_input, streak_dates, coins, level, page):

    # 1) draw your existing spoons UI
    draw_spoons(screen, spoons, icon_image, spoon_name_input)

    # 2) compute current streak length
    if streak_dates:
        start_str, end_str = streak_dates[-1]
        start_dt = datetime.strptime(start_str, "%Y-%m-%d")
        end_dt   = datetime.strptime(end_str,   "%Y-%m-%d")
        current_streak = (end_dt - start_dt).days + 1
    else:
        current_streak = 0

    # 3) render text surfaces
    coin = pygame.transform.scale(coin_image, (coin_image.get_width() * coin_scale, coin_image.get_height() * coin_scale))
    xp_bar = pygame.transform.scale(xp_bar_image, (xp_bar_image.get_width() * xp_scale * 1.2, xp_bar_image.get_height() * xp_scale))
    coins_label  = f"{coins}"
    level_label = f"Lvl: {math.floor(level)}"

    coins_surf  = font.render(coins_label,  True, YELLOW) #type: ignore
    level_surf  = font.render(level_label,  True, WHITE) #type: ignore

    text_x = 115
    text_y = 30
    
    # xp bar
    screen.blit(level_surf, (text_x, text_y))
    pygame.draw.rect(screen, (63, 44, 27), (text_x + level_surf.get_width() + 10, text_y, xp_bar.get_width() - 10, xp_bar.get_height() - 10))  # background
    pygame.draw.rect(screen, (20, 150, 20), (text_x + level_surf.get_width() + 10, text_y, (xp_bar.get_width() - 10) * (level - math.floor(level)), xp_bar.get_height() - 10))  # experience
    screen.blit(xp_bar, (text_x + level_surf.get_width() + 5, text_y - 5))

    screen.blit(coins_surf,  (395 + xp_bar.get_width(), text_y))
    screen.blit(coin, (400 + xp_bar.get_width() + coins_surf.get_width(), text_y))

    window1_x = 785
    window_y = 20
    window2_x = 865

    alpha = get_day_alpha()
    if alpha > 0:
        # copy so you don’t permanently change the original
        avatar_lit = avatar_light.copy()
        avatar_lit.set_alpha(alpha)

    day_color = get_day_color()

    screen.blit(avatar_background, (735, 9))

    pygame.draw.rect(screen, day_color, (window1_x + 3, window_y + 3, 20, 20))
    screen.blit(avatar_window, (window1_x, window_y))
    screen.blit(avatar_lit, (window1_x - 25, window_y - 20))

    pygame.draw.rect(screen, day_color, (window2_x + 3, window_y + 3, 20, 20))
    screen.blit(avatar_window, (window2_x, window_y))
    screen.blit(avatar_lit, (window2_x - 25, window_y - 20))

def draw_spoons(screen, spoons, icon_image, spoon_name):
    # 1) render the label
    spoon_text = font.render(f"{spoon_name}: {spoons}", True, WHITE)  # type: ignore
    text_x, text_y = 115, 70
    screen.blit(spoon_text, (text_x, text_y))

    # 2) prep your icons
    ghost_icon = icon_image.copy()
    ghost_icon.set_alpha(int(255 * 0.3))

    total_capacity = 20
    icon_w, icon_h = icon_image.get_size()

    # 3) total region you want to occupy
    total_icon_image_width = 600
    start_x = text_x + spoon_text.get_width() + 5
    region_width = total_icon_image_width - spoon_text.get_width()
    region_width = max(region_width, icon_w)

    # 4) choose how much tighter (or looser) ghosts should space
    #    1.0 = same as full icons, <1 = more overlap, >1 = more spread
    ghost_spacing_factor = 0.8

    # 5) compute how many "gaps" of each type:
    full_gaps  = max(spoons - 1, 0)
    ghost_count = total_capacity - spoons

    # 6) solve (full_gaps * full_step + ghost_count * ghost_step) + icon_w == region_width
    #    with ghost_step = full_step * ghost_spacing_factor
    denom = full_gaps + ghost_count * ghost_spacing_factor
    if denom > 0:
        full_step  = (region_width - icon_w) / denom
    else:
        full_step = 0
    ghost_step = full_step * ghost_spacing_factor

    # 7) draw all 20
    x = start_x
    for i in range(total_capacity):
        sprite = icon_image if i < spoons else ghost_icon
        screen.blit(sprite, (int(x), text_y))  # adjust Y as you like

        # advance by the appropriate step
        if i < spoons - 1:
            x += full_step
        else:
            x += ghost_step
