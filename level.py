import json
import numpy as np

class Level:
    def __init__(self, level_id):
        self.level = level_id
        self.load_level(f'./level/{level_id}.json')

    def load_level(self, path_to_level):
        with open(path_to_level,'r') as file:
            json_obj = json.load(file)
        self.board = np.asarray(json_obj.get('map'), dtype=bool)
        self.size_y, self.size_x = self.board.shape
        
        self.start = json_obj.get('start')
        self.goal = json_obj.get('end')

        tmp_board = np.asarray(json_obj.get('map'), dtype=int)
        self.fragile_cells = [(r,c) for r,c in zip(*np.where(tmp_board == 2))]

        self.x_btn_list = json_obj.get('x_btn_list')
        self.o_btn_list = json_obj.get('o_btn_list')
        self.split_btn_list = json_obj.get('split_btn_list')


if __name__ == '__main__':
    level = Level(4)
    print('Level',f'{level.level:02d}')
    print('Start:',level.start)
    print('Goal :',level.goal)
    print('Fragile:',level.fragile_cells)
    print('X Button List:',level.x_btn_list)
    print('O Button List:',level.o_btn_list)    
    print('Split Btton List:',level.split_btn_list)
    print('Map:',level.board)