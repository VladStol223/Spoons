from config import *

from drawing_functions.draw_rounded_button import draw_rounded_button
from drawing_functions.draw_spoons import draw_spoons

import pygame

def draw_remove_tasks_hub(screen, spoons,
                            homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list,
                            remove_tasks_hub_folder_color, icon_image, spoon_name_input,
                            folder_one, folder_two, folder_three, folder_four, folder_five, folder_six):
    global hub_buttons_showing
    draw_rounded_button(screen,hub_toggle,LIGHT_GRAY,BLACK,0,2)# type: ignore
    pygame.draw.rect(screen, BLACK, hub_menu1)# type: ignore
    pygame.draw.rect(screen, BLACK, hub_menu2)# type: ignore
    pygame.draw.rect(screen, BLACK, hub_menu3)# type: ignore

    homework_spoons = 0
    homework_tasks = 0
    chores_spoons = 0
    chores_tasks = 0
    work_spoons = 0
    work_tasks = 0
    misc_spoons = 0
    misc_tasks = 0
    for i, (task, spoons_needed, done, days, date, start_time, end_time) in enumerate(homework_tasks_list):
        homework_spoons += spoons_needed
        homework_tasks += 1
    for i, (task, spoons_needed, done, days, date, start_time, end_time) in enumerate(chores_tasks_list):
        chores_spoons += spoons_needed
        chores_tasks += 1
    for i, (task, spoons_needed, done, days, date, start_time, end_time) in enumerate(work_tasks_list):
        work_spoons += spoons_needed
        work_tasks += 1
    for i, (task, spoons_needed, done, days, date, start_time, end_time) in enumerate(misc_tasks_list):
        misc_spoons += spoons_needed
        misc_tasks += 1

    draw_spoons(screen,spoons, icon_image, spoon_name_input)
    draw_rounded_button(screen,remove_homework_tasks,remove_tasks_hub_folder_color, BLACK, 15)# type: ignore
    homework = font.render(f"{folder_one}:", True, BLACK)# type: ignore
    text_width, text_height = homework.get_size()
    screen.blit(homework, (195 + ((400-text_width)/2),110))
    homework_info = font.render(f"{homework_spoons} spoons needed for {homework_tasks} tasks", True, BLACK)# type: ignore
    screen.blit(homework_info, (235,140))

    draw_rounded_button(screen,remove_chores_tasks,remove_tasks_hub_folder_color, BLACK, 15)# type: ignore
    chores = font.render(f"{folder_two}:", True, BLACK)# type: ignore
    text_width, text_height = chores.get_size()
    screen.blit(chores, (195 + ((400-text_width)/2),210))
    chores_info = font.render(f"{chores_spoons} spoons needed for {chores_tasks} tasks", True, BLACK)# type: ignore
    screen.blit(chores_info, (235,240))

    draw_rounded_button(screen,remove_work_tasks,remove_tasks_hub_folder_color, BLACK, 15)# type: ignore
    work = font.render(f"{folder_three}:", True, BLACK)# type: ignore
    text_width, text_height = work.get_size()
    screen.blit(work, (195 + ((400-text_width)/2),310))
    work_info = font.render(f"{work_spoons} spoons needed for {work_tasks} tasks", True, BLACK)# type: ignore
    screen.blit(work_info, (235,340))

    draw_rounded_button(screen,remove_misc_tasks,remove_tasks_hub_folder_color, BLACK, 15)# type: ignore
    misc = font.render(f"{folder_four}:", True, BLACK)# type: ignore
    text_width, text_height = misc.get_size()
    screen.blit(misc, (195 + ((400-text_width)/2),410))
    misc_info = font.render(f"{misc_spoons} spoons needed for {misc_tasks} tasks", True, BLACK)# type: ignore
    screen.blit(misc_info, (235,440))

    draw_rounded_button(screen,remove_all_tasks_button,remove_tasks_hub_folder_color, BLACK, 15)# type: ignore
    remove_all_tasks_text = font.render("Click Here to Remove All Tasks", True, BLACK)# type: ignore
    screen.blit(remove_all_tasks_text, (210,540))