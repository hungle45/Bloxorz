import math
import sys

import pygame
import pygame_menu

# Global Variables
CURRENT_STATE = 'MENU'

# Global Constants
DARK_BLUE = (16, 109, 191)
LIGHT_BLUE = (33, 150, 243)
FPS = 60
NUMBER_OF_LEVELS = 33
LEVEL_PER_ROW = 10
COLOR_BACKGROUND = DARK_BLUE
H_SIZE = 650  # Height of window size
W_SIZE = 880  # Width of window size
CUSTOME_THEME = pygame_menu.Theme(
    background_color=(255, 255, 255),
    selection_color=LIGHT_BLUE,
    title_background_color=LIGHT_BLUE,
    title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_ADAPTIVE,
    title_font=pygame_menu.font.FONT_OPEN_SANS,
    title_font_antialias=True,
    title_font_color =(255,255,255),
    title_font_size=48,
    widget_font=pygame_menu.font.FONT_OPEN_SANS,
    widget_font_size=32,
    widget_margin=(0,8),
    widget_cursor=pygame_menu.locals.CURSOR_HAND,)


# Init pygame
pygame.init()

# Game clock
clock = pygame.time.Clock()

# Create window
surface = pygame.display.set_mode((W_SIZE,H_SIZE))


# -----------------------------------------------------------------------------
# Free play menu
def free_map_chosen_level(level):
    print(level)

def free_map_level_chosen_btn_effect(is_select,widget,menu):
    if is_select:
        widget.set_font(font_size=32,color='white',
                    font=pygame_menu.font.FONT_OPEN_SANS_BOLD,
                    background_color=DARK_BLUE,readonly_color=LIGHT_BLUE,
                    readonly_selected_color='white',selected_color='red',)
    else:
        widget.set_font(font_size=32,color='white',
                    font=pygame_menu.font.FONT_OPEN_SANS_BOLD,
                    background_color=LIGHT_BLUE,readonly_color=LIGHT_BLUE,
                    readonly_selected_color='white',selected_color='red',)


free_play_menu = pygame_menu.Menu('Bloxorz', W_SIZE, H_SIZE,
                                onclose=None,
                                theme=CUSTOME_THEME,
                                mouse_motion_selection=True)

free_play_menu.add.label('LEVELS',font_size=40)

# create level table structure
for r_id in range(math.ceil(NUMBER_OF_LEVELS/LEVEL_PER_ROW)):
    f = free_play_menu.add.frame_h( W_SIZE, 60, margin=(0,0))

    for level_id in range(r_id*LEVEL_PER_ROW,
    min((r_id+1)*LEVEL_PER_ROW,NUMBER_OF_LEVELS)):
        btn = free_play_menu.add.button(f' {level_id+1:02d} ',
                                        free_map_chosen_level,
                                        level_id)
        btn.set_margin(0, 0)
        btn.set_padding((4,8))
        btn.set_selection_effect(pygame_menu.widgets.NoneSelection())
        btn.set_selection_callback(free_map_level_chosen_btn_effect)

        f.pack(btn,align='align-center')

free_play_menu.add.button('BACK', pygame_menu.events.BACK,font_size=24).translate(300,50)


# -----------------------------------------------------------------------------
# Algorithm menu
algorithm_select_menu = pygame_menu.Menu('Bloxorz', W_SIZE, H_SIZE,
                                onclose=None,
                                theme=CUSTOME_THEME,
                                mouse_motion_selection=True)

algorithm_select_menu.add.label('ALGORITHM SELECTION',font_size=40)
algorithm_select_menu.add.button('BACK', pygame_menu.events.BACK)



# -----------------------------------------------------------------------------
# Play menu
play_menu = pygame_menu.Menu('Bloxorz', W_SIZE, H_SIZE,
                            onclose=None,
                            theme=CUSTOME_THEME,
                            mouse_motion_selection=True)

play_menu.add.button('FREE PLAY', free_play_menu)
play_menu.add.button('ALGORITHM', algorithm_select_menu)
play_menu.add.button('BACK', pygame_menu.events.BACK)


# -----------------------------------------------------------------------------
# About menu
about_menu = pygame_menu.Menu('Bloxorz', W_SIZE, H_SIZE,
                        onclose=None,
                        theme=CUSTOME_THEME,
                        mouse_motion_selection=True)

about_menu.add.label('ABOUT',font_size=40)
about_menu.add.button('BACK', pygame_menu.events.BACK)


# -----------------------------------------------------------------------------
# Main menu

menu = pygame_menu.Menu('Bloxorz', W_SIZE, H_SIZE,
                        onclose=None,
                        theme=CUSTOME_THEME,
                        mouse_motion_selection=True,)

menu.add.button('PLAY GAME', play_menu)
menu.add.button('ABOUT', about_menu)
menu.add.button('QUIT', pygame_menu.events.EXIT)


# -----------------------------------------------------------------------------
# Main loop
if __name__ == '__main__':
    while True:
        # tick clock
        clock.tick(FPS)

        surface.fill(COLOR_BACKGROUND)

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if menu.is_enabled():
            menu.update(events)
            menu.draw(surface)
        
        pygame.display.update()