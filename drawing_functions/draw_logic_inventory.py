from config import *
import pygame
from datetime import timedelta
from drawing_functions.draw_rounded_button import draw_rounded_button
from drawing_functions.draw_input_box import draw_input_box

folder_input_box_x = 220
folder_input_box_y = 200

folder_one_name_input_box = pygame.Rect(folder_input_box_x, folder_input_box_y, 140, 40)
folder_two_name_input_box = pygame.Rect(folder_input_box_x + 160, folder_input_box_y, 140, 40)
folder_three_name_input_box = pygame.Rect(folder_input_box_x + 320, folder_input_box_y, 140, 40)
folder_four_name_input_box = pygame.Rect(folder_input_box_x, folder_input_box_y + 50, 140, 40)
folder_five_name_input_box = pygame.Rect(folder_input_box_x + 160, folder_input_box_y + 50, 140, 40)
folder_six_name_input_box = pygame.Rect(folder_input_box_x + 320, folder_input_box_y + 50, 140, 40)

folder_dropdown_rect   = pygame.Rect(folder_input_box_x, 145, 200, 40)
folders_dropdown_open  = False    # new state flag

icons_x = 120

icon_tab_box = pygame.Rect(icons_x, 145, 48, 48)
folder_tab_box = pygame.Rect(icons_x, 215, 48, 48)
theme_tab_box = pygame.Rect(icons_x, 285, 48, 48)
border_tab_box = pygame.Rect(icons_x, 355, 48, 48)
extra_tab_box = pygame.Rect(icons_x, 425, 48, 48)

#themes
aquatic_theme = pygame.Rect(290, 180, 40, 30)
foresty_theme = pygame.Rect(290, 220, 40, 30)
girly_pop_theme = pygame.Rect(290, 260, 40, 30)
vampire_goth_theme = pygame.Rect(290, 300, 40, 30)
sunset_glow_theme = pygame.Rect(290, 340, 40, 30)
#extra themes
light_academia_theme = pygame.Rect(230, 180, 40, 30)
retro_theme = pygame.Rect(230, 220, 40, 30)
minimalist_theme = pygame.Rect(230, 260, 40, 30)
cosmic_theme = pygame.Rect(230, 300, 40, 30)
autumn_harvest_theme = pygame.Rect(230, 340, 40, 30)
tropical_oasis_theme = pygame.Rect(230, 380, 40, 30)
pastel_dreams_theme = pygame.Rect(230, 420, 40, 30)
steampunk_theme = pygame.Rect(230, 460, 40, 30)

#settings page
spoon_name_input_box = pygame.Rect(750, 140, 150, 40)



icon_surfaces = [
    spoon_image,
    battery_image,
    star_image,
    potion_image,
    yourdidit_image,
    mike_image,
    lightningface_image,
    diamond_image,
    starfruit_image,
    strawberry_image,
    terstar_image,
    hcheart_image,
    beer_image,
    drpepper_image,
]

