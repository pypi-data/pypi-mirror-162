"""
Thingspire AI: Optimization using Genetic Algorithm and cyber objective function  
 Create : 2022. 05. 31.
 Owner: Scotty Kim<scotty@thingspire.com>

 Copyright 2022 thingspire.com, Inc. All rights reserved.
 PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
"""

"""
GA-COF-Optimization
(Genetic Algorithm Adaptive Muation Probability Function with Cyber Objective Function)

@version <tt>Revision: 1.0</tt> 2022. 05. 31.
@author <a href="mailto:scotty@thingspire.com">Scotty Kim</a>

"""
from sklearn.neural_network import MLPRegressor


import random
import numpy as np
import copy

class GeneticCOFOptimization(object):
    
    def __init__(self, blackbox_func, pbounds, cspace=10, optimal_score=None):
        
        assert blackbox_func != None, 'blackbox_func is None'
        assert pbounds != None, 'pbounds is None'
        assert cspace != None, 'cspace is None'
        
        self.fitness = blackbox_func
        self.pbounds = pbounds
        # number of continuous space division
        self.cspace = cspace
        self.SEPARATOR = ' '
        self.all_chromosomes = []
        self.all_scores = []
        self.optimal_score = optimal_score
        self.mutation_probability = 0.5
        self.best_chromosome = None
        self.best_score = None
        self.fitness_call_counter = 0
        self.mode = None
        self.result = None
        

    
    def maximize(self, num_population=20, num_generation=40):
        self.mode = 'max'
        assert num_population != None, 'num_population is None'
        assert num_generation != None, 'num_generation is None'
        
        self.num_population = num_population
        self.num_generation = num_generation
        best_chromosome, best_score = self.run_generations()
        self.best_chromosome = best_chromosome
        self.best_score = best_score
        self.result = {'target': self.best_score, 'params': self.parse_params_array(self.best_chromosome)}
#         print("done", self.best_chromosome)
        
        
    def minimize(self, num_population=20, num_generation=40):
        self.mode = 'min'
        assert num_population != None, 'num_population is None'
        assert num_generation != None, 'num_generation is None'
        
        self.num_population = num_population
        self.num_generation = num_generation
        best_chromosome, best_score = self.run_generations()
        self.best_chromosome = best_chromosome
        self.best_score = best_score
        self.result = {'target': self.best_score, 'params': self.parse_params_array(self.best_chromosome)}

    @property
    def max(self):
        return self.result
    
    @property
    def min(self):
        return self.result
    
    def is_inspected(self, chromosome):
        _exists = False
        if self.exists(self.all_chromosomes, chromosome):
            _exists = True
        return _exists

    def int_to_binary(self, int_value):
        length = 8
        form = '{0:0' + str(length) + 'b}'
        return form.format(int_value)
    
    def binary_to_int(self, binary):
        return int(binary, 2)
    
    def init_chromosome_array(self):
        result = []
        keys = list(self.pbounds.keys())
        for key in keys:
            result.append(random.choice(list(range(self.num_bound(key)))))
        return result
    
    def mutate(self, offspring_array, num_of_mutations):
        num_of_genes = len(offspring_array)
        if num_of_genes <= num_of_mutations:
            num_of_mutations = num_of_genes
        mutation_indices = np.array(random.sample(range(num_of_genes), num_of_mutations))
        
        for mutation_index in mutation_indices:
            gene = offspring_array[mutation_index]
            length = self.num_bound(list(self.pbounds.keys())[mutation_index])
            
            if length < 2:
                continue
            selectable_itmes = list(range(length))
            selectable_itmes.remove(gene)
            mutation = random.choice(selectable_itmes)
            offspring_array[mutation_index] = mutation
        return offspring_array
    
    def not_exists(self, _list, element):
        notexists = False
        try:
            list(_list).index(element)
        except ValueError as e:
            notexists = True
        return notexists
    
    def exists(self, _list, element):
        _exists = True
        try:
            list(_list).index(element)
        except ValueError as e:
            _exists = False
        return _exists
    
    def random_population(self, init=False):
        population = []
        while len(population) < self.num_population:
            chromosome_array = self.init_chromosome_array()
            if self.is_inspected(chromosome_array) == False:
                population.append(chromosome_array)
                if init:
                    self.all_chromosomes.append(chromosome_array)
        return population

    def init_population(self):
        return self.random_population(init=True)
    
    def crossover(self, parent1_array, parent2_array):
        num_of_genes = len(parent1_array)
        num_of_crossover = int(num_of_genes/2)

        crossover_indices = np.sort(random.sample(range(num_of_genes), num_of_crossover))

        offsprint1_array = copy.deepcopy(parent1_array)
        offsprint2_array = copy.deepcopy(parent2_array)
        
        for i in range(num_of_genes):
            if self.exists(crossover_indices, i):
                offsprint1_array[i] = parent2_array[i]
                offsprint2_array[i] = parent1_array[i]
        return offsprint1_array, offsprint2_array
    
    # Parent Selections: Random Selection, Rank Selection, Tournament Selection
    #, Stochastic Universal Sampling(SUS), Roulette Wheel Selection, Fitness Proportionate Selection
    # https://www.tutorialspoint.com/genetic_algorithms/genetic_algorithms_parent_selection.htm
    def selection(self, population, scores):
        # Random Selection
        p1_index, p2_index = random.sample(range(self.num_population), 2)
        return population[p1_index], population[p2_index]
    
    def num_bound(self, key):
        result = None
        bound = self.pbounds[key]
        if type(bound) is tuple:
            from_int = isinstance(bound[0], int)
            to_int = isinstance(bound[1], int)
            if from_int and to_int:
                result = len(list(range(bound[0], bound[1]+1)))
            else:
                result = self.cspace
        else:
            result = len(bound)
        return result
    
    def get_param(self, key, gene_index):
        result = None
        bound = self.pbounds[key]
        if type(bound) is tuple:
            _min = bound[0]
            _max = bound[1]
            from_int = isinstance(bound[0], int)
            to_int = isinstance(bound[1], int)
            if from_int and to_int:
                result = list(range(bound[0], bound[1]+1))[gene_index]
            else:
                param_space_tick = (_max - _min)/self.cspace
                result = _min + param_space_tick*gene_index
