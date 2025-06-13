from config import *

from drawing_functions.draw_rounded_button import draw_rounded_button
from switch_themes import switch_theme
from drawing_functions.draw_input_box import draw_input_box

import pygame

"""
Summary:
    Draws the settings interface on the given screen, including tool tips toggle, icon selection, and theme options.

Parameters:
    screen (pygame.Surface): The surface on which the settings interface will be drawn.
    tool_tips (bool): Indicates whether tool tips are enabled or disabled.
    spoon_name_input (str): The current input text for the spoon name.

Returns:
    No returns.
"""

#image outlines
spoon_image_outline = pygame.Rect(120,180,35,35)
battery_image_outline = pygame.Rect(170,180,35,35)
star_image_outline = pygame.Rect(120,230,35,35)
potion_image_outline = pygame.Rect(170,230,35,35)
yourdidit_image_outline = pygame.Rect(120,280,35,35)

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


def draw_shop(screen, tool_tips, spoon_name_input, icon_image, input_active, hub_background_color,
                  folder_one, folder_two, folder_three, folder_four, folder_five, folder_six):
    mouse_pos = pygame.mouse.get_pos()
    global hub_buttons_showing

    draw_rounded_button(screen,spoon_image_outline,hub_background_color,GREEN if icon_image == spoon_image else BLACK,2,2)# type: ignore
    screen.blit(spoon_image, spoon_image_outline.topleft)
    draw_rounded_button(screen,battery_image_outline,hub_background_color,GREEN if icon_image == battery_image else BLACK,2,2)# type: ignore
    screen.blit(battery_image, battery_image_outline.topleft)
    draw_rounded_button(screen,star_image_outline,hub_background_color,GREEN if icon_image == star_image else BLACK,2,2)# type: ignore
    screen.blit(star_image, star_image_outline.topleft)
    draw_rounded_button(screen,potion_image_outline,hub_background_color,GREEN if icon_image == potion_image else BLACK,2,2)# type: ignore
    screen.blit(potion_image, potion_image_outline.topleft)
    draw_rounded_button(screen,yourdidit_image_outline,hub_background_color,GREEN if icon_image == yourdidit_image else BLACK,2,2)# type: ignore
    screen.blit(yourdidit_image, yourdidit_image_outline.topleft)

    Theme_text = font.render("Icons:", True, BLACK)# type: ignore
    screen.blit(Theme_text, (120,140))

    Theme_text = font.render("Themes:", True, BLACK)# type: ignore
    screen.blit(Theme_text, (230,140))

    Theme_text = font.render("Borders:", True, BLACK)# type: ignore
    screen.blit(Theme_text, (370,140))

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

    # draw your previews:
    scaledOakWood = pygame.transform.rotate(pygame.transform.scale(oakWoodEdgeOne, (18, 36)), 90)
    screen.blit(scaledOakWood, oakwood_preview_rect.topleft)
    scaledDarkOakWood = pygame.transform.rotate(pygame.transform.scale(darkOakWoodEdgeOne, (18, 36)), 90)
    screen.blit(scaledDarkOakWood, darkoakwood_preview_rect.topleft)
    scaledMetal = pygame.transform.rotate(pygame.transform.scale(metalEdgeOne, (18, 36)), 90)
    screen.blit(scaledMetal,   metal_preview_rect.topleft)

    if aquatic_theme.collidepoint(mouse_pos):
        hover_text = font.render("Aquatic", True, BLACK)# type: ignore
        screen.blit(hover_text, (mouse_pos[0]+40, mouse_pos[1]))
    elif foresty_theme.collidepoint(mouse_pos):
        hover_text = font.render("Foresty", True, BLACK)# type: ignore
        screen.blit(hover_text, (mouse_pos[0]+40, mouse_pos[1]))
    elif girly_pop_theme.collidepoint(mouse_pos):
        hover_text = font.render("Girly Pop", True, BLACK)# type: ignore
        screen.blit(hover_text, (mouse_pos[0]+40, mouse_pos[1]))
    elif vampire_goth_theme.collidepoint(mouse_pos):
        hover_text = font.render("Vampire Goth", True, BLACK)# type: ignore
        screen.blit(hover_text, (mouse_pos[0]+40, mouse_pos[1]))
    elif sunset_glow_theme.collidepoint(mouse_pos):
        hover_text = font.render("Sunset Glow", True, BLACK)# type: ignore
        screen.blit(hover_text, (mouse_pos[0]+40, mouse_pos[1]))
    elif cosmic_theme.collidepoint(mouse_pos):
        hover_text = font.render("Cosmic", True, BLACK)# type: ignore
        screen.blit(hover_text, (mouse_pos[0]+40, mouse_pos[1]))
    elif autumn_harvest_theme.collidepoint(mouse_pos):
        hover_text = font.render("Autumn Harvest", True, BLACK)# type: ignore
        screen.blit(hover_text, (mouse_pos[0]+40, mouse_pos[1]))
    elif tropical_oasis_theme.collidepoint(mouse_pos):
        hover_text = font.render("Tropical Oasis", True, BLACK)# type: ignore
        screen.blit(hover_text, (mouse_pos[0]+40, mouse_pos[1]))
    elif pastel_dreams_theme.collidepoint(mouse_pos):
        hover_text = font.render("Pastel Dreams", True, BLACK)# type: ignore
        screen.blit(hover_text, (mouse_pos[0]+40, mouse_pos[1]))
    elif steampunk_theme.collidepoint(mouse_pos):
        hover_text = font.render("Steampunk", True, BLACK)# type: ignore
        screen.blit(hover_text, (mouse_pos[0]+40, mouse_pos[1]))
    elif light_academia_theme.collidepoint(mouse_pos):
        hover_text = font.render("Light Academia", True, BLACK)# type: ignore
        screen.blit(hover_text, (mouse_pos[0]+40, mouse_pos[1]))
    elif retro_theme.collidepoint(mouse_pos):
        hover_text = font.render("Retro", True, BLACK)# type: ignore
        screen.blit(hover_text, (mouse_pos[0]+40, mouse_pos[1]))
    elif minimalist_theme.collidepoint(mouse_pos):
        hover_text = font.render("Minimalist", True, BLACK)# type: ignore
        screen.blit(hover_text, (mouse_pos[0]+40, mouse_pos[1]))


