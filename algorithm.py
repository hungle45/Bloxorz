import pygame
import time
from collections import deque,defaultdict

import numpy as np

from problem import Action,Blozorx,State

class Algorithm:
    ALGORITHM_FUNCTION_MAP = {
        'BFS': 'breadth_first_search',
        'GA' : 'genetic_algorithm',
    }

    def __init__(self,algorithm,level_id):
        self.algorithm = getattr(self, self.ALGORITHM_FUNCTION_MAP[algorithm])

    @staticmethod
    def breadth_first_search(problem:Blozorx, state:State = None):
        # return explore_node_num, path
        start_time = time.time()
        explore_node_num = 0

        if state is None:
            state = problem.init_state
        if state.is_goal_state():
            return 0,'',time.time() - start_time

        q = deque()
        q.append(('',state))
        visited = defaultdict(list)

        def _is_visited(state: State):
            nonlocal visited
            for visited_board in visited[tuple(state.cur)]:
                if np.array_equal(state.board_state,visited_board):
                    return True
            return False

        def _add_visited_state(state: State):
            nonlocal visited
            visited[tuple(state.cur)].append(state.board_state)

        while len(q) > 0:
            path,cur_state = q.popleft()
            explore_node_num += 1

            for action in problem.get_possible_actions(cur_state):
                next_state = problem.do_action(cur_state, action, inplace=False)
                
                if next_state.is_goal_state():
                    return explore_node_num, path+action[0], time.time() - start_time
                if _is_visited(next_state): 
                    continue

                _add_visited_state(next_state)
                q.append((path+action[0],next_state))
        
        return explore_node_num, None, time.time() - start_time


    @staticmethod
    def genetic_algorithm():
        print('GA')

if __name__ == '__main__':
    with open('results/bfs.txt','w') as f:
        for level in range(14):
            problem = Blozorx(level+1)
            explore_node_num, path, exe_time = Algorithm('BFS', 2).algorithm(problem)
            f.write(f'----Level {level+1:02d}----\n')
            f.write(f'Explored: {explore_node_num} nodes\n')
            f.write(f'Step num: {len(path)}\n')
            f.write(f'Step : {"-".join(path)}\n')
            f.write(f'Time : {exe_time:0.3f}s\n\n')
            print(f'Level {level+1:02d} {exe_time:0.3f}s')