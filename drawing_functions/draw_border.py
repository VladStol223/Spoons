#draw_border.py
import pygame
import random
from config import *

# === CONFIGURATION ===
base_sizes = {
        "corner":    (12, 12),
        "edge":      (6,  12),
        "t_corner":  (14, 12),
        "calendar":   (9, 24),}

def draw_border(screen, rect, page, background_color, border, is_maximized, scale_factor):
    corner          = border['corner']
    edge_one        = border['edge1']
    edge_two        = border['edge2']
    tcorner         = border['tcorner']
    calendar_border = border['calendar_border']
    x, y, w, h = rect
    sw, sh = screen.get_size()

    # choose your base scale
    scale = max(3, (6 / scale_factor)) if is_maximized else 3

    hub_border_offset = 100     # px from left edge; adjust as needed
    hotbar_border_offset = 80  # px from top edge for inventory page   was 120
    avatar_border_offset = 300  # px from right edge for input_tasks vertical border
    inventory_border_offset = 134 # px from left edge;
    
    # deterministic RNG per border
    seed = x + (y << 8) + (w << 16) + (h << 24)
    rng = random.Random(seed)

    # downscale raw assets to base sizes
    bw, bh = base_sizes["corner"]
    corner_base   = pygame.transform.scale(corner,   (bw, bh))
    ew, eh = base_sizes["edge"]
    edge1_base    = pygame.transform.scale(edge_one,  (ew, eh))
    edge2_base    = pygame.transform.scale(edge_two,  (ew, eh))
    tcw, tch = base_sizes["t_corner"]
    tcorner_base  = pygame.transform.scale(tcorner,  (tcw, tch))
    cbw, cbh = base_sizes["calendar"]
    calendar_base = pygame.transform.scale(calendar_border, (cbw, cbh))

    # scale up by scale
    scw, sch   = bw * scale, bh * scale
    sew, seh   = ew * scale, eh * scale
    stcw, stch = tcw * scale, tch * scale
    cbw, cbh = cbw * scale, cbh * scale

    corner_s    = pygame.transform.scale(corner_base,    (scw,  sch))
    edge1_s     = pygame.transform.scale(edge1_base,     (sew,  seh))
    edge2_s     = pygame.transform.scale(edge2_base,     (sew,  seh))
    tcorner_s   = pygame.transform.scale(tcorner_base,   (stcw, stch))
    calendar_s  = pygame.transform.scale(calendar_base,  (cbw,  cbh))

    # corner variants
    tl = corner_s
    tr = pygame.transform.flip(corner_s, True,  False)
    bl = pygame.transform.flip(corner_s, False, True)
    br = pygame.transform.flip(corner_s, True,  True)

    # 1) rectangle corners
    screen.blit(tl, (x,           y))
    screen.blit(tr, (x + w - scw, y))
    screen.blit(br, (x + w - scw, y + h - sch))
    screen.blit(bl, (x,           y + h - sch))

    # 2) top & bottom edges
    tx = x + scw
    while tx < x + w - scw:
        edge_tile = rng.choice([edge1_s, edge2_s])
        top_tile  = pygame.transform.rotate(edge_tile, -90)
        bot_tile  = pygame.transform.rotate(edge_tile,  90)

        # Skip top edge between 390 and 626 when on the calendar page
        if page == "calendar" and 390 <= tx <= 626:
            # still draw the bottom edge, skip top
            screen.blit(bot_tile, (tx, y + h - bot_tile.get_height()))
        else:
            # normal behavior
            screen.blit(top_tile, (tx, y))
            screen.blit(bot_tile, (tx, y + h - bot_tile.get_height()))

        tx += top_tile.get_width()


    # 3) left & right edges
    ty = y + sch
    while ty < y + h - sch:
        edge_tile  = rng.choice([edge1_s, edge2_s])
        left_tile  = edge_tile
        right_tile = pygame.transform.flip(edge_tile, True, False)
        screen.blit(left_tile,  (x,            ty))
        screen.blit(right_tile, (x + w - edge_tile.get_width(), ty))
        ty += edge_tile.get_height()

    # 4) vertical hub border at hub_border_offset
    edge_h = edge1_s.get_height()
    tc_h   = tcorner_s.get_height()
    half_w = tcorner_s.get_width() // 2
    # tile between T-corners
    yv = tc_h // 2 + edge_h // 2
    bottom_limit = sh - (tc_h // 2 + edge_h // 2)
    while yv < bottom_limit:
        edge_tile = rng.choice([edge1_s, edge2_s])
        screen.blit(edge_tile, (hub_border_offset - edge_tile.get_width()//2, yv))
        yv += edge_tile.get_height()
    # top T-corner (flipped vertically)
    screen.blit(pygame.transform.flip(tcorner_s, False, True),
                (hub_border_offset - half_w, edge_h//2))
    # bottom T-corner
    screen.blit(tcorner_s,
                (hub_border_offset - half_w, sh - tc_h - edge_h//2))

    right_x = sw - avatar_border_offset

    if page not in ("calendar", "settings", "social"):
        # y position of that border
        y_horiz = hotbar_border_offset

        # rotate & mirror your T-corners so their “stem” points down
        left_tc  = pygame.transform.rotate(tcorner_s,  -90)
        right_tc = pygame.transform.flip(left_tc, True, False)

        # compute the start and end X so you don’t overlap vertical hub or go past the main rect
        # the main rect is at x, width w → its right edge is at x + w
        start_x = hub_border_offset + left_tc.get_width() // 2
        end_x   = x + w - right_tc.get_width() // 2 - right_tc.get_width() // 2 - edge_h/2

        # draw left T-corner, centered on hub_border_offset
        screen.blit(
            left_tc,
            (hub_border_offset + (edge_h/4),
             y_horiz - left_tc.get_height() // 2)
        )

        # draw right T-corner, centered at rect’s right minus half-width
        screen.blit(
            right_tc,
            (x + w - right_tc.get_width() // 2 - right_tc.get_width() // 2 - edge_h/2,
             y_horiz - right_tc.get_height() // 2)
        )

        # now tile your horizontal edges (rotated from vertical)
        def horiz(t): return pygame.transform.rotate(t, -90)
        tx = start_x
        while tx < end_x:
            tile = rng.choice([edge1_s, edge2_s])
            ht = horiz(tile)
            screen.blit(
                ht,
                (tx,
                 y_horiz - ht.get_height() // 2)
            )
            tx += ht.get_width()

        if page in "":  #avatar border    ("input_spoons", "input_tasks", "manage_tasks"):
            # 5a-2) vertical slice at 150px from the right
            y_start = tc_h//2 + edge_h//2              # same “hub” top
            y_end   = hotbar_border_offset - edge_h//2
            yv3 = y_start
            while yv3 < y_end:
                edge_tile = rng.choice([edge1_s, edge2_s])
                screen.blit(
                    edge_tile,
                    (right_x + edge_tile.get_width()//2 + 3, yv3)
                )
                yv3 += edge_tile.get_height()

                # top T-corner (flipped vertically)
            screen.blit(pygame.transform.flip(tcorner_s, False, True),
                        (right_x, edge_h//2))
            # bottom T-corner
            screen.blit(tcorner_s,
                        (right_x, hub_border_offset - edge_h//4 - edge_h//2 + 3))
        
    if page in ("input_tasks"):
        right_x = sw - 250
        # Align with the same top/bottom bounds as hub border
        y_start2 = hotbar_border_offset + edge_h // 2          # starts below inventory border
        y_end2   = sh - (tc_h + edge_h // 2)                  # stop where hub border stops

        yv4 = y_start2
        while yv4 < y_end2:
            edge_tile = rng.choice([edge1_s, edge2_s])
            screen.blit(edge_tile, (right_x + edge_tile.get_width() // 2 + 3, yv4))
            yv4 += edge_tile.get_height()

        # --- Proper T-corners ---
        # Top (stem down)
        top_tc = pygame.transform.flip(tcorner_s, False, True)
        screen.blit(top_tc, (right_x, hotbar_border_offset + edge_h//4))

        # Bottom (stem up)
        bottom_y = y_end2
        screen.blit(tcorner_s, (right_x, bottom_y))


    if page == "calendar":
        left_border = 390
        right_border = 626

        # ── draw the horizontal “edge” border between them ──
        left_x  = left_border + calendar_s.get_width()
        right_x = right_border - 6
        # center tiles on the bottom of the calendar corners
        def horiz(tile): 
            return pygame.transform.rotate(tile, -90)
        tx = left_x
        while tx < right_x:
            bot_tile  = pygame.transform.rotate(edge_tile,  90)
            tile = rng.choice([pygame.transform.rotate(edge1_s,  180), pygame.transform.rotate(edge2_s,  180)])
            ht   = horiz(tile)
            # vertically center on the bottom edge of calendar_s
            y = calendar_s.get_height() - ht.get_height() // 2 - 18
            screen.blit(ht, (tx, y))
            tx += ht.get_width()
        
        calendar_s_right = pygame.transform.flip(calendar_s, True,  False)
        screen.blit(calendar_s, (left_border, -9))
        screen.blit(calendar_s_right, (right_border, -9))

    if page == "":  #inventory
        left_x = inventory_border_offset
        # y start just below inventory border
        y_start2 = hotbar_border_offset + edge_h//2
        # y end matches hub bottom
        y_end2   = sh - (tc_h//2 + edge_h//2)
        yv4      = y_start2
        while yv4 < y_end2 - 30:
            edge_tile = rng.choice([edge1_s,edge2_s])
            screen.blit(edge_tile,(left_x+edge_tile.get_width()//2 + 3,yv4))
            yv4 += edge_tile.get_height()
        # top T-corner (stem pointing down) at inventory border
        top_tc = pygame.transform.flip(tcorner_s,False,True)
        screen.blit(top_tc,(left_x,hotbar_border_offset + edge_h//4))
        # bottom T-corner at hub bottom
        screen.blit(tcorner_s,(left_x,sh-tc_h-edge_h//2))