def logic_shop(event, tool_tips, spoon_name_input, input_active, current_theme, icon_image, folder_one, folder_two, folder_three, folder_four, folder_five, folder_six):
    if event.type == pygame.MOUSEBUTTONDOWN:
        if spoon_image_outline.collidepoint(event.pos):
            icon_image = spoon_image
        elif battery_image_outline.collidepoint(event.pos):
            icon_image = battery_image
        elif star_image_outline.collidepoint(event.pos):
            icon_image = star_image
        elif potion_image_outline.collidepoint(event.pos):
            icon_image = potion_image
        elif yourdidit_image_outline.collidepoint(event.pos):
            icon_image = yourdidit_image

        if aquatic_theme.collidepoint(event.pos):
            try:
                border = set_image('border', 'metal')
                current_theme = switch_theme("aquatic", globals())
            except ValueError as e:
                print(e)
        elif foresty_theme.collidepoint(event.pos):
            try:
                border = set_image('border', 'oakWood')
                current_theme = switch_theme("foresty", globals())
            except ValueError as e:
                print(e)
        elif girly_pop_theme.collidepoint(event.pos):
            try:
                current_theme = switch_theme("girly_pop", globals())
            except ValueError as e:
                print(e)
        elif vampire_goth_theme.collidepoint(event.pos):
            try:
                current_theme = switch_theme("vampire_goth", globals())
            except ValueError as e:
                print(e)
        elif sunset_glow_theme.collidepoint(event.pos):
            try:
                current_theme = switch_theme("sunset_glow", globals())
            except ValueError as e:
                print(e)
        elif cosmic_theme.collidepoint(event.pos):
            try:
                current_theme = switch_theme("cosmic", globals())
            except ValueError as e:
                print(e)
        elif autumn_harvest_theme.collidepoint(event.pos):
            try:
                current_theme = switch_theme("autumn_harvest", globals())
            except ValueError as e:
                print(e)
        elif tropical_oasis_theme.collidepoint(event.pos):
            try:
                current_theme = switch_theme("tropical_oasis", globals())
            except ValueError as e:
                print(e)
        elif pastel_dreams_theme.collidepoint(event.pos):
            try:
                current_theme = switch_theme("pastel_dreams", globals())
            except ValueError as e:
                print(e)
        elif steampunk_theme.collidepoint(event.pos):
            try:
                current_theme = switch_theme("steampunk", globals())
            except ValueError as e:
                print(e)
        elif light_academia_theme.collidepoint(event.pos):
            try:
                current_theme = switch_theme("light_academia", globals())
            except ValueError as e:
                print(e)
        elif retro_theme.collidepoint(event.pos):
            try:
                current_theme = switch_theme("retro", globals())
            except ValueError as e:
                print(e)
        elif minimalist_theme.collidepoint(event.pos):
            try:
                current_theme = switch_theme("minimalist", globals())
            except ValueError as e:
                print(e)

    elif event.type == pygame.KEYDOWN:
        if input_active == "spoon_name":
            if event.key == pygame.K_RETURN:
                input_active = False
            elif event.key == pygame.K_BACKSPACE:
                # Remove the last character from the input
                spoon_name_input = spoon_name_input[:-1]
            else:
                # Add new characters to the input
                spoon_name_input += event.unicode  

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

    return tool_tips, spoon_name_input, input_active, current_theme, icon_image, folder_one, folder_two, folder_three, folder_four, folder_five, folder_six

def logic_change_image(event, border, hubIcons, spoonIcons, restIcons, hotbar, manillaFolder, taskBorder, scrollBar, calendarImages, themeBackgroundsImages, intro, border_name, hubIcons_name, spoonIcons_name, resIcons_name, hotbar_name, manillaFolder_name, taskBorder_name, scrollBar_name, calendarImages_name, themeBackgroundsImages_name, intro_name):
    if event.type == pygame.MOUSEBUTTONDOWN:
        if oakwood_preview_rect.collidepoint(event.pos):
            border, border_name = set_image('border', 'oakWood')
        if darkoakwood_preview_rect.collidepoint(event.pos):
            border, border_name = set_image('border', 'darkOakWood')
        if metal_preview_rect.collidepoint(event.pos):
            border, border_name = set_image('border', 'metal')

    return border, hubIcons, spoonIcons, restIcons, hotbar, manillaFolder, taskBorder, scrollBar, calendarImages, themeBackgroundsImages, intro, border_name, hubIcons_name, spoonIcons_name, resIcons_name, hotbar_name, manillaFolder_name, taskBorder_name, scrollBar_name, calendarImages_name, themeBackgroundsImages_name, intro_name