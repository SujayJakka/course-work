
# selection.py

import random
import copy

# For all the functions here, it's strongly recommended to
# review the documentation for Python's random module:
# https://docs.python.org/3/library/random.html

# Parent selection functions---------------------------------------------------
def uniform_random_selection(population, n, **kwargs):
    # TODO: select n individuals uniform randomly
    return random.choices(population, k=n)


def k_tournament_with_replacement(population, n, k, **kwargs):
    # TODO: perform n k-tournaments with replacement to select n individuals
    parents = []

    for _ in range(n):

        # Contestant Selection without replacement
        contestants = random.sample(population, k)

        best_individual = None
        best_score = float("-inf")

        # Competition
        for individual in contestants:
            if individual.fitness > best_score:
                best_individual = individual
                best_score = individual.fitness

        # Add best individual as parent
        parents.append(best_individual)

    return parents


def fitness_proportionate_selection(population, n, **kwargs):
    # TODO: select n individuals using fitness proportionate selection
    parents = []
    fitness_values = [individual.fitness for individual in population]
    negative_fitness_exists = False
    all_fitness_equal = False
    weights = []
    min_fitness = min(fitness_values)

    if min_fitness < 0:
        negative_fitness_exists = True

    if min_fitness == max(fitness_values):
        all_fitness_equal = True

    if negative_fitness_exists and all_fitness_equal:
        weights = [1] * len(population)
    elif negative_fitness_exists:
        weights = [fitness - min_fitness for fitness in fitness_values]
    else:
        weights = fitness_values

    parents = random.choices(population, weights=weights, k=n)
    return parents


# Survival selection functions-------------------------------------------------
def truncation(population, n, **kwargs):
    # TODO: perform truncation selection to select n individuals

    # Sort the population based off of fitness
    sorted_individuals = sorted(population, key=lambda individual: individual.fitness)
    # Pick the last n individuals(the n individuals with the best fitness score)
    best_n_individuals = sorted_individuals[-n:]
    return best_n_individuals
    

def k_tournament_without_replacement(population, n, k, **kwargs):
    # TODO: perform n k-tournaments without replacement to select n individuals
    # Note: an individual should never be cloned from surviving twice!
    # Also note: be careful if using list.remove(), list.pop(), etc.
    # since this can be EXTREMELY slow on large populations if not handled properly
    # A better alternative to my_list.pop(i) is the following:
    # my_list[i] = my_list[-1]
    # my_list.pop()

    survivors = []
    index_and_individual = [[i, population[i]] for i in range(len(population))]

    for i in range(n):
        
        # Contestant Selection without replacement
        contestants = random.sample(index_and_individual, k)

        best_individual = None
        index_of_best_individual = None
        best_score = float("-inf")

        # Competition
        for index, individual in contestants:
            if individual.fitness > best_score:
                best_individual = individual
                index_of_best_individual = index
                best_score = individual.fitness

        # Add best individual as a survivor
        survivors.append(best_individual)

        # Remove best individual from population
        index_and_individual[index_of_best_individual] = index_and_individual[-1]
        index_and_individual[index_of_best_individual][0] = index_of_best_individual
        index_and_individual.pop()
        
    return survivors



# Yellow deliverable parent selection function---------------------------------
def stochastic_universal_sampling(population, n, **kwargs):
    # Recall that yellow deliverables are required for students in the grad
    # section but bonus for those in the undergrad section.
    # TODO: select n individuals using stochastic universal sampling
    pass