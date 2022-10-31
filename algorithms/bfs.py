import time
import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import multiprocessing
from multiprocessing.connection import Connection
from collections import deque,defaultdict

import numpy as np

from problem import Blozorx, State


def breadth_first_search(problem:Blozorx, state:State = None, sender: Connection = None):
    # return explore_node_num, path, exe_time (s)
    start_time_s = time.time()
    explore_node_num = 0
    def _return(explore_node_num,path=None,is_done=False):
        nonlocal sender,start_time_s
        if sender is not None:
            return_dict = {
                'solution_cost': explore_node_num,
                'path': path,
                'time': time.time() - start_time_s,
                'msg': f'Explored Node: {explore_node_num}',
                'is_done': is_done
            }
            try:
                sender.send(return_dict)
            except:
                pass 
        else:
            return explore_node_num,path,time.time() - start_time_s

    if state is None:
        state = problem.init_state
    if state.is_goal_state():
        # return 0,'',time.time()-start_time_s
        return _return(0, '', True)

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
        if explore_node_num % 1000 == 0:
            _return(explore_node_num)

        for action in problem.get_possible_actions(cur_state):
            next_state = problem.do_action(cur_state, action, inplace=False)

            if next_state.is_goal_state():
                # return explore_node_num, path+action[0], time.time() - start_time_s
                return _return(explore_node_num, path+action[0], True)
            if _is_visited(next_state): 
                continue

            _add_visited_state(next_state)
            q.append((path+action[0],next_state))
    
    # return explore_node_num, None, time.time() - start_time_s
    return _return(explore_node_num,None,True)
