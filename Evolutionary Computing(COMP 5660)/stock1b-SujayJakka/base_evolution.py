
# base_evolution.py

import statistics
import random

class BaseEvolutionPopulation():
    def __init__(self, individual_class, mu, num_children,
                 mutation_rate, parent_selection, survival_selection,
                 problem=dict(), parent_selection_kwargs=dict(),
                 recombination_kwargs=dict(), mutation_kwargs=dict(),
                 survival_selection_kwargs=dict(), **kwargs):
        self.mu = mu
        self.num_children = num_children
        self.mutation_rate = mutation_rate
        self.parent_selection = parent_selection
        self.survival_selection = survival_selection
        self.parent_selection_kwargs = parent_selection_kwargs
        self.recombination_kwargs = recombination_kwargs
        self.mutation_kwargs = mutation_kwargs
        self.survival_selection_kwargs = survival_selection_kwargs

        self.log = []
        self.log.append(f'mu: {self.mu}')
        self.log.append(f'num_children: {self.num_children}')
        self.log.append(f'mutation rate: {self.mutation_rate}')
        self.log.append(f'parent selection: {self.parent_selection.__name__ }')
        self.log.append(f'parent selection kwargs: {self.parent_selection_kwargs}')
        self.log.append(f'survival selection: {self.survival_selection.__name__ }')
        self.log.append(f'survival selection kwargs: {self.survival_selection_kwargs}')
        self.log.append(f'recombination kwargs: {self.recombination_kwargs}')
        self.log.append(f'mutation kwargs: {self.mutation_kwargs}')

        self.population = individual_class.initialization(self.mu, **problem, **kwargs)
        self.evaluations = 0

        self.log.append(f'Initial population size: {len(self.population)}')


    def generate_children(self):
        # Randomly select self.num_children * 2 parents using your selection algorithm
        parents = self.parent_selection(self.population, self.num_children * 2, **self.parent_selection_kwargs)
        random.shuffle(parents)

        children = list()
        mutated_child_count = 0

        # TODO: Get pairs of parents
        # HINT: range(0, len(parents), 2) to iterate two at a time
            
        # TODO: Recombine each pair to generate a child
        # HINT: With parents p1 and p2, get a child with
        #       p1.recombine(p2, **self.recombination_kwargs)
        for i in range(0, len(parents), 2):
            p1, p2 = parents[i], parents[i + 1]
            child = p1.recombine(p2, **self.recombination_kwargs)
            children.append(child)

        # TODO: Mutate each child independently with probability self.mutation_rate.
        #       The probability is independent for each child, meaning you should
        #       randomly decide if each individual child gets mutated. That is,
        #       you shouldn't calculate a precise number of mutations to occur ahead of time.
        #       Record the number of mutated children in mutated_child_count variable.
        # HINT: With a recombined child, get a mutated copy with
        #       child.mutate(**self.mutation_kwargs)
        #       Keep in mind this does not modify child, it returns a new object

        for i in range(len(children)):
            random_prob = random.uniform(0, 1)
            if random_prob <= self.mutation_rate:
                children[i] = children[i].mutate(**self.mutation_kwargs)
                mutated_child_count += 1

        self.log.append(f'Number of children: {len(children)}')
        self.log.append(f'Number of mutations: {mutated_child_count}')

        return children


    def survival(self):
        self.log.append(f'Pre-survival population size: {len(self.population)}')
        self.population = self.survival_selection(self.population, self.mu, **self.survival_selection_kwargs)
        self.log.append(f'Post-survival population size: {len(self.population)}')


    def log_base_stats(self):
        self.log.append(f'Evaluations: {self.evaluations}')
        self.log.append(f'Local best: {max(map(lambda x:x.fitness, self.population))}')
        self.log.append(f'Local mean: {statistics.mean(map(lambda x:x.fitness, self.population))}')


    def log_penalized_stats(self):
        self.log.append(f'Evaluations: {self.evaluations}')
        self.log.append(f'Local best penalized fitness: {max(map(lambda x:x.fitness, self.population))}')
        self.log.append(f'Local mean penalized fitness: {statistics.mean(map(lambda x:x.fitness, self.population))}')
        self.log.append(f'Local best base fitness: {max(map(lambda x:x.base_fitness, self.population))}')
        self.log.append(f'Local mean base fitness: {statistics.mean(map(lambda x:x.base_fitness, self.population))}')
        self.log.append(f'Number of valid solutions: {[x.violations for x in self.population].count(0)}')


    def log_multiobjective_stats(self, front, hypervolume):
        self.log.append(f'Evaluations: {self.evaluations}')
        self.log.append(f'Local best length: {max(map(lambda x:x.objectives[0], self.population))}')
        self.log.append(f'Local mean length: {statistics.mean(map(lambda x:x.objectives[0], self.population))}')
        self.log.append(f'Local best width: {max(map(lambda x:x.objectives[1], self.population))}')
        self.log.append(f'Local mean width: {statistics.mean(map(lambda x:x.objectives[1], self.population))}')
        self.log.append(f'Individuals in the Pareto front: {len(pareto_front)}')
        self.log.append(f'Local Pareto front mean length: {statistics.mean(map(lambda x:x.objectives[0], pareto_front))}')
        self.log.append(f'Local Pareto front mean width: {statistics.mean(map(lambda x:x.objectives[1], pareto_front))}')
        self.log.append(f'Local Pareto front hypervolume: {hypervolume}')
