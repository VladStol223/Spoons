from config import *

from drawing_functions.draw_rounded_button import draw_rounded_button
from drawing_functions.draw_spoons import draw_spoons
from datetime import datetime

import pygame

def draw_manage_tasks_hub(screen, spoons,
                            homework_tasks_list, chores_tasks_list, work_tasks_list, misc_tasks_list,
                            complete_tasks_hub_folder_color, icon_image, spoon_name_input,
                            folder_one, folder_two, folder_three, folder_four, folder_five, folder_six):
    global hub_buttons_showing
    draw_rounded_button(screen,hub_toggle,LIGHT_GRAY,BLACK,0,2)# type: ignore
    pygame.draw.rect(screen, BLACK, hub_menu1)# type: ignore
    pygame.draw.rect(screen, BLACK, hub_menu2)# type: ignore
    pygame.draw.rect(screen, BLACK, hub_menu3)# type: ignore

    for task in homework_tasks_list:
        try:
            task_date = task[4]  # Original due date
            days_left = (task_date - datetime.now()).days
            task[3] = days_left + 1  # Update the 'days' field
        except Exception:
            pass

    for task in chores_tasks_list:
        try:
            task_date = task[4]
            days_left = (task_date - datetime.now()).days
            task[3] = days_left + 1
        except Exception:
            pass

    for task in work_tasks_list:
        try:
            task_date = task[4]
            days_left = (task_date - datetime.now()).days
            task[3] = days_left + 1
        except Exception:
            pass

    for task in misc_tasks_list:
        try:
            task_date = task[4]
            days_left = (task_date - datetime.now()).days
            task[3] = days_left + 1
        except Exception:
            pass


    homework_tasks_list.sort(key=lambda task: (task[3]))
    homework_tasks_list.sort(key=lambda task: (task[2]), reverse = True)
    chores_tasks_list.sort(key=lambda task: (task[3]))
    chores_tasks_list.sort(key=lambda task: (task[2]), reverse = True)
    work_tasks_list.sort(key=lambda task: (task[3]))
    work_tasks_list.sort(key=lambda task: (task[2]), reverse = True)
    misc_tasks_list.sort(key=lambda task: (task[3]))
    misc_tasks_list.sort(key=lambda task: (task[2]), reverse = True)

    draw_spoons(screen,spoons, icon_image, spoon_name_input)

    #Calculate Spoons Needed and number of tasks left incomplete
    homework_spoons = 0
    homework_tasks = 0
    chores_spoons = 0
    chores_tasks = 0
    work_spoons = 0
    work_tasks = 0
    misc_spoons = 0
    misc_tasks = 0
    for i, (task, spoons_needed, done, days, date, start_time, end_time) in enumerate(homework_tasks_list):
        if done == "❌":
            homework_spoons += spoons_needed
            homework_tasks += 1
    for i, (task, spoons_needed, done, days, date, start_time, end_time) in enumerate(chores_tasks_list):
        if done == "❌":
            chores_spoons += spoons_needed
            chores_tasks += 1
    for i, (task, spoons_needed, done, days, date, start_time, end_time) in enumerate(work_tasks_list):
        if done == "❌":
            work_spoons += spoons_needed
            work_tasks += 1
    for i, (task, spoons_needed, done, days, date, start_time, end_time) in enumerate(misc_tasks_list):
        if done == "❌":
            misc_spoons += spoons_needed
            misc_tasks += 1

    #Draw the Folder Buttons and Text
    draw_rounded_button(screen,manage_homework_tasks,complete_tasks_hub_folder_color if homework_tasks_list else LIGHT_GRAY, BLACK, 15)# type: ignore
    homework = font.render(f"{folder_one}:", True, BLACK)# type: ignore
    text_width, text_height = homework.get_size()
    screen.blit(homework, (25 + ((400-text_width)/2),110))
    homework_info = font.render(f"{homework_spoons} spoons needed for {homework_tasks} tasks", True, BLACK)# type: ignore
    screen.blit(homework_info, (60,140))

    if homework_tasks_list:
        hover_text = font.render(f"{homework_tasks_list[0][0]}", True, BLACK)# type: ignore
        if homework_tasks_list[0][2] == "❌":
            hover_text_2 = font.render(f"is due in {homework_tasks_list[0][3]} days for {homework_tasks_list[0][1]} spoons", True, BLACK)# type: ignore
        else:
            hover_text_2 = font.render(f"is Complete. Great Job!", True, BLACK)# type: ignore
        screen.blit(hover_text, (440, 110))
        screen.blit(hover_text_2, (440, 135))

    draw_rounded_button(screen,manage_chores_tasks,complete_tasks_hub_folder_color if chores_tasks_list else LIGHT_GRAY, BLACK, 15)# type: ignore
    chores = font.render(f"{folder_two}:", True, BLACK)# type: ignore
    text_width, text_height = chores.get_size()
    screen.blit(chores, (25 + ((400-text_width)/2),210))
    chores_info = font.render(f"{chores_spoons} spoons needed for {chores_tasks} tasks", True, BLACK)# type: ignore
    screen.blit(chores_info, (60,240))

    if chores_tasks_list:
        hover_text = font.render(f"{chores_tasks_list[0][0]}", True, BLACK)# type: ignore
        if chores_tasks_list[0][2] == "❌":
            hover_text_2 = font.render(f"is due in {chores_tasks_list[0][3]} days for {chores_tasks_list[0][1]} spoons", True, BLACK)# type: ignore
        else:
            hover_text_2 = font.render(f"is Complete. Great Job!", True, BLACK)# type: ignore
        screen.blit(hover_text, (440, 210))
        screen.blit(hover_text_2, (440, 235))

    draw_rounded_button(screen,manage_work_tasks,complete_tasks_hub_folder_color if work_tasks_list else LIGHT_GRAY, BLACK, 15)# type: ignore
    work = font.render(f"{folder_three}:", True, BLACK)# type: ignore
    text_width, text_height = work.get_size()
    screen.blit(work, (25 + ((400-text_width)/2),310))
    work_info = font.render(f"{work_spoons} spoons needed for {work_tasks} tasks", True, BLACK)# type: ignore
    screen.blit(work_info, (60,340))

    if work_tasks_list:
        hover_text = font.render(f"{work_tasks_list[0][0]}", True, BLACK)# type: ignore
        if work_tasks_list[0][2] == "❌":
            hover_text_2 = font.render(f"is due in {work_tasks_list[0][3]} days for {work_tasks_list[0][1]} spoons", True, BLACK)# type: ignore
        else:
            hover_text_2 = font.render(f"is Complete. Great Job!", True, BLACK)# type: ignore
        screen.blit(hover_text, (440, 310))
        screen.blit(hover_text_2, (440, 335))

    draw_rounded_button(screen,manage_misc_tasks,complete_tasks_hub_folder_color if misc_tasks_list else LIGHT_GRAY, BLACK, 15)# type: ignore
    misc = font.render(f"{folder_four}:", True, BLACK)# type: ignore
    text_width, text_height = misc.get_size()
    screen.blit(misc, (25 + ((400-text_width)/2),410))
    misc_info = font.render(f"{misc_spoons} spoons needed for {misc_tasks} tasks", True, BLACK)# type: ignore
    screen.blit(misc_info, (60,440))

    if misc_tasks_list:
        hover_text = font.render(f"{misc_tasks_list[0][0]}", True, BLACK)# type: ignore
        if misc_tasks_list[0][2] == "❌":
            hover_text_2 = font.render(f"is due in {misc_tasks_list[0][3]} days for {misc_tasks_list[0][1]} spoons", True, BLACK)# type: ignore
        else:
            hover_text_2 = font.render(f"is Complete. Great Job!", True, BLACK)# type: ignore
        screen.blit(hover_text, (440, 410))
        screen.blit(hover_text_2, (440, 435))