def draw_inventory(
    screen,
    spoon_name_input,
    inventory_tab,
    background_color,
    input_active,
    folder_one,
    folder_two,
    folder_three,
    folder_four,
    folder_five,
    folder_six, folders_dropdown_open
):
    r, g, b = background_color
    darker_background   = (max(r - 40, 0), max(g - 40, 0), max(b - 40, 0))
    light_background    = (min(r + 20, 255), min(g + 20, 255), min(b + 20, 255))
    lighter_background  = (min(r + 40, 255), min(g + 40, 255), min(b + 40, 255))

    # load & scale each icon
    icons_icon    = inventoryIcons['icons']
    scaled_icons  = pygame.transform.scale(icons_icon,   (48, 48))
    icons_folders = inventoryIcons['folders']
    scaled_folders = pygame.transform.scale(icons_folders, (48, 48))
    icons_themes  = inventoryIcons['themes']
    scaled_themes = pygame.transform.scale(icons_themes,  (48, 48))
    icons_borders = inventoryIcons['borders']
    scaled_borders = pygame.transform.scale(icons_borders, (48, 48))
    icons_extras  = inventoryIcons['extras']
    scaled_extras = pygame.transform.scale(icons_extras,  (48, 48))

    # each tab: (name, hit-box, surface)
    tabs = [
        ("Icons",   icon_tab_box,   scaled_icons),
        ("Folders", folder_tab_box, scaled_folders),
        ("Themes",  theme_tab_box,  scaled_themes),
        ("Borders", border_tab_box, scaled_borders),
        ("Extra",   extra_tab_box,  scaled_extras),
    ]

    circle_padding = 5

    square_width = 80

    for i in range(7):
        for j in range(3):
            pygame.draw.rect(screen, lighter_background, (220 + 100 * i, 190 + 100 * j, square_width, square_width))
            pygame.draw.rect(screen, darker_background, (220 + 100 * i, 190 + 100 * j, square_width, square_width), 4)

    for name, rect, surf in tabs:
        center = rect.center
        radius = surf.get_width() // 2 + circle_padding
        is_sel = (inventory_tab == name)

        # draw selection circle if needed
        if is_sel:
            pygame.draw.circle(screen, lighter_background, center, radius)

        # pick tint
        tint = darker_background if is_sel else lighter_background

        # tint the white icon, preserve per-pixel alpha
        icon_t = surf.copy()
        icon_t.fill(tint, special_flags=pygame.BLEND_RGBA_MULT)

        # blit tinted icon
        screen.blit(icon_t, icon_t.get_rect(center=center))


    if inventory_tab == "Icons":
        inventory_icon_buttons.clear()

        draw_input_box(screen, spoon_name_input_box, input_active == "spoon_name", spoon_name_input, LIGHT_GRAY, DARK_SLATE_GRAY, False, background_color, "light", 5)#type: ignore
        icon_prompt = bigger_font.render("ICONS", True, BLACK)# type: ignore
        screen.blit(icon_prompt, (folder_input_box_x, 145))

        icon_name_prompt = font.render("Icon Name:", True, BLACK)# type: ignore
        screen.blit(icon_name_prompt, (spoon_name_input_box.left - icon_name_prompt.get_width() - 5, 145))
        

        icon_width = square_width - 15

        for idx, icon in enumerate(icon_surfaces):
            col = idx % 7
            row = idx // 7
            if row >= 3:
                break

            cell_x = 220 + 100 * col
            cell_y = 190 + 100 * row
            outline = pygame.Rect(cell_x, cell_y, square_width, square_width)

            # store for the click logic
            inventory_icon_buttons.append((outline, icon))

            # draw the button
            draw_rounded_button(
                screen,
                outline,
                lighter_background,
                darker_background, #type: ignore
                1, 2
            )

            # scale & blit the icon
            scaled_icon = pygame.transform.scale(icon, (icon_width, icon_width))
            icon_rect   = scaled_icon.get_rect(center=outline.center)
            screen.blit(scaled_icon, icon_rect)

    elif inventory_tab == "Folders":
        # draw the dropdown header
        header_bg = lighter_background
        header_border = darker_background
        draw_rounded_button(
            screen,
            folder_dropdown_rect,
            header_bg,
            header_border,
            1, 2
        )
        # header text: either placeholder or first folder name
        header_txt = folder_one if folders_dropdown_open else " Select Folder"
        txt_surf = bigger_font.render(header_txt, True, BLACK) #type:ignore
        txt_pos  = (folder_dropdown_rect.x + 10,
                    folder_dropdown_rect.y + (folder_dropdown_rect.height - txt_surf.get_height())//2)
        screen.blit(txt_surf, txt_pos)

        # if open, draw the six input boxes underneath
        if folders_dropdown_open:
            draw_input_box(screen, folder_one_name_input_box, input_active == "folder_one", folder_one, LIGHT_GRAY, DARK_SLATE_GRAY, False, background_color, "light", 5)#type: ignore
            draw_input_box(screen, folder_two_name_input_box, input_active == "folder_two", folder_two, LIGHT_GRAY, DARK_SLATE_GRAY, False, background_color, "light", 5)#type: ignore
            draw_input_box(screen, folder_three_name_input_box, input_active == "folder_three", folder_three, LIGHT_GRAY, DARK_SLATE_GRAY, False, background_color, "light", 5)#type: ignore
            draw_input_box(screen, folder_four_name_input_box, input_active == "folder_four", folder_four, LIGHT_GRAY, DARK_SLATE_GRAY, False, background_color, "light", 5)#type: ignore
            draw_input_box(screen, folder_five_name_input_box, input_active == "folder_five", folder_five, LIGHT_GRAY, DARK_SLATE_GRAY, False, background_color, "light", 5)#type: ignore
            draw_input_box(screen, folder_six_name_input_box, input_active == "folder_six", folder_six, LIGHT_GRAY, DARK_SLATE_GRAY, False, background_color, "light", 5)#type: ignore

    elif inventory_tab == "Themes":
        rename_folders_text = bigger_font.render("THEMES", True, BLACK)# type: ignore
        screen.blit(rename_folders_text, (folder_input_box_x,145))

        draw_rounded_button(screen, aquatic_theme, (0,105,148), BLACK, 18)# type: ignore
        draw_rounded_button(screen, foresty_theme, (85,107,47), BLACK, 18)# type: ignore
        draw_rounded_button(screen, girly_pop_theme, (255,182,193), BLACK, 18)# type: ignore
        draw_rounded_button(screen, vampire_goth_theme, (120,0,0), BLACK, 18)# type: ignore
        draw_rounded_button(screen, sunset_glow_theme, (255,140,0), BLACK, 18)# type: ignore

        draw_rounded_button(screen, light_academia_theme, (245, 240, 230), BLACK, 18)# type: ignore
        draw_rounded_button(screen, retro_theme, (204, 122, 46), BLACK, 18) # type: ignore
        draw_rounded_button(screen, minimalist_theme, (255, 255, 255), BLACK, 18) # type: ignore
        draw_rounded_button(screen, cosmic_theme, (85, 0, 128), BLACK, 18) # type: ignore
        draw_rounded_button(screen, autumn_harvest_theme, (183, 65, 14), BLACK, 18)# type: ignore
        draw_rounded_button(screen, tropical_oasis_theme, (64, 224, 208), BLACK, 18)# type: ignore
        draw_rounded_button(screen, pastel_dreams_theme, (255, 182, 193), BLACK, 18) # type: ignore
        draw_rounded_button(screen, steampunk_theme, (181, 166, 66), BLACK, 18) # type: ignore

    elif inventory_tab == "Borders":
        rename_folders_text = bigger_font.render("BORDERS", True, BLACK)# type: ignore
        screen.blit(rename_folders_text, (folder_input_box_x,145))

        scaledOakWood = pygame.transform.rotate(pygame.transform.scale(oakWoodEdgeOne, (18, 36)), 90)
        screen.blit(scaledOakWood, oakwood_preview_rect.topleft)
        scaledDarkOakWood = pygame.transform.rotate(pygame.transform.scale(darkOakWoodEdgeOne, (18, 36)), 90)
        screen.blit(scaledDarkOakWood, darkoakwood_preview_rect.topleft)
        scaledMetal = pygame.transform.rotate(pygame.transform.scale(metalEdgeOne, (18, 36)), 90)
        screen.blit(scaledMetal,   metal_preview_rect.topleft)


def logic_inventory(event, tool_tips, inventory_tab, spoon_name_input, input_active, icon_image, folder_one, folder_two, folder_three, folder_four, folder_five, folder_six, folders_dropdown_open):
    if event.type == pygame.MOUSEBUTTONDOWN:
        if spoon_name_input_box.collidepoint(event.pos):
            input_active = "spoon_name"
        else:
            input_active = ""
        if inventory_tab == "Folders" and folder_dropdown_rect.collidepoint(event.pos):
            folders_dropdown_open = not folders_dropdown_open
            if folder_one_name_input_box.collidepoint(event.pos):
                input_active = "folder_one"
            elif folder_two_name_input_box.collidepoint(event.pos):
                input_active = "folder_two"
            elif folder_three_name_input_box.collidepoint(event.pos):
                input_active = "folder_three"
            elif folder_four_name_input_box.collidepoint(event.pos):
                input_active = "folder_four"
            elif folder_five_name_input_box.collidepoint(event.pos):
                input_active = "folder_five"
            elif folder_six_name_input_box.collidepoint(event.pos):
                input_active = "folder_six"
            else:
                input_active = ""

        for outline, icon in inventory_icon_buttons:
            if outline.collidepoint(event.pos):
                icon_image = icon
                break

        mx, my = event.pos
        if icon_tab_box.collidepoint(mx, my):
            inventory_tab = "Icons"
        elif folder_tab_box.collidepoint(mx, my):
            inventory_tab = "Folders"
        elif theme_tab_box.collidepoint(mx, my):
            inventory_tab = "Themes"
        elif border_tab_box.collidepoint(mx, my):
            inventory_tab = "Borders"
        elif extra_tab_box.collidepoint(mx, my):
            inventory_tab = "Extras"


    elif event.type == pygame.KEYDOWN:
        if input_active == "spoon_name":
            if event.key == pygame.K_RETURN:
                input_active = False
            elif event.key == pygame.K_BACKSPACE:
                spoon_name_input = spoon_name_input[:-1]
            else:
                # Propose the new text
                new_text = spoon_name_input + event.unicode
                # Measure its width
                text_width, _ = font.size(new_text)
                # Leave 10px padding on each side
                max_width = spoon_name_input_box.width - 10
                if text_width <= max_width:
                    spoon_name_input = new_text

        elif input_active == "folder_one":
            if event.key == pygame.K_BACKSPACE:
                folder_one = folder_one[:-1]
            else:
                folder_one += event.unicode

        elif input_active == "folder_two":
            if event.key == pygame.K_BACKSPACE:
                folder_two = folder_two[:-1]
            else:
                folder_two += event.unicode

        elif input_active == "folder_three":
            if event.key == pygame.K_BACKSPACE:
                folder_three = folder_three[:-1]
            else:
                folder_three += event.unicode

        elif input_active == "folder_four":
            if event.key == pygame.K_BACKSPACE:
                folder_four = folder_four[:-1]
            else:
                folder_four += event.unicode

        elif input_active == "folder_five":
            if event.key == pygame.K_BACKSPACE:
                folder_five = folder_five[:-1]
            else:
                folder_five += event.unicode

        elif input_active == "folder_six":
            if event.key == pygame.K_BACKSPACE:
                folder_six = folder_six[:-1]
            else:
                folder_six += event.unicode

    return inventory_tab, spoon_name_input, input_active, icon_image, folder_one, folder_two, folder_three, folder_four, folder_five, folder_six, folders_dropdown_open