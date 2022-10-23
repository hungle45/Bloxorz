from level import Level
import numpy as np
import copy

class Action:
    LEFT  = 'LEFT'
    RIGHT = 'RIGHT'
    UP    = 'UP'
    DOWN  = 'DOWN'
    SWITCH = 'SWITCH'


class State:
    def __init__(self, cur:list, goal: list, btn_state: dict, board_state: dict):
        self.cur = copy.copy(cur)
        self.goal = copy.copy(goal)
        self.btn_state = copy.copy(btn_state) # remain trigger time, -1 if infinity
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
        try:
            return self.board_state[x,y]
        except:
            pass


class Blozorx:
    TRIGGER_TYPE_INT_MAP = {
        'none'  : 0,
        'hide'  : 1,
        'unhide': 2,
        'toggle': 3
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

        # board's cell: (cell_type, trigger_type)
        self.board = np.zeros((*self.level.board.shape,2), dtype='int')

        self.btn_target_map = {}
        btn_trigger_num = {}

        for x,y in self.level.fragile_cells:
            self.board[x,y,0] = self.CELL_TYPE_INT_MAP['fragile']

        for x,y,trigger_type,trigger_num,target_list in self.level.x_btn_list:
            self.board[x,y,0] = self.CELL_TYPE_INT_MAP['x_btn']
            self.board[x,y,1] = self.TRIGGER_TYPE_INT_MAP[trigger_type]
            for tx,ty in target_list:
                self.board[tx,ty,0] = self.CELL_TYPE_INT_MAP['flexible']
            self.btn_target_map[(x,y)] = target_list
            btn_trigger_num[(x,y)] = trigger_num

        for x,y,trigger_type,trigger_num,target_list in self.level.o_btn_list:
            self.board[x,y,0] = self.CELL_TYPE_INT_MAP['o_btn']
            self.board[x,y,1] = self.TRIGGER_TYPE_INT_MAP[trigger_type]
            for tx,ty in target_list:
                self.board[tx,ty,0] = self.CELL_TYPE_INT_MAP['flexible']
            self.btn_target_map[(x,y)] = target_list
            btn_trigger_num[(x,y)] = trigger_num

        for x,y,trigger_num,target_list in self.level.split_btn_list:
            self.board[x,y,0] = self.CELL_TYPE_INT_MAP['split_btn']
            for tx,ty in target_list:
                self.board[tx,ty,0] = self.CELL_TYPE_INT_MAP['flexible']
            self.btn_target_map[(x,y)] = target_list
            btn_trigger_num[(x,y)] = trigger_num

        self.init_state = State(cur = self.level.start,
                                goal = self.level.goal,
                                btn_state = btn_trigger_num, 
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
                if state.is_cell_available(x0,y0-1) and self.board[x0,y0-1,0] != self.CELL_TYPE_INT_MAP['fragile']:
                    possile_actions.append(Action.LEFT)
                if state.is_cell_available(x0,y1+1) and self.board[x0,y1+1,0] != self.CELL_TYPE_INT_MAP['fragile']:
                    possile_actions.append(Action.RIGHT)
            else:
                if state.is_cell_available(x0-1,y0) and self.board[x0-1,y0,0] != self.CELL_TYPE_INT_MAP['fragile']:
                    possile_actions.append(Action.UP)
                if state.is_cell_available(x1+1,y0) and self.board[x1+1,y0,0] != self.CELL_TYPE_INT_MAP['fragile']:
                    possile_actions.append(Action.DOWN)
                if state.is_cell_available(x0,y0-1) and state.is_cell_available(x1,y1-1):
                    possile_actions.append(Action.LEFT)
                if state.is_cell_available(x0,y0+1) and state.is_cell_available(x1,y1+1):
                    possile_actions.append(Action.RIGHT)

        else:  # block is splited
            x,y,_,_ = state.cur

            if action == Action.UP:
                pass
            if action == Action.DOWN:
                pass
            if action == Action.LEFT:
                pass
            if action == Action.RIGHT:
                pass
            
        # print(possile_actions)
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
            x,y,_,_ = state.cur

            if action == Action.UP:
                pass
            elif action == Action.DOWN:
                pass
            elif action == Action.LEFT:
                pass
            elif action == Action.RIGHT:
                pass

    def _trigger_o_btn_if_possible(self, x, y, state:State):
        if self.board[x,y,0] != self.CELL_TYPE_INT_MAP['o_btn']\
            or state.btn_state[(x,y)] == 0: return

        trigger_type = self.board[x,y,1]
        if trigger_type == self.TRIGGER_TYPE_INT_MAP['hide']:
            for tx,ty in self.btn_target_map[(x,y)]:
                state.board_state[tx,ty] = False
        if trigger_type == self.TRIGGER_TYPE_INT_MAP['unhide']:
            for tx,ty in self.btn_target_map[(x,y)]:
                state.board_state[tx,ty] = True
        if trigger_type == self.TRIGGER_TYPE_INT_MAP['toggle']:
            for tx,ty in self.btn_target_map[(x,y)]:
                state.board_state[tx,ty] = not state.board_state[tx,ty]

        if state.btn_state[(x,y)] != -1:
            state.btn_state[(x,y)] -= 1
    
    def _trigger_x_btn_if_possible(self, x, y, state:State):
        if self.board[x,y,0] != self.CELL_TYPE_INT_MAP['x_btn']\
            or state.btn_state[(x,y)] == 0: return

        trigger_type = self.board[x,y,1]
        if trigger_type == self.TRIGGER_TYPE_INT_MAP['hide']:
            for tx,ty in self.btn_target_map[(x,y)]:
                state.board_state[tx,ty] = False
        if trigger_type == self.TRIGGER_TYPE_INT_MAP['unhide']:
            for tx,ty in self.btn_target_map[(x,y)]:
                state.board_state[tx,ty] = True
        if trigger_type == self.TRIGGER_TYPE_INT_MAP['toggle']:
            for tx,ty in self.btn_target_map[(x,y)]:
                state.board_state[tx,ty] = not state.board_state[tx,ty]

        if state.btn_state[(x,y)] != -1:
            state.btn_state[(x,y)] -= 1


    def _trigger_button(self, state):
        if state.is_standing_state():
            x,y = state.cur
            self._trigger_o_btn_if_possible(x, y, state)
            self._trigger_x_btn_if_possible(x, y, state)
        elif state.is_lying_state():
            x0,y0,x1,y1 = state.cur
            self._trigger_o_btn_if_possible(x0, y0, state)
            self._trigger_o_btn_if_possible(x1, y1, state)
        else:
            pass

    def do_action(self, state:State, action, inplace=False):
        if not inplace:
            state = copy.deepcopy(state)

        if action == Action.SWITCH:
            if state.is_plited_state():
                state.cur = state.cur[2:]+state.cur[:2]
        else:
            self._move_block(state, action)
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
    level = Level(1)
    state = State.load_state_from_level(level)