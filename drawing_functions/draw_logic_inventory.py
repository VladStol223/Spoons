from config import *
import pygame
from datetime import timedelta
from drawing_functions.draw_rounded_button import draw_rounded_button
from drawing_functions.draw_input_box import draw_input_box

input_box_x = 120

folder_one_name_input_box = pygame.Rect(input_box_x, 200, 140, 40)
folder_two_name_input_box = pygame.Rect(input_box_x, 250, 140, 40)
folder_three_name_input_box = pygame.Rect(input_box_x, 300, 140, 40)
folder_four_name_input_box = pygame.Rect(input_box_x, 350, 140, 40)
folder_five_name_input_box = pygame.Rect(input_box_x, 400, 140, 40)
folder_six_name_input_box = pygame.Rect(input_box_x, 450, 140, 40)

#settings page
spoon_name_input_box = pygame.Rect(400, 200, 100, 40)

def draw_inventory(screen, spoon_name_input, background_color, input_active, folder_one, folder_two, folder_three, folder_four, folder_five, folder_six):

    #Draw Folder renaming:
    rename_folders_text = font.render("Rename Folders:", True, BLACK)# type: ignore
    screen.blit(rename_folders_text, (120,160))

    draw_input_box(screen, folder_one_name_input_box, input_active == "folder_one", folder_one, DARK_SLATE_GRAY, DARK_SLATE_GRAY, False, background_color, "light", 5)#type: ignore
    draw_input_box(screen, folder_two_name_input_box, input_active == "folder_two", folder_two, DARK_SLATE_GRAY, DARK_SLATE_GRAY, False, background_color, "light", 5)#type: ignore
    draw_input_box(screen, folder_three_name_input_box, input_active == "folder_three", folder_three, DARK_SLATE_GRAY, DARK_SLATE_GRAY, False, background_color, "light", 5)#type: ignore
    draw_input_box(screen, folder_four_name_input_box, input_active == "folder_four", folder_four, DARK_SLATE_GRAY, DARK_SLATE_GRAY, False, background_color, "light", 5)#type: ignore
    draw_input_box(screen, folder_five_name_input_box, input_active == "folder_five", folder_five, DARK_SLATE_GRAY, DARK_SLATE_GRAY, False, background_color, "light", 5)#type: ignore
    draw_input_box(screen, folder_six_name_input_box, input_active == "folder_six", folder_six, DARK_SLATE_GRAY, DARK_SLATE_GRAY, False, background_color, "light", 5)#type: ignore

    draw_input_box(screen, spoon_name_input_box, input_active == "spoon_name", spoon_name_input, DARK_SLATE_GRAY, DARK_SLATE_GRAY, False, background_color, "light", 5)#type: ignore
    icon_prompt = font.render("Enter icon name:", True, BLACK)# type: ignore
    screen.blit(icon_prompt, (400, 160))

def logic_inventory(event, tool_tips, spoon_name_input, input_active, icon_image, folder_one, folder_two, folder_three, folder_four, folder_five, folder_six):
    if event.type == pygame.MOUSEBUTTONDOWN:
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

    return spoon_name_input, input_active, icon_image, folder_one, folder_two, folder_three, folder_four, folder_five, folder_six