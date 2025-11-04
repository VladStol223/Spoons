import pygame
import math
from datetime import datetime, timedelta
from config import *
from drawing_functions.draw_input_box import draw_input_box

# Global UI elements
daily_inputs    = {}
labels          = []
spoon_rects     = []  # for the 20-spoons grid
rest_icon_rects = {}  # for our 3 rest icons 
rest_labels = {}

layout_heights = {
    "spoon_label":     0.32,
    "spoon_input_line":0.40,
    "rest_buttons":    0.35,
    "daily_prompt":    0.27,
}

timer_toggle_button = toggleButtons['timerButton']

timer_background = avatarBackgrounds['timer_background']
timer_hand = avatarBackgrounds['timer_hand']
timer_top = avatarBackgrounds['timer_top']

# === Timer configuration ===
deg_per_spoon = time_per_spoon * 6       # hand rotation per spoon (for display)

# === Timer animation state ===
timer_angle = 45         # starts rotated 45° CW (the "0" position)
target_angle = 45
rotating = False
rotation_speed = 180     # degrees per second (visual spin)

# === Timer logic state ===
timer_active = False
timer_start_time = None
timer_end_time = None
spoons_to_recover = 0
total_spoons_to_recover = 0
next_spoon_time = None

# === Timer intro animation state (initial spin from 45° to start angle) ===
intro_anim_active = False
intro_start_time = None
intro_duration = 0.8  # seconds; will be tweaked per rest-size on start

def set_opacity(image, alpha):
    temp = image.copy()
    temp.set_alpha(alpha)
    return temp

def tint_image(image, tint_color):
    surf = image.copy().convert_alpha()
    r, g, b = tint_color[:3]
    mask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    mask.fill((r, g, b, 255))
    surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return surf

def get_pulse_alpha(t, min_alpha=128, max_alpha=255, speed=4.0):
    return int(min_alpha + (max_alpha - min_alpha) * 0.3 * (1 + math.sin(t * speed)))


