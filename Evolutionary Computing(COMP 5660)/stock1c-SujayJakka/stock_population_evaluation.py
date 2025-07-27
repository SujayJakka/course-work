
# stock_population_evaluation.py

from cutting_stock.fitness_functions import *

# 1b TODO: Evaluate the population and assign the fitness
# member variable as described in the Assignment 1b notebook
def base_population_evaluation(population, **kwargs):
    # Use base_fitness_function, i.e.,
    # base_fitness_function(individual.genes, **kwargs)

    for linear_genotype in population:
        output = base_fitness_function(linear_genotype.genes, **kwargs)
        linear_genotype.fitness = output["fitness"]


# 1c TODO: Evaluate the population and assign the base_fitness, violations, and fitness
# member variables as described in the constraint satisfaction portion of Assignment 1c
def unconstrained_population_evaluation(population, penalty_coefficient, red=None, **kwargs):
    # Use unconstrained_fitness_function, i.e.,
    # unconstrained_fitness_function(individual.genes, **kwargs)
    if not red:
        # GREEN deliverable logic goes here
        for linear_genotype in population:
            # Evaluate the solution
            output = unconstrained_fitness_function(linear_genotype.genes, **kwargs)

            # Assign member variables based on the evaluation
            linear_genotype.base_fitness = output['base fitness']
            linear_genotype.violations = output['violations']
            linear_genotype.fitness = output['unconstrained fitness'] - linear_genotype.violations * penalty_coefficient

    else:
        # RED deliverable logic goes here
        pass


# 1d TODO: Evaluate the population and assign the objectives
# member variable as described in the multi-objective portion of Assignment 1d
def multiobjective_population_evaluation(population, yellow=None, **kwargs):
    # Use multiobjective_fitness_function, i.e.,
    # multiobjective_fitness_function(individual.genes, **kwargs)
    if not yellow:
        # GREEN deliverable logic goes here
        pass

    else:
        # YELLOW deliverable logic goes here
        pass

