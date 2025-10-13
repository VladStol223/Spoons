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



def draw_hotbar(screen, spoons, icon_image, spoon_name_input, streak_dates, coins, level, page, today_needed, spoons_used_today):

    # 1) draw your existing spoons UI
    draw_spoons(screen, spoons, icon_image, spoon_name_input)

    # 2) “Spoons used today” (replaces XP bar)
    text_x = 115
    text_y = 30

    used_msg = f"'s used today: {int(spoons_used_today)}"
    used_surf = font.render(used_msg, True, WHITE)  # type: ignore
    icon_x = text_x 
    screen.blit(icon_image, (icon_x, text_y - 3))
    msg_x = icon_x + 30
    msg_y = text_y
    screen.blit(used_surf, (msg_x, msg_y))

    # 3) “{icon}s needed for today: {num}” to the right of the used-today text
    msg = f"'s needed for today: {today_needed}"
    msg_surf = font.render(msg, True, WHITE)  # type: ignore

    icon_x = text_x + used_surf.get_width() + 290
    screen.blit(icon_image, (icon_x, text_y - 3))
    msg_x = icon_x + 30
    msg_y = text_y
    screen.blit(msg_surf, (msg_x, msg_y))


def draw_spoons(screen, spoons, icon_image, spoon_name):
    # 1) label
    spoon_text = font.render(f"{spoon_name}: {spoons}", True, WHITE)  # type: ignore
    text_x, text_y = 115, 70
    screen.blit(spoon_text, (text_x, text_y))

    # 2) prep icons
    icon_image = icon_image.convert_alpha()
    icon_w, icon_h = icon_image.get_size()
    ghost_scale = 0.85  # slightly smaller
    ghost_w, ghost_h = int(icon_w * ghost_scale), int(icon_h * ghost_scale)
    ghost_icon = pygame.transform.smoothscale(icon_image, (ghost_w, ghost_h))
    ghost_icon.set_alpha(int(255 * 0.35))  # a bit lighter

    total_capacity = 20

    # 3) total region you want to occupy
    total_icon_image_width = 800
    start_x = text_x + spoon_text.get_width() + 5
    region_width = total_icon_image_width - spoon_text.get_width()
    region_width = max(region_width, icon_w)

    # 4) spacing factors
    ghost_spacing_factor = 0.8

    # 5) gaps math
    full_gaps = max(spoons - 1, 0)
    ghost_count = total_capacity - spoons
    denom = full_gaps + ghost_count * ghost_spacing_factor
    full_step = (region_width - icon_w) / denom if denom > 0 else 0.0
    ghost_step = full_step * ghost_spacing_factor

    # 6) draw all 20 (ghosts are vertically centered to the full icon height)
    x = start_x
    for i in range(total_capacity):
        use_ghost = i >= spoons
        surf = ghost_icon if use_ghost else icon_image
        sw, sh = (ghost_w, ghost_h) if use_ghost else (icon_w, icon_h)
        if use_ghost:
            # ghost icons are centered vertically
            y = text_y + (icon_h - sh*0.85) // 2
        else:
            y = text_y + (icon_h - sh) // 2
        screen.blit(surf, (int(x), int(y)))
        x += full_step if i < spoons - 1 else ghost_step