import pygame
from config import font, small_font
from colors import COLORS
for name, value in COLORS.items():
    globals()[name] = value

def adjust_color(color, amount):
    """
    Lighten or darken an RGB color by the given amount.
    Positive amount makes it lighter, negative makes it darker.
    """
    r, g, b = color
    new_r = max(0, min(255, r + amount))
    new_g = max(0, min(255, g + amount))
    new_b = max(0, min(255, b + amount))
    return (new_r, new_g, new_b)

def draw_input_box(
        screen,
        rect,
        active,
        text,
        active_color,
        inactive_color,
        centered=False,
        background_color=None,
        infill=None
    ):
    """
    Draws a text input box with an optional infill color.
    
    Parameters:
        screen (pygame.Surface): Surface to draw on.
        rect (pygame.Rect): Rectangle defining the input box position and size.
        active (bool or str): Whether the box is active (focused). If equal to "small_font",
                              uses small_font for rendering text.
        text (str): The text to display inside the box.
        active_color (tuple): Border color when active.
        inactive_color (tuple): Border color when inactive.
        centered (bool): If True, center the text inside the rect.
        background_color (tuple): Base background color (RGB) used for infill adjustments.
        infill (str): One of {"light", "lighter", "dark", "darker"} indicating how to adjust
                      the background_color for the fill. If None, no fill is drawn.
    """
    # 1) Determine border color and render text
    if active == "small_font":
        text_surface = small_font.render(str(text), True, BLACK)  # type: ignore
        color = inactive_color
    else:
        color = active_color if active else inactive_color
        text_surface = font.render(str(text), True, BLACK)  # type: ignore

    # 2) Compute text position
    if centered:
        text_x = rect.x + (rect.width - text_surface.get_width()) // 2
        text_y = rect.y + 12
    else:
        text_x = rect.x + 5
        text_y = rect.y + 12

    # 3) If infill is requested, compute fill color and draw filled rect
    if infill and background_color is not None:
        if infill == "light":
            fill_color = adjust_color(background_color, 20)
        elif infill == "lighter":
            fill_color = adjust_color(background_color, 40)
        elif infill == "dark":
            fill_color = adjust_color(background_color, -20)
        elif infill == "darker":
            fill_color = adjust_color(background_color, -40)
        else:
            fill_color = None

        if fill_color:
            pygame.draw.rect(screen, fill_color, rect)

    # 4) Blit the text on top of any fill
    screen.blit(text_surface, (text_x, text_y))

    # 5) Draw border around the input box
    pygame.draw.rect(screen, color, rect, 4)
