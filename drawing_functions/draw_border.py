import pygame
import random
from config import *

# === CONFIGURATION ===
base_sizes = {
    "corner":    (12, 12),
    "edge":      (6,  12),
    "connector": (8, 8),
    "t_corner":  (14, 12)
}

scale = 3                # multiplier for pixel-art → screen pixels
hub_border_offset = 100      # px from left edge; adjust as needed
spoons_border_offset = 185  # px up from bottom for input_spoons horizontal border
inventory_border_offset = 120  # px from top edge for inventory page
avatar_border_offset = 250  # px from right edge for input_tasks vertical border

def draw_border(screen, rect, page):
    x, y, w, h = rect
    sw, sh = screen.get_size()

    # deterministic RNG per border
    seed = x + (y << 8) + (w << 16) + (h << 24)
    rng = random.Random(seed)

    # downscale raw assets to base sizes
    bw, bh = base_sizes["corner"]
    corner_base   = pygame.transform.scale(corner,   (bw, bh))
    ew, eh = base_sizes["edge"]
    edge1_base    = pygame.transform.scale(edge_one,  (ew, eh))
    edge2_base    = pygame.transform.scale(edge_two,  (ew, eh))
    cw, ch = base_sizes["connector"]
    conn_base     = pygame.transform.scale(connector, (cw, ch))
    tcw, tch = base_sizes["t_corner"]
    tcorner_base  = pygame.transform.scale(tcorner,  (tcw, tch))

    # scale up by scale
    scw, sch   = bw * scale, bh * scale
    sew, seh   = ew * scale, eh * scale
    scw2, sch2 = cw * scale, ch * scale
    stcw, stch = tcw * scale, tch * scale

    corner_s    = pygame.transform.scale(corner_base,    (scw,  sch))
    edge1_s     = pygame.transform.scale(edge1_base,     (sew,  seh))
    edge2_s     = pygame.transform.scale(edge2_base,     (sew,  seh))
    connector_s = pygame.transform.scale(conn_base,      (scw2, sch2))
    tcorner_s   = pygame.transform.scale(tcorner_base,   (stcw, stch))

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
        screen.blit(top_tile, (tx,           y))
        screen.blit(bot_tile, (tx,           y + h - top_tile.get_height()))
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

    # 5) horizontal hub border if on input_spoons page
    if page == "input_spoons":
        # y position of that border
        y_horiz = sh - spoons_border_offset

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

    if page == "input_tasks" or page == "manage_tasks":
        # y position of that border
        y_horiz = inventory_border_offset

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

        # 5a-2) vertical slice at 150px from the right
        right_x = sw - avatar_border_offset
        y_start = tc_h//2 + edge_h//2              # same “hub” top
        y_end   = inventory_border_offset - edge_h//2
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
        
    if page == "input_tasks":
        # y start just below inventory border
        y_start2 = inventory_border_offset + edge_h//2
        # y end matches hub bottom
        y_end2   = sh - (tc_h//2 + edge_h//2)
        yv4      = y_start2
        while yv4 < y_end2:
            edge_tile = rng.choice([edge1_s,edge2_s])
            screen.blit(edge_tile,(right_x+edge_tile.get_width()//2 + 3,yv4))
            yv4 += edge_tile.get_height()
        # top T-corner (stem pointing down) at inventory border
        top_tc = pygame.transform.flip(tcorner_s,False,True)
        screen.blit(top_tc,(right_x,inventory_border_offset + edge_h//4))
        # bottom T-corner at hub bottom
        screen.blit(tcorner_s,(right_x,sh-tc_h-edge_h//2))