def draw_input_spoons(screen, spoons, spoon_name, delta_time, icon_image, input_active, background_color, timer_toggle_on, time_per_spoon, x_offset=40):
    global spoon_rects, rest_icon_rects, rest_labels, timer_angle, rotating, timer_active, timer_start_time, timer_end_time, spoons_to_recover, total_spoons_to_recover, next_spoon_time, intro_anim_active, intro_start_time, intro_duration

    # --- Timer Toggle Button ---
    toggle_rect = pygame.Rect(120, 100, timer_toggle_button.get_width(), timer_toggle_button.get_height())

    # Aura effect when ON
    if timer_toggle_on:
        t = pygame.time.get_ticks() / 1000.0
        pulse_alpha = get_pulse_alpha(t, 150, 255, 4.0)
        aura_radius = int(timer_toggle_button.get_width() * 0.7)
        aura_surf = pygame.Surface((aura_radius*2, aura_radius*2), pygame.SRCALPHA)
        pygame.draw.circle(aura_surf, (255, 255, 150, pulse_alpha), (aura_radius, aura_radius), aura_radius)
        screen.blit(aura_surf, (toggle_rect.centerx - aura_radius, toggle_rect.centery - aura_radius))

    # Blit toggle button
    screen.blit(timer_toggle_button, toggle_rect.topleft)

    # Base screen setup
    sw, sh = screen.get_size()
    mouse_x, mouse_y = pygame.mouse.get_pos()
    sw -= 200

    title_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(sh * 0.07))
    rest_font  = pygame.font.Font("fonts/Stardew_Valley.ttf", int(sh * 0.045))
    timer_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(sh * 0.047))

    shift_y = 0
    shift_x = 0

    # --- Timer Visualization when ON ---
    if timer_toggle_on:
        tw, th = timer_background.get_size()
        timer_x = (sw - tw) // 2 + 135
        timer_y = int(sh * 0.18)
        screen.blit(timer_background, (timer_x, timer_y))

        # --- Update logic if active ---
        total_rotation = total_spoons_to_recover * deg_per_spoon
        total_secs = total_spoons_to_recover * time_per_spoon * 60

        if intro_anim_active and intro_start_time:
            # Phase A: spin from 45° to start-angle, label counts up 00:00 -> total time
            p = (datetime.now() - intro_start_time).total_seconds() / max(0.001, intro_duration)
            p = max(0.0, min(1.0, p))
            timer_angle = 45 + p * total_rotation

            # Count-up label during intro (H:MM:SS)
            intro_elapsed_secs = int(p * total_secs)
            ih   = intro_elapsed_secs // 3600
            im   = (intro_elapsed_secs % 3600) // 60
            isec = intro_elapsed_secs % 60
            time_str = f"{ih}:{im:02}:{isec:02}"
            text_surf = timer_font.render(time_str, True, BLACK)  # type: ignore
            text_rect = text_surf.get_rect(center=(timer_x + tw//2, timer_y + th//2 - 42))
            screen.blit(text_surf, text_rect)

            # Transition to countdown when intro finishes
            if p >= 1.0:
                intro_anim_active = False
                timer_active = True
                timer_start_time = datetime.now()
                timer_end_time   = timer_start_time + timedelta(seconds=total_secs)
                next_spoon_time  = timer_start_time + timedelta(minutes=time_per_spoon)

        elif timer_active and timer_start_time and timer_end_time:
            # Phase B: countdown; hand moves back to 45°, label shows time remaining
            now = datetime.now()
            remaining_secs = max(0, (timer_end_time - now).total_seconds())
            elapsed = total_secs - remaining_secs
            prog = 0.0 if total_secs <= 0 else (elapsed / total_secs)
            prog = max(0.0, min(1.0, prog))
            timer_angle = 45 + (1.0 - prog) * total_rotation

            # Award spoons at intervals — ensures 1 spoon per time_per_spoon minutes
            while spoons_to_recover > 0 and now >= next_spoon_time:
                spoons += 1
                spoons_to_recover -= 1
                next_spoon_time += timedelta(minutes=time_per_spoon)
                if spoons_to_recover <= 0:
                    timer_active = False
                    break

            # Remaining time label (H:MM:SS)
            ih   = int(remaining_secs // 3600)
            im   = int((remaining_secs % 3600) // 60)
            isec = int(remaining_secs % 60)
            time_str = f"{ih}:{im:02}:{isec:02}"
            text_surf = timer_font.render(time_str, True, BLACK)  # type: ignore
            text_rect = text_surf.get_rect(center=(timer_x + tw//2, timer_y + th//2 - 42))
            screen.blit(text_surf, text_rect)
        else:
            # Idle in timer mode (no active timer/intro) -> show 0:00:00 at rest
            timer_angle = 45
            text_surf = timer_font.render("0:00:00", True, BLACK)  # type: ignore
            text_rect = text_surf.get_rect(center=(timer_x + tw//2, timer_y + th//2 - 42))
            screen.blit(text_surf, text_rect)


        # --- Draw hand ---
        rotated_hand = pygame.transform.rotate(timer_hand, -timer_angle)
        hand_rect = rotated_hand.get_rect(center=(timer_x + tw//2, timer_y + th//2))
        screen.blit(rotated_hand, hand_rect)

        # Top overlay
        screen.blit(timer_top, (timer_x, timer_y))

        # Move rest icons down
        shift_y = int(th * 0.45)
        shift_x = 30

    # --- Rest icons ---
    button_w = button_h = int(sh * 0.35)
    spacing = sw * 0.05
    total_w = 3 * button_w + 2 * spacing
    start_x = ((sw - total_w) // 2) + x_offset
    y_rest = int(sh * layout_heights["rest_buttons"])

    rest_icon_rects = {
        "short": pygame.Rect(start_x - shift_x, y_rest, button_w, button_h),
        "half":  pygame.Rect(start_x + (button_w + spacing), y_rest + shift_y, button_w, button_h),
        "full":  pygame.Rect(start_x + 2*(button_w + spacing) + shift_x, y_rest, button_w, button_h)
    }

    # --- Animation handling ---
    icons = {"short": short_rest, "half": half_rest, "full": full_rest}
    hovered_rest = None

    frame_w, frame_h = 90, 90
    columns, rows = 5, 8
    gap = 1
    frame_count = columns * rows
    t = pygame.time.get_ticks() / 1000.0
    fps = 8
    current_frame = int(t * fps) % frame_count
    row = current_frame // columns
    col = current_frame % columns
    sx = col * (frame_w + gap)
    sy = row * (frame_h + gap)
    frame_rect = pygame.Rect(sx, sy, frame_w, frame_h)

    for name, rect in rest_icon_rects.items():
        sheet = icons[name]
        try:
            frame = sheet.subsurface(frame_rect).copy()
        except ValueError:
            frame = sheet.subsurface(pygame.Rect(0, 0, frame_w, frame_h)).copy()
        frame_scaled = pygame.transform.scale(frame, rect.size)
        screen.blit(frame_scaled, rect.topleft)
        if rect.collidepoint(mouse_x, mouse_y):
            hovered_rest = name

    # --- Rest labels ---
    rest_labels.clear()
    texts = {"short": "Short rest", "half": "Half rest", "full": "Full rest"}
    for name, rect in rest_icon_rects.items():
        label = rest_font.render(texts[name], True, (255, 255, 255))
        label_rect = label.get_rect(center=(rect.centerx, rect.bottom + label.get_height()//2 - 20))
        screen.blit(label, label_rect)


def logic_input_spoons(event, daily_spoons, spoons, input_active, timer_toggle_on, rest_spoons):
    global spoon_rects, rest_icon_rects
    global timer_active, timer_start_time, timer_end_time, spoons_to_recover, total_spoons_to_recover, next_spoon_time, intro_anim_active, intro_start_time, intro_duration, timer_angle
    page = "input_spoons"

    rest_values = rest_spoons

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        # --- Timer toggle click ---
        toggle_rect = pygame.Rect(120, 100, timer_toggle_button.get_width(), timer_toggle_button.get_height())
        if toggle_rect.collidepoint(event.pos):
            timer_toggle_on = not timer_toggle_on
            return spoons, daily_spoons, page, input_active, timer_toggle_on, rest_spoons

        # --- Rest icon clicks ---
        for name, rect in rest_icon_rects.items():
            if rect.collidepoint(event.pos):
                rest_amount = rest_values[name]

                if timer_toggle_on:
                    # Phase A: intro spin setup (no spoons granted yet)
                    total_spoons_to_recover = rest_amount
                    spoons_to_recover = rest_amount
                    intro_anim_active = True
                    intro_start_time = datetime.now()
                    intro_duration = 0.4 + 0.2 * rest_amount  # feel: 2->0.8s, 5->1.4s, 10->2.4s (tweak)
                    timer_active = False  # countdown begins after intro finishes
                    timer_angle = 45      # start from zero position; draw() animates to target

                else:
                    # --- Instant spoon recovery (classic mode) ---
                    spoons += rest_amount
                    if spoons > 99:
                        spoons = 99

                return spoons, daily_spoons, "input_spoons", False, timer_toggle_on, rest_spoons

    return spoons, daily_spoons, page, input_active, timer_toggle_on, rest_spoons