from math import inf
import math
import numpy as np


# TODO: Return True if A dominates B based on the objective member variables of both objects.
#       If attempting the YELLOW deliverable, your code must be able to gracefully handle
#       any number of objectives, i.e., don't hardcode an assumption that there are 2 objectives.
def dominates(A, B):
    # HINT: We strongly recommend use of the built-in functions any() and all()

    objectives_a_b = list(zip(A.objectives, B.objectives))
    not_worse = all([a_i >= b_i for a_i, b_i in objectives_a_b])
    better = any([a_i > b_i for a_i, b_i in objectives_a_b])
    
    return True if not_worse and better else False
    

# TODO: Use the dominates function (above) to sort the input population into levels
#       of non-domination, and assign to the level members based on an individual's level.
def nondomination_sort(population):

    # Create a mapping from an individual in the population to a list of individuals that this individual dominates
    domination_map = {i: [] for i in range(len(population))}

    # Create a count of the individuals that dominate an individual
    count_of_domination = {i: 0 for i in range(len(population))}

    # Keep track of the previous front
    prev_front = []

    # Create this domination map
    for i in range(len(population) - 1):
        for j in range(i + 1, len(population)):
            if dominates(population[i], population[j]):
                domination_map[i].append(j)
                count_of_domination[j] += 1
            elif dominates(population[j], population[i]):
                domination_map[j].append(i)
                count_of_domination[i] += 1
        if count_of_domination[i] == 0:
            population[i].level = 1
            prev_front.append(i)

    # Make sure to check if the last individual is dominated as well
    if count_of_domination[len(population) - 1] == 0:
        population[len(population) - 1].level = 1
        prev_front.append(len(population) - 1)

    # Idea is to loop through each individual in the current non dominated front and also loop through the individuals these individuals dominate(dominated individuals)
    # We subtract 1 from the each of these dominated individuals because we are removing the current non dominated individuals,
    # as they are already assigned a level
    current_level = 2
    while prev_front:
        new_front = []
        for non_dominated_individual in prev_front:
            for dominated_indvidual in domination_map[non_dominated_individual]:
                count_of_domination[dominated_indvidual] -= 1
                if count_of_domination[dominated_indvidual] == 0:
                    population[dominated_indvidual].level = current_level
                    new_front.append(dominated_indvidual)
        
        current_level += 1
        prev_front = new_front


# TODO: Calculate the crowding distance from https://ieeexplore.ieee.org/document/996017
#       For each individual in the population, and assign this value to the crowding member variable.
#       Use the inf constant (imported at the top of this file) to represent infinity where appropriate.
# IMPORTANT: Note that crowding should be calculated for each level of nondomination independently.
#            That is, only individuals within the same level should be compared against each other for crowding.
def assign_crowding_distances(population):
    # Don't forget to check for division by zero! Replace any divisions by zero with the inf constant.

    # Find the max level amongst all the individuals
    max_level = max(individual.level for individual in population)

    # Create an array for each level
    non_dominated_levels = [[] for _ in range(max_level)]

    # Add the corresponding individuals to each level
    for individual in population:
        non_dominated_levels[individual.level - 1].append(individual)
        individual.crowding = 0

    # Enumerate over Objective
    for i in range(len(population[0].objectives)):

        # Enumerate over level
        for j in range(max_level):

            # Sort individuals in the level by the current objective
            sorted_level = sorted(non_dominated_levels[j], key=lambda individual: individual.objectives[i])

            # Set the crowding of the min and max individuals for the current objective at the current level each to inf as per the paper
            sorted_level[0].crowding = inf
            sorted_level[-1].crowding = inf

            # Check to see if subtracting the max and min causes it to be 0, and if it is set it to infinity
            denom = sorted_level[-1].objectives[i] - sorted_level[0].objectives[i]
            if denom == 0:
                denom = inf

            for k in range(1, len(sorted_level) - 1):
                numer = sorted_level[k + 1].objectives[i] - sorted_level[k - 1].objectives[i]
                sorted_level[k].crowding += (numer / denom)


# This function is implemented for you. You should not modify it.
# It uses the above functions to assign fitnesses to the population.
def assign_fitnesses(population, crowding, failure_fitness, **kwargs):
    # Assign levels of nondomination.
    nondomination_sort(population)

    # Assign fitnesses.
    max_level = max(map(lambda x:x.level, population))
    for individual in population:
        individual.fitness = max_level + 1 - individual.level

    # Check if we should apply crowding penalties.
    if not crowding:
        for individual in population:
            individual.crowding = 0

    # Apply crowding penalties.
    else:
        assign_crowding_distances(population)
        for individual in population:
            if individual.crowding != inf:
                assert 0 <= individual.crowding <= len(individual.objectives),\
                    f'A crowding distance ({individual.crowding}) was not in the correct range. ' +\
                    'Make sure you are calculating them correctly in assign_crowding_distances.'
                individual.fitness -= 1 - 0.999 * (individual.crowding / len(individual.objectives))




# The remainder of this file is code used to calculate hypervolumes.
# You do not need to read, modify or understand anything below this point.
# Implementation based on https://ieeexplore.ieee.org/document/5766730


def calculate_hypervolume(front, reference_point=None):
    point_set = [individual.objectives for individual in front]
    if reference_point is None:
        # Defaults to (-1)^n, which assumes the minimal possible scores are 0.
        reference_point = [-1] * len(point_set[0])
    return wfg_hypervolume(list(point_set), reference_point, True)


def wfg_hypervolume(pl, reference_point, preprocess=False):
    if preprocess:
        pl_set = {tuple(p) for p in pl}
        pl = list(pl_set)
        if len(pl[0]) >= 4:
            pl.sort(key=lambda x: x[0])

    if len(pl) == 0:
        return 0
    return sum([wfg_exclusive_hypervolume(pl, k, reference_point) for k in range(len(pl))])


def wfg_exclusive_hypervolume(pl, k, reference_point):
    return wfg_inclusive_hypervolume(pl[k], reference_point) - wfg_hypervolume(limit_set(pl, k), reference_point)


def wfg_inclusive_hypervolume(p, reference_point):
    return math.prod([abs(p[j] - reference_point[j]) for j in range(len(p))])


def limit_set(pl, k):
    ql = []
    for i in range(1, len(pl) - k):
        ql.append([min(pl[k][j], pl[k+i][j]) for j in range(len(pl[0]))])
    result = set()
    for i in range(len(ql)):
        interior = False
        for j in range(len(ql)):
            if i != j:
                if all(ql[j][d] >= ql[i][d] for d in range(len(ql[i]))) and any(ql[j][d] > ql[i][d] for d in range(len(ql[i]))):
                    interior = True
                    break
        if not interior:
            result.add(tuple(ql[i]))
    return list(result)
