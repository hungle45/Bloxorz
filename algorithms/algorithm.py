import time
import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import multiprocessing
from multiprocessing.connection import Connection
from collections import deque,defaultdict

import numpy as np

from problem import Blozorx, State
from algorithms.bfs import breadth_first_search
from algorithms.ga import generic_algorithm

class Algorithm:
    ALGORITHM_FUNCTION_MAP = {
        'BFS': breadth_first_search,
        'GA' : generic_algorithm,
    }

    def __init__(self,algorithm):
        self.name = algorithm
        # self.algorithm = getattr(self, self.ALGORITHM_FUNCTION_MAP[algorithm])
        self.algorithm = self.ALGORITHM_FUNCTION_MAP[algorithm]

    def solve(self, problem:Blozorx, state:State = None, sender: Connection = None):
        return self.algorithm(problem,state,sender)

if __name__ == '__main__':
    # BFS
    # with open('results/bfs.txt','w') as f:
    #     for level in range(30):
    #         try:
    #             f.write(f'\n----Level {level+1:02d}----\n')
    #             problem = Blozorx(level+1)
    #             explore_node_num, path, exe_time_s = Algorithm('BFS').solve(problem)
    #             print(f'Level {level+1:02d} {int(exe_time_s*1000)}ms')
    #             if path is not None:
    #                 f.write(f'Explored: {explore_node_num} nodes\n')
    #                 f.write(f'Step num: {len(path)}\n')
    #                 f.write(f'Step : {"-".join(path)}\n')
    #             else:
    #                 f.write(f'NO SOLUTION FOUND!\n')
    #             f.write(f'Time : {int(exe_time_s*1000)}ms\n')
    #         except:
    #             f.write('ERROR!\n')

    # GA
    with open('results/ga.txt','w') as f:
        for level in range(5):
            try:
                f.write(f'\n----Level {level+1:02d}----\n')
                problem = Blozorx(level+1)
                explore_node_num, path, exe_time_s = Algorithm('GA').solve(problem)
                print(f'Level {level+1:02d} {int(exe_time_s*1000)}ms')
                if path is not None:
                    f.write(f'Generation num: {explore_node_num}\n')
                    f.write(f'Step num: {len(path)}\n')
                    f.write(f'Step : {"-".join(path)}\n')
                else:
                    f.write(f'NO SOLUTION FOUND!\n')
                f.write(f'Time : {int(exe_time_s*1000)}ms\n')
            except:
                f.write('ERROR!\n')