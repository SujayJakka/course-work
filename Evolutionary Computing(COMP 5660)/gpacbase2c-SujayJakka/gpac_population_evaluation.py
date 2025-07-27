
# gpac_population_evaluation.py

from fitness import *


# 2b TODO: Evaluate the population and assign base_fitness, fitness, and log
#          member variables as described in the Assignment 2b notebook.
def base_population_evaluation(population, parsimony_coefficient, experiment, **kwargs):
    if experiment.casefold() == 'green':
        # Evaluate a population of Pac-Man controllers against the default ghost agent.
        # Sample call: score, log = play_GPac(controller, **kwargs)
        pass

    elif experiment.casefold() == 'yellow':
        # YELLOW: Evaluate a population of Pac-Man controllers against the default ghost agent.
        # Apply parsimony pressure as a second objective to be minimized, rather than a penalty.
        # Sample call: score, log = play_GPac(controller, **kwargs)
        pass

    elif experiment.casefold() == 'red1':
        # RED1: Evaluate a population of Pac-Man controllers against the default ghost agent.
        # Use the score vectors to calculate fitness sharing.
        # Sample call: score, log, score_vector = play_GPac(controller, score_vector=True, **kwargs)
        pass

    elif experiment.casefold() == 'red2':
        # RED2: Evaluate a population of Pac-Man controllers against the default ghost agent.
        # Sample call: score, log = play_GPac(controller, **kwargs)
        pass

    elif experiment.casefold() == 'red3':
        # RED3: Evaluate a population where each game has multiple different Pac-Man controllers.
        # You must write your own play_GPac_multicontroller function, and use that.
        pass

    elif experiment.casefold() == 'red4':
        # RED4: Evaluate a population of ghost controllers against the default Pac-Man agent.
        # Sample call: score, log = play_GPac(None, controller, **kwargs)
        pass

    elif experiment.casefold() == 'red5':
        # RED5: Evaluate a population where each game has multiple different ghost controllers.
        # You must write your own play_GPac_multicontroller function, and use that.
        pass


    # This code will strip out unnecessary log member variables, to save your memory.
    # We remove the log from any individual that doesn't have a maximal fitness.
    max_fit = max(individual.fitness for individual in population)
    max_base_fit = max(individual.base_fitness for individual in population)
    for individual in population:
        if individual.fitness != max_fit and individual.base_fitness != max_base_fit:
            del individual.log
            individual.log = None

