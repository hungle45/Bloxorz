from level import Level
import numpy as np
import copy

class Action:
    LEFT  = 'LEFT'
    RIGHT = 'RIGHT'
    UP    = 'UP'
    DOWN  = 'DOWN'
    SWITCH = 'SWITCH'

    @staticmethod
    def is_opposite_action(a1: str, a2):
        if a1 == Action.DOWN:
            return a2 == Action.UP
        if a1 == Action.UP:
            return a2 == Action.DOWN
        if a1 == Action.LEFT:
            return a2 == Action.RIGHT
        if a1 == Action.RIGHT:
            return a2 == Action.LEFT
        if a1 == Action.SWITCH:
            return a2 == Action.SWITCH
        return False

    @staticmethod
    def get_action_set():
        return [Action.UP,Action.DOWN,Action.LEFT,Action.RIGHT,Action.SWITCH]

    @staticmethod
    def decode_action(coded_action):
        for action in Action.get_action_set():
            if action[0] == coded_action:
                return action


class State:
    def __init__(self, cur:list, goal: list, board_state: dict):
        self.cur = copy.copy(cur)
        self.goal = copy.copy(goal)
        self.board_state = copy.copy(board_state)

    def is_standing_state(self):
        return len(self.cur) == 2

    def is_plited_state(self):
        # if splited, 2-first number in self.cur is the position of the current controlled block
        return len(self.cur) == 4 \
            and Blozorx.manhattan_distance(self.cur[:2], self.cur[2:]) != 1
        
    def is_lying_state(self):
        return not self.is_standing_state() and not self.is_plited_state()

    def is_goal_state(self):
        return self.is_standing_state() \
            and self.cur == self.goal

    def is_cell_available(self,x,y):
        return (0 <= x < self.board_state.shape[0])\
            and (0 <= y < self.board_state.shape[1])\
            and self.board_state[x,y]

    def __eq__(self, other):
        return np.array_equal(self.board_state,other.board_state) \
            and self.cur == other.cur


