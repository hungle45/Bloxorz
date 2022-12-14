import time
import sys
import multiprocessing
from multiprocessing.connection import Connection
from collections import deque,defaultdict

import pygame
import numpy as np

from problem import Action,Blozorx,State
from game import GameUI
from algorithms import Algorithm

WHITE = (250,250,250)
LIGHT_BLUE = (16, 109, 191)
BLACK = (80,80,80)
GRAY = (150,150,150)
RED = (150,0,0)


class AlgorithmStatsUI:
    SOLUTION_COST_MAP = {
        'BFS': 'Node explored',
        'GA': 'Total generation'
    }

    def __init__(self, surface, W_HEIGHT_SIZE, W_WIDTH_SIZE, level_id, algorithm):
        self.surface = surface
        self.W_HEIGHT_SIZE = W_HEIGHT_SIZE
        self.W_WIDTH_SIZE  = W_WIDTH_SIZE
        self.CENTER_X = W_WIDTH_SIZE / 2
        self.CENTER_Y = W_HEIGHT_SIZE / 2

        self.problem = Blozorx(level_id)
        self.algorithm = Algorithm(algorithm)
        
        self.big_font = pygame.font.Font(None, 50)
        self.medium_font = pygame.font.Font(None, 40)
        self.small_font = pygame.font.Font(None, 30, bold=False)

        self.solution_cost = None
        self.path = None
        self.exe_time_s = None

        self.ESC  = False
        self.show = False

        self.run_algorithm()

    def draw_loading_screen(self, receiver: Connection):
        msg = 'Loading...'
        _fps = 10
        _clock = pygame.time.Clock()
        
        while True:
            for _e in pygame.event.get():
                if _e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if _e.type == pygame.KEYDOWN:
                    if _e.key == pygame.K_ESCAPE:
                        self.ESC = True
                        return
            if receiver.poll():
                return_dict = receiver.recv()
                if return_dict['is_done']:
                    self.solution_cost = return_dict['solution_cost']
                    self.path = return_dict['path']
                    self.exe_time_s = return_dict['time']
                    return
                else:
                    msg = return_dict['msg']

            self.surface.fill(WHITE)
            # Level header
            text = self.big_font.render(f"Level: {self.problem.level.level:02d}", True, LIGHT_BLUE)
            text_rect = text.get_rect(center=(self.W_WIDTH_SIZE/2, 80))
            self.surface.blit(text, text_rect)

            # Algorithm header
            text = self.medium_font.render(f"Algorithm: {self.algorithm.name}", True, LIGHT_BLUE)
            text_rect = text.get_rect(center=(self.W_WIDTH_SIZE/2, 125))
            self.surface.blit(text, text_rect)

            # Algorithm Calculating Status
            text = self.medium_font.render(msg, True, BLACK)
            text_rect = text.get_rect(center=(self.W_WIDTH_SIZE/2, self.W_HEIGHT_SIZE/2))
            self.surface.blit(text, text_rect)

            pygame.display.update()
            _clock.tick(_fps)

    def run_algorithm(self):
        # self.solution_cost, self.path, self.exe_time_s = self.algorithm.solve(self.problem)
        receiver, sender = multiprocessing.Pipe(duplex=False)

        solver = multiprocessing.Process(target=self.algorithm.solve, args=(self.problem,None,sender))
        solver.daemon = True
        solver.start()

        self.draw_loading_screen(receiver)

    def get_solution(self):
        return self.path

    def process_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.run_algorithm()
                elif event.key == pygame.K_s and self.path is not None:
                    self.show = True
                elif event.key == pygame.K_ESCAPE:
                    self.ESC = True

    def draw(self):
        self.surface.fill(WHITE)

        # Level header
        text = self.big_font.render(f"Level: {self.problem.level.level:02d}", True, LIGHT_BLUE)
        text_rect = text.get_rect(center=(self.W_WIDTH_SIZE/2, 80))
        self.surface.blit(text, text_rect)

        # Algorithm header
        text = self.medium_font.render(f"Algorithm: {self.algorithm.name}", True, LIGHT_BLUE)
        text_rect = text.get_rect(center=(self.W_WIDTH_SIZE/2, 125))
        self.surface.blit(text, text_rect)

        # Solution Cost
        if self.solution_cost is not None:
            text = self.medium_font.render(f"{self.SOLUTION_COST_MAP[self.algorithm.name]}: {self.solution_cost}", True, BLACK)
            text_rect = text.get_rect(center=(self.W_WIDTH_SIZE/2, 250))
            self.surface.blit(text, text_rect)
        
        # Time to Solve
        if self.exe_time_s is not None:
            text = self.medium_font.render(f"Time exec: {int(self.exe_time_s*1000)}ms", True, BLACK)
            text_rect = text.get_rect(center=(self.W_WIDTH_SIZE/2, 300))
            self.surface.blit(text, text_rect)

        if self.path is not None:
            # Press N to VIEW NODES EXPLORED.
            text = self.medium_font.render(f"Total step: {len(self.path)}", 230, BLACK)
            text_rect = text.get_rect(center=(self.W_WIDTH_SIZE/2, 350))
            self.surface.blit(text, text_rect)
            # Press S to VIEW SOLUTION.
            text = self.small_font.render("Press S to view solution steps.", True, GRAY)
            text_rect = text.get_rect(center=(self.W_WIDTH_SIZE/2, self.W_HEIGHT_SIZE - 128))
            self.surface.blit(text, text_rect)
        else:
            # NO SOLUTION FOUND
            text = self.small_font.render("NO SOLUTION FOUND!", True, RED)
            text_rect = text.get_rect(center=(self.W_WIDTH_SIZE/2, 350))
            self.surface.blit(text, text_rect)

        # Press R to re run algorithm.
        text = self.small_font.render("Press R to run the algorithm again.", True, GRAY)
        text_rect = text.get_rect(center=(self.W_WIDTH_SIZE/2, self.W_HEIGHT_SIZE - 90))
        self.surface.blit(text, text_rect)

        # Press ESC to go back.
        text = self.small_font.render("Press ESC to go back.", True, GRAY)
        text_rect = text.get_rect(center=(self.W_WIDTH_SIZE/2, self.W_HEIGHT_SIZE - 52))
        self.surface.blit(text, text_rect)

    def process(self, events):
        self.process_input(events)
        self.draw()

    def should_quit(self):
        return self.ESC

    def should_show(self):
        return self.show


