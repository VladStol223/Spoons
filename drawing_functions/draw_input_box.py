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
        infill=None,
        pullUp = 0,
        fontsize = 0.06
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
    sw, sh = screen.get_size()
    font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(sh * fontsize))

    # 1) Determine border color and font
    if active == "small_font":
        render_font = small_font
        color = inactive_color
    else:
        render_font = font
        color = active_color if active else inactive_color

    # 2) Wrap text automatically for multiline support
    words = str(text).split(" ")
    lines = []
    current_line = ""
    max_width = rect.width - 10  # padding

    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        if render_font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    # 3) Limit to two lines max (for your two-line box)
    lines = lines[:2]

    # 4) Compute y positions to center vertically if single line; top align if two lines
    line_height = render_font.get_height()
    if len(lines) == 1:
        total_text_height = line_height
        start_y = rect.y + (rect.height - total_text_height) // 2
    else:
        total_text_height = line_height * len(lines)
        start_y = rect.y + 5  # top padding for multiline

    # 5) If infill is requested, compute fill color and draw background
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

    # 6) Draw each line
    y = start_y
    for line in lines:
        if centered:
            text_x = rect.x + (rect.width - render_font.size(line)[0]) // 2
        else:
            text_x = rect.x + 5
        screen.blit(render_font.render(line, True, BLACK), (text_x, y)) #type: ignore
        y += line_height + 2

    # 7) Draw border
    pygame.draw.rect(screen, color, rect, 4)