class Blozorx:
    TRIGGER_TYPE_INT_MAP = {
        'none'  : 'none',
        'hide'  : 'hide',
        'unhide': 'unhide',
        'toggle': 'toggle'
    }

    CELL_TYPE_INT_MAP = {
        'normal'     : 0,
        'fragile'    : 1,
        'flexible'   : 2,
        'x_btn'      : 3,
        'o_btn'      : 4,
        'split_btn'  : 5,
    }

    def __init__(self, level_id):
        self.load_level(level_id)

    def load_level(self,level_id):
        self.level = Level(level_id)

        # board's cell: (cell_type)
        self.board = np.zeros(self.level.board.shape, dtype='int')

        self.btn_target_map = {}

        for x,y in self.level.fragile_cells:
            self.board[x,y] = self.CELL_TYPE_INT_MAP['fragile']

        for x,y,target_list in self.level.x_btn_list:
            self.board[x,y] = self.CELL_TYPE_INT_MAP['x_btn']
            for tx,ty,_ in target_list:
                self.board[tx,ty] = self.CELL_TYPE_INT_MAP['flexible']
            self.btn_target_map[(x,y)] = target_list

        for x,y,target_list in self.level.o_btn_list:
            self.board[x,y] = self.CELL_TYPE_INT_MAP['o_btn']
            for tx,ty,_ in target_list:
                self.board[tx,ty] = self.CELL_TYPE_INT_MAP['flexible']
            self.btn_target_map[(x,y)] = target_list

        for x,y,target_list in self.level.split_btn_list:
            self.board[x,y] = self.CELL_TYPE_INT_MAP['split_btn']
            self.btn_target_map[(x,y)] = target_list

        self.init_state = State(cur = self.level.start,
                                goal = self.level.goal,
                                board_state = self.level.board)
    
    def get_possible_actions(self, state:State):
        possile_actions = []

        if state.is_standing_state():
            x,y = state.cur
            if state.is_cell_available(x-2,y) and state.is_cell_available(x-1,y):
                possile_actions.append(Action.UP)
            if state.is_cell_available(x+1,y) and state.is_cell_available(x+2,y):
                possile_actions.append(Action.DOWN)
            if state.is_cell_available(x,y-2) and state.is_cell_available(x,y-1):
                possile_actions.append(Action.LEFT)
            if state.is_cell_available(x,y+1) and state.is_cell_available(x,y+2):
                possile_actions.append(Action.RIGHT)

        elif state.is_lying_state():        
            x0,y0,x1,y1 = state.cur
            # lying on row
            if x0 == x1:
                if state.is_cell_available(x0-1,y0) and state.is_cell_available(x1-1,y1):
                    possile_actions.append(Action.UP)
                if state.is_cell_available(x0+1,y0) and state.is_cell_available(x1+1,y1):
                    possile_actions.append(Action.DOWN)
                if state.is_cell_available(x0,y0-1) and self.board[x0,y0-1] != self.CELL_TYPE_INT_MAP['fragile']:
                    possile_actions.append(Action.LEFT)
                if state.is_cell_available(x0,y1+1) and self.board[x0,y1+1] != self.CELL_TYPE_INT_MAP['fragile']:
                    possile_actions.append(Action.RIGHT)
            else:
                if state.is_cell_available(x0-1,y0) and self.board[x0-1,y0] != self.CELL_TYPE_INT_MAP['fragile']:
                    possile_actions.append(Action.UP)
                if state.is_cell_available(x1+1,y0) and self.board[x1+1,y0] != self.CELL_TYPE_INT_MAP['fragile']:
                    possile_actions.append(Action.DOWN)
                if state.is_cell_available(x0,y0-1) and state.is_cell_available(x1,y1-1):
                    possile_actions.append(Action.LEFT)
                if state.is_cell_available(x0,y0+1) and state.is_cell_available(x1,y1+1):
                    possile_actions.append(Action.RIGHT)

        else:  # block is splited
            x,y,_,_ = state.cur
            possile_actions.append(Action.SWITCH)
            if state.is_cell_available(x-1,y):
                possile_actions.append(Action.UP)
            if state.is_cell_available(x+1,y):
                possile_actions.append(Action.DOWN)
            if state.is_cell_available(x,y-1):
                possile_actions.append(Action.LEFT)
            if state.is_cell_available(x,y+1):
                possile_actions.append(Action.RIGHT)
            
        # print(possile_actions)
        # possile_actions = [Action.UP,Action.DOWN,Action.LEFT,Action.RIGHT,Action.SWITCH]
        return possile_actions

    def _move_block(self, state:State, action):
        if state.is_standing_state(): 
            x,y = state.cur
            if action == Action.UP:
                state.cur = [x-2,y,x-1,y]
            elif action == Action.DOWN:
                state.cur = [x+1,y,x+2,y]
            elif action == Action.LEFT:
                state.cur = [x,y-2,x,y-1]
            elif action == Action.RIGHT:
                state.cur = [x,y+1,x,y+2]
        elif state.is_lying_state():        
            x0,y0,x1,y1 = state.cur
            # lying on row
            if x0 == x1:
                if action == Action.UP:
                    state.cur = [x0-1,y0,x1-1,y1]
                elif action == Action.DOWN:
                    state.cur = [x0+1,y0,x1+1,y1]
                elif action == Action.LEFT:
                    state.cur = [x0,y0-1]
                elif action == Action.RIGHT:
                    state.cur = [x0,y1+1]
            else:
                if action == Action.UP:
                    state.cur = [x0-1,y0]
                elif action == Action.DOWN:
                    state.cur = [x1+1,y0]
                elif action == Action.LEFT:
                    state.cur = [x0,y0-1,x1,y1-1]
                elif action == Action.RIGHT:
                    state.cur = [x0,y0+1,x1,y1+1]
        # block is splited
        else:  
            x0,y0,x1,y1 = state.cur

            if action == Action.UP:
                state.cur = [x0-1,y0,x1,y1]
            elif action == Action.DOWN:
                state.cur = [x0+1,y0,x1,y1]
            elif action == Action.LEFT:
                state.cur = [x0,y0-1,x1,y1]
            elif action == Action.RIGHT:
                state.cur = [x0,y0+1,x1,y1]
            
            if not state.is_plited_state():
                x0,y0,x1,y1 = state.cur
                state.cur = [min(x0,x1),min(y0,y1),max(x0,x1),max(y0,y1)]
                

    def _trigger_o_btn_if_possible(self, x, y, state:State):
        if self.board[x,y] != self.CELL_TYPE_INT_MAP['o_btn']: return
        for tx,ty,trigger_type in self.btn_target_map[(x,y)]:
            if trigger_type == self.TRIGGER_TYPE_INT_MAP['hide']:
                state.board_state[tx,ty] = False
            elif trigger_type == self.TRIGGER_TYPE_INT_MAP['unhide']:
                state.board_state[tx,ty] = True
            elif trigger_type == self.TRIGGER_TYPE_INT_MAP['toggle']:
                state.board_state[tx,ty] ^= True
        
    def _trigger_x_btn_if_possible(self, x, y, state:State):
        if self.board[x,y] != self.CELL_TYPE_INT_MAP['x_btn']: return

        for tx,ty,trigger_type in self.btn_target_map[(x,y)]:
            if trigger_type == self.TRIGGER_TYPE_INT_MAP['hide']:
                state.board_state[tx,ty] = False
            elif trigger_type == self.TRIGGER_TYPE_INT_MAP['unhide']:
                state.board_state[tx,ty] = True
            elif trigger_type == self.TRIGGER_TYPE_INT_MAP['toggle']:
                state.board_state[tx,ty] ^= True

    def _trigger_split_btn_if_possible(self, x, y, state:State):
        if self.board[x,y] != self.CELL_TYPE_INT_MAP['split_btn']: return
        state.cur = self.btn_target_map[(x,y)][0] + self.btn_target_map[(x,y)][1]

    def _trigger_button(self, state):
        if state.is_standing_state():
            x,y = state.cur
            self._trigger_o_btn_if_possible(x, y, state)
            self._trigger_x_btn_if_possible(x, y, state)
            self._trigger_split_btn_if_possible(x, y, state)
        elif state.is_lying_state():
            x0,y0,x1,y1 = state.cur
            self._trigger_o_btn_if_possible(x0, y0, state)
            self._trigger_o_btn_if_possible(x1, y1, state)
        else: # split state
            x,y,_,_ = state.cur
            self._trigger_o_btn_if_possible(x, y, state)

    def do_action(self, state:State, action, inplace=False):
        if not inplace:
            state = copy.deepcopy(state)

        if action == Action.SWITCH:
            if state.is_plited_state():
                state.cur = state.cur[2:]+state.cur[:2]
        else:
            is_split_state = state.is_plited_state()
            self._move_block(state, action)
            if not is_split_state or state.is_plited_state():
                self._trigger_button(state)

        if not inplace:
            return state
    
    def do_action_if_possible(self, state:State, action, inplace=False):
        if action in self.get_possible_actions(state):
            return True,self.do_action(state, action, inplace)
        return False,None

    @staticmethod
    def manhattan_distance(x,y):
        return abs(x[0]-y[0]) + abs(x[1]-y[1])


if __name__ == '__main__':
    # p1 = Blozorx(2)
    # p2 = Blozorx(2)
    # print(p1.do_action(p1.init_state,'UP',inplace=False) == p2.init_state)
    print(Action.is_opposite_action(Action.UP, Action.UP))