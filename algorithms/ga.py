import time
import sys,os
import copy
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import multiprocessing
from multiprocessing.connection import Connection
from collections import deque,defaultdict

import numpy as np

from problem import Blozorx, State, Action

POPULATION_SIZE = 100
MUTATION_RATE = 0.1
INIT_MOVE = 5
INCREASED_MOVE = 5
INCREASED_MOVE_EVERY_EPOCH = 5
MAX_GEN = 500
GENES = [action[0] for action in Action.get_action_set()]

class Individual:
    def __init__(self, chromosome):
        self.chromosome = chromosome
        
    def survive(self, problem:Blozorx, init_state: State):
        state = copy.deepcopy(init_state)
        for gene in self.chromosome:
            action = Action.decode_action(gene)
            problem.do_action_if_possible(state, action, inplace=True)
            if state.is_goal_state():
                break
    
        self.fitness = Individual.fitness_function(problem, state)
        self.is_win = state.is_goal_state()


    def increase_move(self, size):
        self.chromosome += ''.join(np.random.choice(GENES) for _ in range(size))

    def mutate(self, mutation_rate):
        chromosome = list(self.chromosome)
        for i in range(len(chromosome)):
            if np.random.random() < mutation_rate:
                chromosome[i] = np.random.choice(GENES)
        self.chromosome = ''.join(chromosome)

    @classmethod
    def create(cls):
        global GENES,INIT_MOVE
        chromosome = ''.join(np.random.choice(GENES) for _ in range(INIT_MOVE))
        return cls(chromosome)

    @staticmethod
    def fitness_function(problem:Blozorx, state:State):
        if state.is_standing_state():
            loss = abs(state.cur[0] - problem.init_state.goal[0]) + abs(state.cur[1] - problem.init_state.goal[1])
        else:
            loss = abs((state.cur[0] + state.cur[2])/2 - problem.init_state.goal[0]) \
                + abs((state.cur[1] + state.cur[3])/2 - problem.init_state.goal[1])
        
        return 1/(loss+1e-6)

    @staticmethod
    def crossover(parent1,parent2):
        cross_i = np.random.randint(0,len(parent1.chromosome))
        child1 = Individual(parent1.chromosome[:cross_i] + parent2.chromosome[cross_i:])
        child2 = Individual(parent2.chromosome[:cross_i] + parent1.chromosome[cross_i:])
        return child1,child2



class GenericAlgorithm:
    def __init__(self, population_size = POPULATION_SIZE, mutation_rate = MUTATION_RATE, increased_move = INCREASED_MOVE, increased_move_every_epoch = INCREASED_MOVE_EVERY_EPOCH):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.increased_move = INCREASED_MOVE
        self.increased_move_every_epoch = INCREASED_MOVE_EVERY_EPOCH

    def _initialize(self):
        self.population = []
        for _ in range(self.population_size):
            individual = Individual.create()
            self.population.append(individual)

    def _calc_fitness(self):
        population_fitness = []
        for individual in self.population:
            individual.survive(self.problem, self.init_state)
            population_fitness.append(
                individual.fitness)
        return population_fitness


    def __call__(self, problem:Blozorx, state:State = None, sender: Connection = None, max_gen = MAX_GEN, show_logs = False):
        # return generation_num, path, exe_time (s)
        start_time_s = time.time()
        self.problem = problem
        self.init_state = state if state is not None else self.problem.init_state

        def _return(generation_num, path=None, is_done=False, fitness = 0, length=None):
            nonlocal sender,start_time_s,problem

            # optimal path
            if path is not None:
                _state = copy.deepcopy(self.init_state)
                optimal_path = ''
                for coded_action in path:
                    action = Action.decode_action(coded_action)
                    can_do,_ = problem.do_action_if_possible(_state, action, inplace=True) 
                    if can_do:
                        optimal_path += coded_action
                    if _state.is_goal_state():
                        break
                path = optimal_path

            if sender is not None:
                return_dict = {
                    'solution_cost': generation_num,
                    'path': path,
                    'time': time.time() - start_time_s,
                    'msg': f'Generation: {generation_num} - Length: {length} - Fitness: {fitness:.3f}',
                    'is_done': is_done
                }
                try:
                    sender.send(return_dict)
                except:
                    pass 
            else:
                return generation_num,path,time.time() - start_time_s

        # init population
        self._initialize()
        for generation_num in range(max_gen):
            # increase self.increased_move every self.increased_move_every_epoch
            if generation_num % self.increased_move_every_epoch == 1:
                for individual in self.population:
                    individual.increase_move(self.increased_move)

            # calc fitness
            population_fitness = self._calc_fitness()
            fitness_individual = self.population[np.argmax(population_fitness)]
            highest_fitness = max(population_fitness)

            # check if reached goal state
            for individual in self.population:
                if individual.is_win:
                    return _return(generation_num, path=individual.chromosome, is_done=True)

            # show log
            if show_logs:
                print(f'Generation: {generation_num} - Length: {len(self.population[0].chromosome)} - Fitness: {highest_fitness}')
            _return(generation_num, length=len(self.population[0].chromosome) ,fitness=highest_fitness)

            # probability that the individual should be selected as parent
            parent_probs = np.exp(population_fitness)
            parent_probs /= parent_probs.sum()
            # parent_probs = [fitness/sum(population_fitness) for fitness in population_fitness]
            
            new_population = [] 
            for _ in range(0,self.population_size,2):
                # natural selection
                parent1,parent2 = np.random.choice(self.population, size=2, p=parent_probs, replace=False)

                # produce offsprings
                child1,child2 = Individual.crossover(parent1,parent2)

                # mutate offsprings
                child1.mutate(self.mutation_rate)
                child2.mutate(self.mutation_rate)

                new_population.extend([child1,child2])

            self.population = new_population

        return _return(max_gen,None,True)

generic_algorithm = GenericAlgorithm()

if __name__ == '__main__':
    generation_num, path, exe_time = GenericAlgorithm()(Blozorx(30),show_logs=True)
    print(generation_num)
    print(path)
    print(exe_time)

    problem = Blozorx(2)
    i = Individual(path)
    i.survive(problem, problem.init_state)
    print(i.is_win)