#                 print(key, gene_index, param_space_tick, result)
        else:
            result = bound[gene_index]
        return result
        
    def parse_params_array(self, chromosome_array):
        result = []
        keys = list(self.pbounds.keys())
        i = 0
        for gene_index in chromosome_array:
            param = self.get_param(keys[i], gene_index)
            result.append(param)
            i += 1
        params = dict(zip(self.pbounds.keys(), result))
        return params
    
    def run_generation(self, population, scores):
        # Random Selection
        if scores is None :
            scores = []
            local_optimal_score = -90000000 if self.mode == 'max' else 90000000
            for chromosome_array in population:
                params = self.parse_params_array(chromosome_array)
                score = self.fitness(**params)
                self.fitness_call_counter += 1
                self.all_scores.append(score)
                
                local_optimal = local_optimal_score < score if self.mode == 'max' else local_optimal_score >= score
                if local_optimal:
                    #TODO Logger self.update_log(self.counter, score, -1)
                    local_optimal_score = score
                scores.append(score)
        num_of_params = None
        while len(population) < self.num_population*2:
            parent1, parent2 = self.selection(population, scores)
            offspring1, offspring2 = self.crossover(parent1, parent2)
            if num_of_params is None:
                num_of_params = len(parent1)
            if random.random() < self.mutation_probability:
                num_of_mutations = random.choice(list(range(num_of_params)))
                offspring1 = self.mutate(offspring1, num_of_mutations)
            if random.random() < self.mutation_probability:
                num_of_mutations = random.choice(list(range(num_of_params)))
                offspring2 = self.mutate(offspring2, num_of_mutations)
            if self.is_inspected(offspring1) == False:
                population.append(offspring1)
                params = self.parse_params_array(offspring1)
                score = self.fitness(**params)
                self.fitness_call_counter += 1
#                 print("offspring1", offspring1, "score", score)
                scores.append(score)
                self.all_chromosomes.append(offspring1)
                self.all_scores.append(score)
            if self.is_inspected(offspring2) == False:
                population.append(offspring2)
                params = self.parse_params_array(offspring2)
                score = self.fitness(**params)
                self.fitness_call_counter += 1
#                 print("offspring2", offspring2, "score", score)
                scores.append(score)
                self.all_chromosomes.append(offspring2)
                self.all_scores.append(score)

        cadidate_chromosomes, candidate_scores, acc = self.cyber_objective_function(self.all_chromosomes, self.all_scores)
#         print(np.max(candidate_scores), ",", np.max(scores), ",", acc)
        _length = len(cadidate_chromosomes)
        for i in range(_length):
            population.append(cadidate_chromosomes[i])
            scores.append(candidate_scores[i])
        sorted_scores = scores.copy()
        reverse = True if self.mode == 'max' else False
        sorted_scores.sort(reverse=reverse)
       
        next_generation_population = []
        next_generation_scores = []
        for score in sorted_scores:
            next_generation_scores.append(score)
            next_generation_population.append(population[scores.index(score)])
            if len(next_generation_population) == self.num_population:
                break

        return next_generation_population, next_generation_scores

    def cyber_objective_function(self, X, y):
        regr = MLPRegressor(random_state=1, hidden_layer_sizes=(100, 50), max_iter=10000).fit(X, y)
        y_optimal = np.max(y) if self.mode == 'max' else np.min(y)
        acc = regr.score(X, y)
        if acc < 0.9:
            return [], [], acc
        candidates = []
        scores = []
        max_loop = 5000
        cnt = 0
        while len(candidates) < 5:
            random_population = self.random_population()
            
            for chromo in random_population:
                y_hat = regr.predict([chromo])
                is_optimal = y_optimal < y_hat if self.mode == 'max' else y_optimal > y_hat
                if is_optimal and self.is_inspected(chromo) is False:
                    candidates.append(chromo)
                    params = self.parse_params_array(chromo)
                    score = self.fitness(**params)
                    self.fitness_call_counter += 1
                    scores.append(score)
                    self.all_chromosomes.append(chromo)
                    self.all_scores.append(score)
            cnt += len(random_population)
            if cnt > max_loop:
                break
#         print("cof max score", np.max(self.all_score))            
        return candidates, scores, acc

    def get_fitness_call_count(self):
        return self.fitness_call_counter

    def run_generations(self):
        population = self.init_population()
        scores = None 
        best_chromosome = None
        
        best_score = -9000000 if self.mode == 'max' else 9000000
        for i in range(self.num_generation): 
            population, scores = self.run_generation(population, scores)
            optimal_index = np.argmax(scores) if self.mode == 'max' else np.argmin(scores)
            local_optimal_score = scores[optimal_index]
            is_best = best_score < local_optimal_score if self.mode == 'max' else best_score > local_optimal_score
            if is_best:
#                 self.update_log(None, local_max_score, -1)
                best_score = local_optimal_score
                best_chromosome = population[optimal_index]
                if self.optimal_score is not None:
                    is_goal = self.optimal_score <= best_score if self.mode == 'max' else best_score >= self.optimal_score
                    if is_goal:
                        break
        return best_chromosome, best_score
    
