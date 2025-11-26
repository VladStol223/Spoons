import pygame
import math
from datetime import datetime, timedelta
from config import *
from drawing_functions.draw_input_box import draw_input_box
from drawing_functions.draw_logic_timer import TimerEngine

timer_engine = TimerEngine()

layout_heights = {
    "spoon_label":     0.32,
    "spoon_input_line":0.40,
    "rest_buttons":    0.35,
    "daily_prompt":    0.27,
}


def draw_input_spoons(screen, spoons, spoon_name, delta_time, icon_image,
                      input_active, background_color, timer_toggle_on,
                      time_per_spoon, x_offset=40):

    global rest_icon_rects

    sw, sh = screen.get_size()
    sw -= 200
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # ================================================================
    # ALWAYS DRAW TIMER TOGGLE BUTTON (even when timer is OFF)
    # ================================================================
    toggle_button = timer_engine.timer_toggle_button
    toggle_rect = pygame.Rect(
        120, 100,
        toggle_button.get_width(),
        toggle_button.get_height()
    )

    # Glowing aura only when ON
    if timer_toggle_on:
        t = pygame.time.get_ticks() / 1000
        alpha = int(150 + 105 * (0.5 * (1 + math.sin(t * 4))))
        r = int(toggle_button.get_width() * 0.7)
        aura = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(aura, (255, 255, 150, alpha), (r, r), r)
        screen.blit(aura, (toggle_rect.centerx - r, toggle_rect.centery - r))

    # Draw the toggle button itself
    screen.blit(toggle_button, toggle_rect)

    # Tooltip
    if toggle_rect.collidepoint(mouse_x, mouse_y):
        timer_engine._tooltip(screen, toggle_rect, "Recover spoons over time")


    # ================================================================
    # 1) DRAW TIMER — BUT FREEZE WHEN TOGGLE OFF
    # ================================================================
    if timer_toggle_on:
        spoons = timer_engine.draw(screen, "rest", timer_toggle_on, spoons, time_per_spoon)
        timer_drawn = True
        # Restore original icon shifting logic
        tw, th = avatarBackgrounds["timer_background"].get_size()
        shift_y = int(th * 0.45)
        shift_x = 30
    else:
        # When OFF, DO NOT update timer logic anywhere,
        # DO NOT update timer angle in engine,
        # DO NOT animate intro or countdown
        # DO NOT draw the timer UI

        timer_drawn = False
        shift_y = 0
        shift_x = 0


    # ================================================================
    # 2) DRAW REST ICONS — WITH ORIGINAL SHIFT BEHAVIOR RESTORED
    # ================================================================
    button_w = button_h = int(sh * 0.35)
    spacing = sw * 0.05
    total_w = 3 * button_w + 2 * spacing
    start_x = ((sw - total_w) // 2) + x_offset
    y_rest = int(sh * layout_heights["rest_buttons"])

    # Exact original icon placement restored:
    rest_icon_rects = {
        "short": pygame.Rect(start_x - shift_x, y_rest, button_w, button_h),
        "half":  pygame.Rect(start_x + (button_w + spacing), y_rest + shift_y, button_w, button_h),
        "full":  pygame.Rect(start_x + 2*(button_w + spacing) + shift_x, y_rest, button_w, button_h),
    }

    icons = {"short": short_rest, "half": half_rest, "full": full_rest}

    frame_w, frame_h = 90, 90
    cols, rows = 5, 8
    frame_count = cols * rows
    t = pygame.time.get_ticks() / 1000
    fps = 8
    current_frame = int(t * fps) % frame_count
    row = current_frame // cols
    col = current_frame % cols
    sx = col * (frame_w + 1)
    sy = row * (frame_h + 1)
    frame_rect = pygame.Rect(sx, sy, frame_w, frame_h)

    for name, rect in rest_icon_rects.items():
        sheet = icons[name]
        try:
            frame = sheet.subsurface(frame_rect).copy()
        except Exception:
            frame = sheet.subsurface(pygame.Rect(0, 0, frame_w, frame_h)).copy()

        frame_scaled = pygame.transform.scale(frame, rect.size)
        screen.blit(frame_scaled, rect.topleft)

    # labels
    font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(sh * 0.045))
    names = {"short": "Short rest", "half": "Half rest", "full": "Full rest"}

    for name, rect in rest_icon_rects.items():
        surf = font.render(names[name], True, (255, 255, 255))
        label_rect = surf.get_rect(center=(rect.centerx, rect.bottom + surf.get_height()//2 - 20))
        screen.blit(surf, label_rect)

    return spoons


def logic_input_spoons(event, daily_spoons, spoons, input_active,
                       timer_toggle_on, rest_spoons):

    # --- TIMER LOGIC ---
    timer_toggle_on, spoons = timer_engine.logic(
        "rest",
        event,
        timer_toggle_on,
        rest_spoons,
        spoons,
        rest_icon_rects
    )

    return spoons, daily_spoons, "input_spoons", input_active, timer_toggle_on, rest_spoons
