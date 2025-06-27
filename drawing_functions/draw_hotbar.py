import pygame
from datetime import datetime
from config import *
import math
from math import hypot

# pre-create font so you’re not reloading every frame
font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen_height * 0.06))
coin_scale = 1.8
xp_scale = 1.4


# Initial avatar position
avatar_x = 860
avatar_y = 60
avatar_speed = 1

def get_alpha(time):
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
    if time == 'day':
        brightness = max(0.0, 1.0 - dist / 12.0)
        return int(brightness * 255)
    if time == 'night':
        brightness = max(0.0, 1.0 - dist / 12.0)
        return int((0.25 - brightness) * 255)
    if time == 'dark_night':
        brightness = max(0.0, 1.0 - dist / 12.0)
        return int((1.0 - brightness) * 255)

def _lerp(c0, c1, t):
    """linear-interpolate two colour tuples."""
    return tuple(int(a + (b - a) * t) for a, b in zip(c0, c1))

def get_day_color():
    """
    Return sky-colour that:
      • is darkest at midnight,
      • warms at sunrise / sunset,
      • brightens to pale blue at the solar midpoint,
      • and shifts sunrise±sunset ±2 h across the seasons.
    """
    # ---------- 1  current fractional hour & day-of-year -------------------
    now   = datetime.now()
    hourf = now.hour + now.minute/60.0               # 0–24 float
    doy   = now.timetuple().tm_yday                  # 1-366

    # ---------- 2  compute seasonal shift (±2 h) ---------------------------
    # Use a cosine so shift = +max on 21 Jun (doy≈172), −max on 21 Dec.
    # amplitude  = 2 hours
    hours_amp   = 2.0
    # phase so cos(0)=1 on 21 Jun
    shift = hours_amp * math.cos( 2*math.pi * (doy - 172) / 365.0 )

    sunrise = 6.0 - shift          # earlier in summer, later in winter
    sunset  = 18.0 + shift         # later  in summer, earlier in winter
    # keep within bounds
    sunrise = max(0.0, min(24.0, sunrise))
    sunset  = max(0.0, min(24.0, sunset))
    solar_mid = (sunrise + sunset) / 2.0   # stays 12.0 when shift is symmetric

    # ---------- 3  define key-frame colours --------------------------------
    night_blue      = (  0,   0,  80)      # midnight
    dawn_orange     = (255,120, 50)        # sunrise glow
    noon_blue       = (173,216,230)        # pale daytime sky
    dusk_orange     = (255,140, 60)        # sunset glow

    keyframes = [
        (0.0,   night_blue),
        (sunrise,  dawn_orange),
        (solar_mid, noon_blue),
        (sunset,   dusk_orange),
        (24.0,  night_blue)   # wrap
    ]

    # ---------- 4  find bracket segment & interpolate ----------------------
    for (h0, c0), (h1, c1) in zip(keyframes, keyframes[1:]):
        if h0 <= hourf <= h1:
            t = (hourf - h0) / (h1 - h0)   # 0-1 within segment
            return _lerp(c0, c1, t)

    # Fallback (shouldn’t occur)
    return night_blue


