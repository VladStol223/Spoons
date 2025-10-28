from config import *
import pygame

# Global list of clickable folder rects
folder_rects = []

def draw_complete_tasks_folders(screen,selected_folder,folder_one,folder_two,folder_three,folder_four,folder_five,folder_six,homework_tasks_list,chores_tasks_list,work_tasks_list,misc_tasks_list,exams_tasks_list,projects_tasks_list, manillaFolder):
    global folder_rects; folder_rects=[]
    # config
    right_offset=0; top_offset=85; vertical_spacing=-24
    scale_factor=1.5
    manilla_folder = manillaFolder['manilla_folder']
    manilla_folder_open = manillaFolder['manilla_folder_open']
    manilla_folder_tab  = manillaFolder['manilla_folder_tab']
    # images from config: body closed/open and separate tab
    base_closed=pygame.transform.scale(manilla_folder,(int(manilla_folder.get_width()*scale_factor),int(manilla_folder.get_height()*scale_factor)))
    base_open=pygame.transform.scale(manilla_folder_open,(int(manilla_folder_open.get_width()*scale_factor),int(manilla_folder_open.get_height()*scale_factor)))
    tab_img=pygame.transform.scale(manilla_folder_tab,(int(manilla_folder_tab.get_width()*scale_factor),int(manilla_folder_tab.get_height()*scale_factor)))
    fw,fh=base_closed.get_size(); tw,th=tab_img.get_size()
    # folder definitions
    folder_list=[("homework",folder_one),("chores",folder_two),("work",folder_three),("misc",folder_four),("exams",folder_five),("projects",folder_six)]
    # draw each
    for i,(key,name) in enumerate(folder_list):
        img=base_open if key==selected_folder else base_closed
        x=screen.get_width()-right_offset-fw; y=top_offset+i*(fh+vertical_spacing)
        # draw tab then body underneath
        screen.blit(tab_img,(x,y))
        screen.blit(img,(x,y+th))
        # text centered on tab
        text_surf=font.render(name,True, BLACK if key == selected_folder else DARK_SLATE_GRAY) #type: ignore
        tx= (x+tw+(fw-tw-text_surf.get_width())//2 - 20) if key ==selected_folder else (x+tw+(fw-tw-text_surf.get_width())//2 - 30)
        ty= (y+th+(fh-th-text_surf.get_height())//2 ) if key ==selected_folder else (y+th+(fh-th-text_surf.get_height())//2 - 10)
        screen.blit(text_surf,(tx,ty))
        # click rect covers tab+body
        folder_rects.append((key,pygame.Rect(x,y,fw,fh+th)))
