# Game UI: https://play.google.com/store/apps/details?id=air.com.biocode.BloxorzHD

import pygame
import copy

from problem import Action,Blozorx,State

AVAILABLE_COLOR = (255, 255, 255)
BLOCK_COLOR = (255,20,60)
UNCONTROLLED_BLOCK_COLOR = (179,14,42)
GOAL_COLOR = (50,205,50)
BUTTON_COLOR = (105,105,105)
FLEXIBLE_CELL_COLOR = (150,150,150)
FRAGILE_CELL_COLOR = (242, 183, 5)
GAME_COLOR_BACKGROUND = (0,0,139)


class Game:
    def __init__(self, surface, W_HEIGHT_SIZE, W_WIDTH_SIZE, level_id):
        self.surface = surface
        self.W_HEIGHT_SIZE = W_HEIGHT_SIZE
        self.W_WIDTH_SIZE  = W_WIDTH_SIZE
        self.CENTER_X = W_WIDTH_SIZE / 2
        self.CENTER_Y = W_HEIGHT_SIZE / 2

        self.problem = Blozorx(level_id)
        self.state = copy.deepcopy(self.problem.init_state)

        # drawing
        self.square_size = min(50, 700//max(self.problem.level.size_x,self.problem.level.size_y))
        self.starting_x = self.CENTER_X - self.problem.level.size_x / 2 * self.square_size
        self.starting_y = self.CENTER_Y - self.problem.level.size_y / 2 * self.square_size
        self.ending_x   = self.CENTER_X + self.problem.level.size_x / 2 * self.square_size
        self.ending_y   = self.CENTER_Y + self.problem.level.size_y / 2 * self.square_size
        
        self.FONT = pygame.font.Font(None, 50)

        self.moves = 0
        self.over = False # whether game is end
        self.ESC  = False

    def process_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if not self.over and event.key == pygame.K_LEFT:
                    can_do,_ = self.problem.do_action_if_possible(self.state, Action.LEFT, True)
                    if can_do:
                        self.moves += 1
                elif not self.over and event.key == pygame.K_RIGHT:
                    can_do,_ = self.problem.do_action_if_possible(self.state, Action.RIGHT, True)
                    if can_do:
                        self.moves += 1
                elif not self.over and event.key == pygame.K_UP:
                    can_do,_ = self.problem.do_action_if_possible(self.state, Action.UP, True)
                    if can_do:
                        self.moves += 1
                elif not self.over and event.key == pygame.K_DOWN:
                    can_do,_ = self.problem.do_action_if_possible(self.state, Action.DOWN, True)
                    if can_do:
                        self.moves += 1

                elif not self.over and event.key == pygame.K_SPACE:
                    can_do,_ = self.problem.do_action_if_possible(self.state, Action.SWITCH, True)
                    if can_do:
                        self.moves += 1

                elif event.key == pygame.K_ESCAPE:
                    self.ESC = True

    def _draw_sqr_cell(self, position, size, color):
        pygame.draw.rect(
            self.surface,color,
            (*position,size,size)
        )

    def _draw_x_btn_cell(self, position, size, cell_color, btn_color=BUTTON_COLOR):
        self._draw_sqr_cell(position,size,cell_color)
        cx = position[0]+size/2
        cy = position[1]+size/2
        btn_size = size*0.5*0.7
        pygame.draw.line(self.surface,btn_color,(cx-btn_size,cy-btn_size),(cx+btn_size,cy+btn_size),int(size*0.2))
        pygame.draw.line(self.surface,btn_color,(cx+btn_size,cy-btn_size),(cx-btn_size,cy+btn_size),int(size*0.2))


    def _draw_o_btn_cell(self, position, size, cell_color=AVAILABLE_COLOR, btn_color=BUTTON_COLOR):
        self._draw_sqr_cell(position,size,cell_color)
        cx = position[0]+size/2
        cy = position[1]+size/2
        pygame.draw.circle(self.surface,btn_color,(cx,cy),size*0.5*0.8)
        
    def _draw_splited_btn_cell(self, position, size, cell_color, btn_color=BUTTON_COLOR):
        self._draw_sqr_cell(position,size,cell_color)
        cx = position[0]+size/2
        cy = position[1]+size/2
        width = size*0.2
        height = size*0.7
        pygame.draw.line(self.surface,btn_color,(cx-width,cy-height/2),(cx-width,cy+height/2),int(width))
        pygame.draw.line(self.surface,btn_color,(cx+width,cy-height/2),(cx+width,cy+height/2),int(width))


    def _draw_map(self):
        for x in range(self.problem.level.size_x):
            for y in range(self.problem.level.size_y):
                start_x = self.starting_x+1+x*self.square_size
                start_y = self.starting_y+1+y*self.square_size

                if self.state.board_state[y,x]: # is available
                    cell_type = self.problem.board[y,x]

                    if cell_type == Blozorx.CELL_TYPE_INT_MAP['normal']:
                        self._draw_sqr_cell(position=(start_x,start_y),
                            size=self.square_size-1,color=AVAILABLE_COLOR)

                    elif cell_type == Blozorx.CELL_TYPE_INT_MAP['x_btn']:
                        self._draw_x_btn_cell(position=(start_x,start_y),
                            size=self.square_size-1,cell_color=AVAILABLE_COLOR)

                    elif cell_type == Blozorx.CELL_TYPE_INT_MAP['o_btn']:
                        self._draw_o_btn_cell(position=(start_x,start_y),
                            size=self.square_size-1,cell_color=AVAILABLE_COLOR)

                    elif cell_type == Blozorx.CELL_TYPE_INT_MAP['split_btn']:
                        self._draw_splited_btn_cell(position=(start_x,start_y),
                            size=self.square_size-1,cell_color=AVAILABLE_COLOR)

                    elif cell_type == Blozorx.CELL_TYPE_INT_MAP['flexible']:
                        self._draw_sqr_cell(position=(start_x,start_y),
                            size=self.square_size-1,color=FLEXIBLE_CELL_COLOR)

                    elif cell_type == Blozorx.CELL_TYPE_INT_MAP['fragile']:
                        self._draw_sqr_cell(position=(start_x,start_y),
                            size=self.square_size-1,color=FRAGILE_CELL_COLOR)


    def _draw_goal(self):
        start_x = self.starting_x+1+self.state.goal[1]*self.square_size
        start_y = self.starting_y+1+self.state.goal[0]*self.square_size
        self._draw_sqr_cell(
            position=(start_x,start_y),
            size=self.square_size-1,
            color=GOAL_COLOR)

    def _draw_block(self):
        if self.state.is_standing_state():
            x = self.starting_x+1+self.state.cur[1]*self.square_size
            y = self.starting_y+1+self.state.cur[0]*self.square_size
            self._draw_sqr_cell(position=(x,y),size=self.square_size-1,color=BLOCK_COLOR)
        else:
            x0 = self.starting_x+1+self.state.cur[1]*self.square_size
            y0 = self.starting_y+1+self.state.cur[0]*self.square_size
            x1 = self.starting_x+1+self.state.cur[3]*self.square_size
            y1 = self.starting_y+1+self.state.cur[2]*self.square_size
            self._draw_sqr_cell(position=(x0,y0),size=self.square_size-1,color=BLOCK_COLOR)
            self._draw_sqr_cell(position=(x1,y1),size=self.square_size-1,color=BLOCK_COLOR)
            
            if self.state.is_lying_state():
                self._draw_sqr_cell(position=(x1,y1),size=self.square_size-1,color=BLOCK_COLOR)
                self._draw_sqr_cell(position=((x0+x1)/2,(y0+y1)/2),size=self.square_size-1,color=BLOCK_COLOR)
            else: # splited state
                self._draw_sqr_cell(position=(x1,y1),size=self.square_size-1,color=UNCONTROLLED_BLOCK_COLOR)

    def draw(self):
        self.surface.fill(GAME_COLOR_BACKGROUND)
        self._draw_map()
        self._draw_goal()
        self._draw_block()

    def process_end(self):
        if self.state.is_goal_state():
            self.over = True
            msg = f'Win at {self.moves} moves. Press ESC to go back.'
        else:
            msg = f'Moves: {self.moves:05d}'

        text = self.FONT.render(msg, 230, (255, 255, 255))
        text_rect = text.get_rect(center=(self.W_WIDTH_SIZE/2, self.W_HEIGHT_SIZE - 35))
        self.surface.blit(text, text_rect)

    def process(self, events):
        self.process_input(events)
        self.draw()
        self.process_end()

    def should_quit(self):
        return self.ESC