def draw_shadow(screen,
                image1, x1, y1,
                image2, x2, y2,
                kind="variable"):
    """
    Draws a realistic translucent shadow overhang with three rays:
      - one from each bottom-corner (near & far)
      - one from the bottom-center (max opacity line)

    Opacity:
      · Full at the center ray.
      · 0% at the two corner rays and at the tip.
      · Steeper quartic fade toward the edges.
    """
    import math
    # ------------------------------------------------ centres & corners
    w1, h1 = image1.get_width(), image1.get_height()
    w2, h2 = image2.get_width(), image2.get_height()
    cx, cy = x1 + w1/2.0, y1 + h1/2.0         # light center

    bl = (x2,       y2 + h2)                  # bottom-left of furniture
    br = (x2 + w2,  y2 + h2)                  # bottom-right
    center_corner = ((bl[0] + br[0]) / 2, bl[1])

    # choose near/far corners relative to light
    near = bl if abs(cx - bl[0]) < abs(cx - br[0]) else br
    far  = br if near is bl else bl

    # ------------------------------------------------ allocated length
    if kind == "constant":
        line_len = 175
    else:
        brightness = get_alpha("day") / 255.0  # 0 @ midnight → 1 @ noon
        line_len   = 75 + 100 * brightness

    # ------------------------------------------------ compute all three rays
    def make_ray(corner_pt):
        dx, dy = corner_pt[0] - cx, corner_pt[1] - cy
        dist   = math.hypot(dx, dy)
        if dist == 0 or line_len <= dist:
            return None
        ux, uy   = dx/dist, dy/dist
        overhang = line_len - dist
        end_pt   = (corner_pt[0] + ux*overhang,
                    corner_pt[1] + uy*overhang)
        return corner_pt, end_pt

    rays = []
    for corner in (near, center_corner, far):
        ray = make_ray(corner)
        if ray is None:
            return      # if any ray won’t project, skip the shadow
        rays.append(ray)

    # unpack
    (nc, ne), (cc, ce), (fc, fe) = rays

    # ------------------------------------------------ build the shadow polygon
    poly = [nc, cc, fc, fe, ce, ne]

    # bounding box
    xs, ys = zip(*poly)
    left, top  = int(min(xs)), int(min(ys))
    right, bot = int(max(xs))+1, int(max(ys))+1
    width, height = right-left, bot-top
    if width == 0 or height == 0:
        return

    # create mask for the wedge
    poly_offset = [(x-left, y-top) for x, y in poly]
    mask_surf   = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.polygon(mask_surf, (255,255,255), poly_offset)
    mask = pygame.mask.from_surface(mask_surf)

    # prepare gradient surface
    grad = pygame.Surface((width, height), pygame.SRCALPHA)
    α_max = 45

    # precompute dirs & lengths
    near_vec   = (ne[0]-nc[0], ne[1]-nc[1])
    near_len   = math.hypot(*near_vec)
    near_dir   = (near_vec[0]/near_len, near_vec[1]/near_len)

    center_vec = (ce[0]-cc[0], ce[1]-cc[1])
    center_len = math.hypot(*center_vec)

    # helper: distance from point to a ray
    def dist_to_ray(px, py, x0, y0, x1, y1, ray_len):
        return abs((y1 - y0)*px - (x1 - x0)*py + x1*y0 - y1*x0) / ray_len

    # ---------- fill in per-pixel alpha
    for yy in range(height):
        for xx in range(width):
            if not mask.get_at((xx, yy)):
                continue
            wx, wy = xx + left, yy + top

            # length-wise fade (along near-ray)
            vx, vy = wx-nc[0], wy-nc[1]
            t = (vx*near_dir[0] + vy*near_dir[1]) / near_len
            t = max(0.0, min(1.0, t))

            # compute half-width at this t (distance between near & far rays)
            near_pt = (nc[0] + near_dir[0]*near_len*t,
                       nc[1] + near_dir[1]*near_len*t)
            far_vec  = (fe[0]-fc[0], fe[1]-fc[1])
            far_pt = (fc[0] + far_vec[0]*t, fc[1] + far_vec[1]*t)
            half_width = math.hypot(far_pt[0]-near_pt[0],
                                     far_pt[1]-near_pt[1]) / 2.0

            # distance to the center-ray
            d_center = dist_to_ray(wx, wy, cc[0], cc[1], ce[0], ce[1], center_len)
            fade_side = min(1.0, d_center / half_width)
            # quartic for a steeper drop-off
            fade_side = fade_side**4

            α = int(α_max * (1.0 - t) * (1.0 - fade_side))
            if α > 0:
                grad.set_at((xx, yy), (0,0,0, α))

    # blit once
    screen.blit(grad, (left, top))



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

    # ------------------------------------------------------------------------------
    # Draw the avatar background, furniture, windows, etc.
    # ------------------------------------------------------------------------------

    def draw_window(x):
        pygame.draw.rect(screen, day_color, (x + 3, window_y + 3, 20, 20))
        screen.blit(avatar_window, (x, window_y))
        screen.blit(avatar_lit, (x - 25, window_y - 20))

        dark_alpha = get_alpha("dark_night")
        if dark_alpha > 0:
            avatar_dark_flowers = avatar_window_flower.copy()
            avatar_dark_flowers.set_alpha(dark_alpha)
        screen.blit(avatar_dark_flowers, (x, window_y))

    window1_x = 785
    window_y   = 20
    window2_x  = 885

    bookshelf_x = 800

    # ---------- daylight overlay (sunlight coming in) -----------------------------
    light_alpha = get_alpha("day")
    if light_alpha > 1:
        avatar_lit = avatar_light.copy()         # don’t mutate original
        avatar_lit.set_alpha(light_alpha)

    day_color = get_day_color()

    screen.blit(avatar_background, (735, 9))


    draw_window(window1_x)
    # draw_window(window2_x)   # second window, if needed

    screen.blit(avatar_lamp, (window2_x, window_y))
    screen.blit(avatar_light, (window2_x - 30, window_y - 25))
    screen.blit(avatar_bookshelf, (bookshelf_x, window_y + 20))

    # draw the avatar
    handle_movement()
    screen.blit(vlavatar, (avatar_x, avatar_y))

    #draw the shadows

    draw_shadow(screen, avatar_window, window1_x, window_y, avatar_bookshelf, bookshelf_x, window_y + 20, kind="variable")
    draw_shadow(screen, avatar_lamp, window2_x, window_y, avatar_bookshelf, bookshelf_x, window_y + 20, kind="constant")

    draw_shadow(screen, avatar_window, window1_x, window_y, vlavatar, avatar_x, avatar_y, kind="variable")
    draw_shadow(screen, avatar_lamp, window2_x, window_y, vlavatar, avatar_x, avatar_y, kind="constant")

    # ---------- night-time dark overlay ----------------
    dark_alpha = get_alpha("night")
    if dark_alpha > 0:
        # create a temporary surface the same size as the avatar background
        dark_overlay = pygame.Surface(avatar_background.get_size(), pygame.SRCALPHA)
        # fill with black using per-pixel alpha
        dark_overlay.fill((0, 0, 0, dark_alpha))   # (R, G, B, A)
        # blit the overlay
        screen.blit(dark_overlay, (735, 9))


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


def handle_movement():
    global avatar_x, avatar_y
    keys = pygame.key.get_pressed()  # Get the current state of all keys
    
    if keys[pygame.K_LEFT]:
        avatar_x -= avatar_speed  # Move left
    if keys[pygame.K_RIGHT]:
        avatar_x += avatar_speed  # Move right
    if keys[pygame.K_UP]:
        avatar_y -= avatar_speed  # Move up
    if keys[pygame.K_DOWN]:
        avatar_y += avatar_speed  # Move down

    # Prevent avatar from going off screen (assuming screen width 1024px and height 768px)
    avatar_x = max(745, min(avatar_x, 940 - vlavatar.get_width()))
    avatar_y = max(40, min(avatar_y, 110 - vlavatar.get_height()))