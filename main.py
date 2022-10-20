import pygame
import pygame_menu
import sys

# Global Variables

# Global Constants
FPS = 60
COLOR_BACKGROUND = [15,125,117]
H_SIZE = 650  # Height of window size
W_SIZE = 880  # Width of window size
CUSTOME_THEME = pygame_menu.Theme(
    background_color=(255, 255, 255),
    selection_color=(20, 136, 219),
    title_background_color=(20, 136, 219),
    title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_ADAPTIVE,
    title_font=pygame_menu.font.FONT_OPEN_SANS,
    title_font_antialias=True,
    title_font_color =(255,255,255),
    title_font_size=48,
    widget_font=pygame_menu.font.FONT_OPEN_SANS,
    widget_font_size=32,
    widget_margin=(0,8)
)


# Init pygame
pygame.init()

# Game clock
clock = pygame.time.Clock()

# Create window
surface = pygame.display.set_mode((W_SIZE,H_SIZE))


# -----------------------------------------------------------------------------
# Free play menu
free_play_menu = pygame_menu.Menu('Bloxorz', W_SIZE, H_SIZE,
                                onclose=None,
                                theme=CUSTOME_THEME,
                                mouse_motion_selection=True)

free_play_menu.add.label('FREE PLAY',font_size=40)
free_play_menu.add.button('BACK', pygame_menu.events.BACK)


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
                        mouse_motion_selection=True)

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