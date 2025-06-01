import pygame
from datetime import datetime
from config import *
import math

# pre-create font so you’re not reloading every frame
font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen_height * 0.06))
coin_scale = 1.8
xp_scale = 1.4

def draw_inventory(screen, spoons, icon_image, spoon_name_input, streak_dates, coins, level, page):

    if page == "input_tasks" or page == "manage_tasks":
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
        streak_label = f"Streak: {current_streak} Day{'s' if current_streak != 1 else ''}"
        coins_label  = f"{coins}"
        level_label = f"Lvl: {math.floor(level)}"

        streak_surf = font.render(streak_label, True, WHITE) #type: ignore
        coins_surf  = font.render(coins_label,  True, WHITE) #type: ignore
        level_surf  = font.render(level_label,  True, WHITE) #type: ignore

        text_x = 115
        text_y = 30
        screen.blit(streak_surf, (text_x, text_y))
        screen.blit(coins_surf,  (text_x + streak_surf.get_width() + 25, text_y))
        screen.blit(coin, (text_x + streak_surf.get_width() + 25 + coins_surf.get_width() + 5, text_y))
        screen.blit(level_surf, (text_x + streak_surf.get_width() + 50 + coins_surf.get_width() + 5 + coin.get_width() + 5, text_y))
        # xp bar
        pygame.draw.rect(screen, (63, 44, 27), (text_x + streak_surf.get_width() + 50 + coins_surf.get_width() + 5 + coin.get_width() + 5 + level_surf.get_width() + 10, text_y, xp_bar.get_width() - 10, xp_bar.get_height() - 10))  # background
        pygame.draw.rect(screen, (20, 150, 20), (text_x + streak_surf.get_width() + 50 + coins_surf.get_width() + 5 + coin.get_width() + 5 + level_surf.get_width() + 10, text_y, (xp_bar.get_width() - 10) * (level - math.floor(level)), xp_bar.get_height() - 10))  # experience
        screen.blit(xp_bar, (text_x + streak_surf.get_width() + 50 + coins_surf.get_width() + 5 + coin.get_width() + 5 + level_surf.get_width() + 5, text_y - 5))


def draw_spoons(screen, spoons, icon_image, spoon_name):
    # render the label
    spoon_text = font.render(f"{spoon_name}:", True, WHITE)  # type: ignore
    text_x, text_y = 115, 70
    screen.blit(spoon_text, (text_x, text_y))

    # layout parameters
    padding      = -10
    start_x      = text_x + spoon_text.get_width() + 5
    icon_y       = 68
    icon_w, _    = icon_image.get_size()
    full_step    = icon_w + padding
    overlap_step = int(icon_w * 0.75)

    # prepare a 30%-alpha “ghost” icon for missing spoons
    ghost_icon = icon_image.copy()
    ghost_icon.set_alpha(int(255 * 0.3))

    # total slots to show
    total_capacity = 20

    x = start_x
    for i in range(total_capacity):
        if i < spoons:
            # full-opacity spoon
            screen.blit(icon_image, (x, icon_y))
        else:
            # ghosted spoon
            screen.blit(ghost_icon,  (x, icon_y))
        # advance by overlap for all after the first max_no_overlap
        if i < max(spoons - 10, 0):
            x += full_step
        else:
            x += overlap_step

    # draw the numeric count at the right
    spoon_amount_text = font.render(f"{spoons}", True, WHITE)  # type: ignore
    screen.blit(spoon_amount_text, (680, 70))