class AlgorithmShowUI:
    def __init__(self, surface, W_HEIGHT_SIZE, W_WIDTH_SIZE, level_id, solution, transition_speed_ms):
        self.game = GameUI(surface, W_HEIGHT_SIZE, W_WIDTH_SIZE, level_id)
        self.surface = surface

        self.W_HEIGHT_SIZE = W_HEIGHT_SIZE
        self.W_WIDTH_SIZE  = W_WIDTH_SIZE
        self.CENTER_X = W_WIDTH_SIZE / 2
        self.CENTER_Y = W_HEIGHT_SIZE / 2

        self.transition_speed_ms = transition_speed_ms
        self.timer_ms = 0

        self.FONT = pygame.font.Font(None, 50)

        self.solution = solution
        self.solution_index = -1

        self.ESC = False
        self.PAUSE = False

    def get_next_action(self, deltatime):
        if self.PAUSE:
            return
        if self.solution_index == len(self.solution) - 1:
            return

        self.timer_ms += deltatime
        if self.timer_ms >= self.transition_speed_ms:
            self.timer_ms -= self.transition_speed_ms
            self.solution_index += 1

            coded_action = self.solution[self.solution_index]
            # for action in Action.get_action_set():
            #     if coded_action == action[0]:
            #         return action
            return Action.decode_action(coded_action)


    def process_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.ESC = True
                elif event.key == pygame.K_SPACE:
                    self.PAUSE ^= True

    def draw_pause(self):
        text = self.FONT.render('PAUSE', True, WHITE)
        text_rect = text.get_rect(center=(self.W_WIDTH_SIZE/2, 35))
        self.surface.blit(text, text_rect)
            

    def process(self, events, deltatime):
        self.process_input(events)

        next_action = self.get_next_action(deltatime)
        if next_action is not None:
            self.game.do_action_if_posible(next_action)

        self.game.draw()
        self.game.process_end()

        if self.PAUSE:
            self.draw_pause()

    def should_quit(self):
        return self.ESC



if __name__ == '__main__':
    # with open('results/ga.txt','w') as f:
    with open('results/bfs.txt','w') as f:
        for level in range(30):
            try:
                f.write(f'\n----Level {level+1:02d}----\n')
                problem = Blozorx(level+1)
                # explore_node_num, path, exe_time_s = Algorithm('GA').solve(problem)
                explore_node_num, path, exe_time_s = Algorithm('BFS').solve(problem)
                print(f'Level {level+1:02d} {int(exe_time_s*1000)}ms')
                if path is not None:
                    f.write(f'Explored: {explore_node_num} nodes\n')
                    f.write(f'Step num: {len(path)}\n')
                    f.write(f'Step : {"-".join(path)}\n')
                    f.write(f'Time : {int(exe_time_s*1000)}ms\n')
                else:
                    f.write(f'NO SOLUTION FOUND!\n')
            except:
                f.write('ERROR!\n')