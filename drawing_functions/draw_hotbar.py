import pygame
from datetime import datetime
from config import *
from drawing_functions.draw_input_box import draw_input_box, InputBox, logic_input_box
import math

# pre-create font so you’re not reloading every frame
font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen_height * 0.06))

spoon_input_box = InputBox(
    None,
    text="",
    multiline=False,
    fontsize=0.06,
    box_type="number"
)
spoon_input_box.active = False
spoon_input_box.caret = 0
spoon_input_box.saved_text = ""

def draw_hotbar(screen, page, background_color, spoons, icon_image, spoon_name_input, daily_spoons, today_needed, spoons_used_today):
    # ----------------------------
    # Hover Animation Settings
    # ----------------------------
    hover_speed = 4.0       # Higher = faster slide
    hover_offset_bar = 45   # How far the hotbar (spoons + fatigue bar) moves upward
    hover_offset_text = 30  # How far the stats text moves upward
    text_color = (255, 255, 255)
    shadow_color = (0, 0, 0)
    shadow_offset = 2

    # Static state variables (persist between frames)
    if not hasattr(draw_hotbar, "offset_bar"):
        draw_hotbar.offset_bar = 0.0
        draw_hotbar.offset_text = 0.0
        draw_hotbar.is_hovered = False

    screen.blit(info_button, (screen.get_width() - info_button.get_width() - 30, 30))

    # ----------------------------
    # Detect Hover State
    # ----------------------------
    mx, my = pygame.mouse.get_pos()
    hover_area = (screen_width - 80 < mx < screen_width - 18) and (18 < my < 80)
    draw_hotbar.is_hovered = hover_area

    # Animate offsets toward targets
    target_bar = -hover_offset_bar if draw_hotbar.is_hovered else 0
    target_text = -hover_offset_text if draw_hotbar.is_hovered else 0
    draw_hotbar.offset_bar += (target_bar - draw_hotbar.offset_bar) * 0.1 * hover_speed
    draw_hotbar.offset_text += (target_text - draw_hotbar.offset_text) * 0.1 * hover_speed

    # Convert to integers for drawing
    y_offset_bar = int(draw_hotbar.offset_bar)
    y_offset_text = int(draw_hotbar.offset_text)

    # ----------------------------
    # Draw spoons + fatigue bar (move by bar offset)
    # ----------------------------
    draw_spoons(screen, page, background_color, spoons, icon_image, spoon_name_input, today_needed=today_needed, y_offset=y_offset_bar)

    fatigue_bar = hotbar['fatigue_bar']

    fatigue_bar_x = screen_width - fatigue_bar.width - 80
    fatigue_bar_y = 28 + y_offset_bar
    bar_width, bar_height = fatigue_bar.get_size()

    color_x = fatigue_bar_x + 8
    color_y = fatigue_bar_y + 8
    color_width = bar_width - 16
    color_height = bar_height - 16

    today_str = datetime.now().strftime("%a")
    daily_target = daily_spoons.get(today_str, 10)
    used = spoons_used_today

    slot_count = max(1, daily_target)
    slot_width = color_width / slot_count
    fill_width = min(used * slot_width, color_width * 3)


    green_limit = daily_target * slot_width
    yellow_limit = daily_target * 2 * slot_width

    if used > 0:
        green_w = min(fill_width, green_limit)
        pygame.draw.rect(screen, (0, 255, 0), (color_x, color_y, green_w, color_height))
        if used > daily_target:
            yellow_w = min(fill_width - green_limit, yellow_limit - green_limit)
            pygame.draw.rect(screen, (255, 255, 0), (color_x, color_y, yellow_w, color_height))
        if used > daily_target * 2:
            red_w = fill_width - yellow_limit
            pygame.draw.rect(screen, (255, 0, 0), (color_x, color_y, red_w, color_height))

    line_color = (63, 44, 27)
    for i in range(1, slot_count):
        line_x = int(color_x + i * slot_width)
        pygame.draw.line(screen, line_color, (line_x, color_y), (line_x, color_y + color_height), 2)

    screen.blit(fatigue_bar, (fatigue_bar_x, fatigue_bar_y))

    # ----------------------------
    # Draw Hover Stats Text (move by smaller offset)
    # ----------------------------
    if draw_hotbar.is_hovered or abs(draw_hotbar.offset_text) > 1:
        stats_y = 45 + y_offset_text + hover_offset_text
        text_str = f"Spoons owned: {spoons}       Spoons needed: {today_needed}       Spoons used: {spoons_used_today}"

        shadow = font.render(text_str, True, shadow_color)
        text_surface = font.render(text_str, True, text_color)

        text_rect = text_surface.get_rect(center=(screen_width // 2 + 25, stats_y))
        shadow_rect = text_rect.copy()
        shadow_rect.x += shadow_offset
        shadow_rect.y += shadow_offset

        screen.blit(shadow, shadow_rect)
        screen.blit(text_surface, text_rect)

def draw_spoons(screen, page, background_color, spoons, icon_image, spoon_name, today_needed, y_offset=0):
    import pygame

    # --- SPOON INPUT BOX (invisible) ---
    spoon_input_box.rect = pygame.Rect(120, 28 + y_offset, 40, 37)
    # Only update input text if the box is NOT active AND value changed externally
    if not spoon_input_box.active and spoon_input_box.text != str(spoons):
        spoon_input_box.text = str(spoons)
        spoon_input_box.caret = len(spoon_input_box.text)


    # Pulse border if on input spoons page
    if page == "input_spoons":
        t = pygame.time.get_ticks() / 1000.0
        pulse = (math.sin(t * (2 * math.pi / 30)) + 1) * 0.5  # 30 sec cycle
        border_color = (
            max(0, int(background_color[0] * (1 - 0.05 * pulse))),
            max(0, int(background_color[1] * (1 - 0.05 * pulse))),
            max(0, int(background_color[2] * (1 - 0.05 * pulse)))
        )
    else:
        border_color = background_color

    draw_input_box(
        screen,
        spoon_input_box,
        background_color,
        border_color,
        background_color=background_color,
        infill="invisible"
    )


    total_slots = 11
    slot_spacing = 33
    base_x, base_y = 160, 28 + y_offset


    # --- Derive icon variants ---
    stem = None
    for key, val in spoonIcons.items():
        if val is icon_image:
            stem = key.replace("_image", "")
            break
    if not stem:
        return

    icon_1 = spoonIcons[f"{stem}_image"].convert_alpha()
    icon_5 = spoonIcons.get(f"{stem}_image_5", icon_1).convert_alpha()
    icon_25 = spoonIcons.get(f"{stem}_image_25", icon_1).convert_alpha()
    exclamation = spoonIcons["exclamation_mark"].convert_alpha()

    # --- Sizes and scaling ---
    icon_w, icon_h = icon_1.get_size()
    ghost_scale = 0.65
    ghost_alpha = int(255 * 0.35)

    ghost_1 = pygame.transform.smoothscale(icon_1, (int(icon_w * ghost_scale), int(icon_h * ghost_scale))); ghost_1.set_alpha(ghost_alpha)
    ghost_5 = pygame.transform.smoothscale(icon_5, (int(icon_w * ghost_scale), int(icon_h * ghost_scale))); ghost_5.set_alpha(ghost_alpha)
    ghost_25 = pygame.transform.smoothscale(icon_25, (int(icon_w * ghost_scale), int(icon_h * ghost_scale))); ghost_25.set_alpha(ghost_alpha)

    ex_w, ex_h = exclamation.get_size()
    ghost_ex = pygame.transform.smoothscale(exclamation, (int(ex_w * ghost_scale), int(ex_h * ghost_scale))); ghost_ex.set_alpha(200)

    # --- Helper: break into denominations ---
    def breakdown(value):
        parts = []
        while value > 0 and len(parts) < total_slots:
            if value >= 25:
                parts.append(25)
                value -= 25
            elif value >= 5:
                parts.append(5)
                value -= 5
            else:
                parts.append(1)
                value -= 1
        return parts

    # --- Helper: denomination difference ---
    def denomination_diff(needed_parts, owned_parts):
        def count_parts(parts):
            counts = {25: 0, 5: 0, 1: 0}
            for p in parts:
                counts[p] += 1
            return counts

        need = count_parts(needed_parts)
        own = count_parts(owned_parts)

        diff = {25: need[25]-own[25], 5: need[5]-own[5], 1: need[1]-own[1]}
        result = []
        for denom in (25, 5, 1):
            n = diff[denom]
            if n > 0:
                result.extend([denom]*n)      # ghosts
            elif n < 0:
                result.extend([-denom]*(-n))  # missing ex marks
        return result

    # --- Determine slot contents ---
    owned_parts = breakdown(spoons)
    needed_parts = breakdown(today_needed)
    diffs = denomination_diff(needed_parts, owned_parts)

    # Separate ghosts vs removals
    ghost_parts = [abs(d) for d in diffs if d > 0]
    remove_ex_parts = [abs(d) for d in diffs if d < 0]

    # Start assuming all owned have exclamation marks
    owned_ex_flags = [True] * len(owned_parts)

    # Remove marks that correspond to "extra" denominations
    for extra_val in remove_ex_parts:
        # Find the rightmost owned part matching this denomination that still has a mark
        for i in range(len(owned_parts) - 1, -1, -1):
            if owned_parts[i] == extra_val and owned_ex_flags[i]:
                owned_ex_flags[i] = False
                break

    # Build slots (full icons first, then ghosts, then empties)
    slots = []
    for i, val in enumerate(owned_parts):
        slots.append(("full", val, owned_ex_flags[i]))
    for val in ghost_parts:
        slots.append(("ghost", val, True))
    while len(slots) < total_slots:
        slots.append(("empty", 0, False))

    # --- Drawing helper ---
    def pick_img(mode, val):
        if val == 25:
            return icon_25 if mode == "full" else ghost_25
        if val == 5:
            return icon_5 if mode == "full" else ghost_5
        if val == 1:
            return icon_1 if mode == "full" else ghost_1
        return None

    # --- Draw ---
    for i, (mode, val, has_ex) in enumerate(slots[:total_slots]):
        x = base_x + i * slot_spacing + 7 if mode == "ghost" else base_x + i * slot_spacing
        y = base_y + 5 if mode == "ghost" else base_y
        img = pick_img(mode, val)
        if img is None or mode == "empty":
            center = (x + icon_w // 2, y + icon_h // 2)
            pygame.draw.circle(screen, (0, 0, 0), center, int(icon_w * 0.15), 2)
            continue

        iw, ih = img.get_size()
        screen.blit(img, (x, y))

        if has_ex:
            ex = ghost_ex if mode == "ghost" else exclamation
            ex_x = x + 5 + (iw - ex.get_width()) // 2
            ex_y = y + (ih - ex.get_height()) // 2
            screen.blit(ex, (ex_x, ex_y))

def logic_hotbar(event, page, spoons):
    global spoon_input_box

    # Let InputBox handle typing
    logic_input_box(event, spoon_input_box, pygame.display.get_surface())

    # Only update spoons when the user is actively typing in the box
    if spoon_input_box.active:
        try:
            val = int(spoon_input_box.text)
        except:
            val = 0

        val = max(0, min(99, val))
        return val

    return spoons