from config import *
from drawing_functions.draw_rounded_button import draw_rounded_button

import pygame

def draw_complete_tasks_folders(screen, folder, add_tasks_chosen_folder_color, add_tasks_choose_folder_color,
                                folder_one, folder_two, folder_three, folder_four, folder_five, folder_six):
    font = pygame.font.Font(None, 25)
    draw_rounded_button(screen, homework_tasks_big if folder == "homework" else homework_tasks ,add_tasks_chosen_folder_color if folder == "homework" else add_tasks_choose_folder_color, BLACK, 15)# type: ignore
    homework = font.render(folder_one, True, BLACK)# type: ignore
    text_width, text_height = homework.get_size()
    screen.blit(homework, (167 + ((100 - text_width)/2),95))
    draw_rounded_button(screen, chores_tasks_big if folder == "chores" else chores_tasks,add_tasks_chosen_folder_color if folder == "chores" else add_tasks_choose_folder_color, BLACK, 15)# type: ignore
    chores = font.render(folder_two, True, BLACK)# type: ignore
    text_width, text_height = chores.get_size()
    screen.blit(chores, (287 + ((100 - text_width)/2),95))
    draw_rounded_button(screen, work_tasks_big if folder == "work" else work_tasks ,add_tasks_chosen_folder_color if folder == "work" else add_tasks_choose_folder_color, BLACK, 15)# type: ignore
    work = font.render(folder_three, True, BLACK)# type: ignore
    text_width, text_height = work.get_size()
    screen.blit(work, (407 + ((100 - text_width)/2),95))
    draw_rounded_button(screen, misc_tasks_big if folder == "misc" else misc_tasks ,add_tasks_chosen_folder_color if folder == "misc" else add_tasks_choose_folder_color, BLACK, 15)# type: ignore
    misc = font.render(folder_four, True, BLACK)# type: ignore
    text_width, text_height = misc.get_size()
    screen.blit(misc, (527 + ((100 - text_width)/2),95))
    font = pygame.font.Font(None, 36)#