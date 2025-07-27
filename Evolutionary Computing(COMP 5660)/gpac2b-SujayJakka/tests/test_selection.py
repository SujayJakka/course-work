
# tests/test_selection.py

from test_utils import *
import random, pytest, copy, os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from selection import *
from snake_eyes import read_config

config = read_config('configs/1b/easy_green_config.txt', globals(), locals())
del config['parent_selection_kwargs']['k']
del config['survival_selection_kwargs']['k']
iterations = 30

class TestUniformRandomParentSelection:
    def test_output_size(self):
        # Returns the correct number of parents
        for _ in range(iterations):
            popsize = random.randrange(50, 500)
            pop = random_pop(popsize, **config['problem'])
            random_fitness(pop)
            outsize = random.randint(1, popsize * 2)
            assert len(uniform_random_selection(pop, outsize,\
                       **config['parent_selection_kwargs'])) == outsize

    def test_is_uniform(self):
        # Selection is approximately uniformly distributed
        popsize = random.randrange(50, 500)
        out_of_bounds = 0
        outsize = popsize * 1000
        expected = outsize / popsize
        min_bound = max(expected / 1.2, 1)
        max_bound = expected * 1.2
        for _ in range(iterations):
            pop = random_pop(popsize, **config['problem'])
            random_fitness(pop)
            counts = {x:0 for x in pop}
            for individual in uniform_random_selection(pop, outsize,\
                                **config['parent_selection_kwargs']):
                counts[individual] += 1
            for count in counts.values():
                if min_bound > count or max_bound < count:
                    out_of_bounds += 1
        assert out_of_bounds <= 1.15 * iterations

    def test_definitely_duplicates(self):
        # Always has duplicates when out > in
        for _ in range(iterations):
            popsize = random.randrange(50, 500)
            pop = random_pop(popsize, **config['problem'])
            random_fitness(pop)
            counts = {x:0 for x in pop}
            outsize = popsize + 1
            for individual in uniform_random_selection(pop, outsize,\
                                **config['parent_selection_kwargs']):
                counts[individual] += 1
            ones = 0
            multiples = 0
            for count in counts.values():
                if count == 1:
                    ones += 1
                elif count >= 2:
                    multiples += 1
            assert ones <= outsize - 1
            assert multiples >= 1

    def test_probably_duplicates(self):
        # Can have duplicates even when out < in
        failures = 0
        for _ in range(iterations):
            popsize = random.randrange(50, 500)
            outsize = popsize - 1
            pop = random_pop(popsize, **config['problem'])
            random_fitness(pop)
            counts = {x:0 for x in pop}
            for individual in uniform_random_selection(pop, outsize,\
                                **config['parent_selection_kwargs']):
                counts[individual] += 1
            failed = True
            for count in counts.values():
                if count > 1:
                    failed = False
                    break
            if failed:
                failures += 1
        assert failures < max(iterations / 10, 2)

    def test_population_unmodified(self):
        # Selection doesn't modify the input population
        for _ in range(5):
            popsize = random.randrange(50, 500)
            pop = random_pop(popsize, **config['problem'])
            random_fitness(pop)
            copies = [copy.deepcopy(x) for x in pop]
            selection = uniform_random_selection(pop, random.randint(1, popsize * 2),\
                                **config['parent_selection_kwargs'])
            for i in range(popsize):
                assert same_object(pop[i], copies[i])

class TestKTournamentWithReplacement:
    def test_output_size(self):
        # Returns the correct number of parents
        for _ in range(iterations):
            popsize = random.randrange(50, 500)
            pop = random_pop(popsize, **config['problem'])
            random_fitness(pop)
            outsize = random.randint(1, popsize * 2)
            k = random.randint(2, popsize)
            assert len(k_tournament_with_replacement(pop, outsize, k=k,\
                                **config['parent_selection_kwargs'])) == outsize
        assert len(k_tournament_with_replacement(pop, outsize, k=popsize,\
                                **config['parent_selection_kwargs'])) == outsize
        assert len(k_tournament_with_replacement(pop, outsize, k=2,\
                                **config['parent_selection_kwargs'])) == outsize

    def test_elitist(self):
        # Never selects any of the worst k-1 individuals
        for _ in range(iterations * 5): # Very prone to false positives
            popsize = random.randrange(10, 100)
            outsize = popsize * 3
            pop = random_pop(popsize, **config['problem'])
            random_fitness(pop)
            k = random.randint(2, popsize-1)
            worst_individuals = set(sorted(pop, key=lambda x:x.fitness)[:k-1])
            out = k_tournament_with_replacement(pop, outsize, k=k,\
                                **config['parent_selection_kwargs'])
            for selected in out:
                assert selected not in worst_individuals

    def test_is_based_on_fitness(self):
        # Individuals with a higher fitness are selected more often
        popsize = random.randrange(10, 100)
        outsize = popsize * 100
        out_of_order = 0
        for _ in range(iterations):
            pop = random_pop(popsize, **config['problem'])
            random_fitness(pop)
            counts = {x:0 for x in pop}
            k = random.randint(2, popsize-1)
            for individual in k_tournament_with_replacement(pop, outsize, k=k,\
                                **config['parent_selection_kwargs']):
                counts[individual] += 1
            ordering = sorted(pop, key=lambda x:x.fitness)
            for i in range(len(ordering) - 1):
                if counts[ordering[i]] > counts[ordering[i + 1]]:
                    out_of_order += 1
        assert out_of_order < popsize * iterations / 10

    def test_definitely_duplicates(self):
        # Always has duplicates when out > in
        for _ in range(iterations):
            popsize = random.randrange(50, 500)
            pop = random_pop(popsize, **config['problem'])
            random_fitness(pop)
            counts = {x:0 for x in pop}
            outsize = popsize + 1
            for individual in k_tournament_with_replacement(pop, outsize, k=2,\
                                **config['parent_selection_kwargs']):
                counts[individual] += 1
            ones = 0
            greater = 0
            for count in counts.values():
                if count == 1:
                    ones += 1
                elif count >= 2:
                    greater += 1
            assert ones <= outsize - 1
            assert greater >= 1

    def test_probably_duplicates(self):
        # Can have duplicates even when out < in
        failures = 0
        for _ in range(iterations):
            popsize = random.randrange(50, 500)
            outsize = popsize - 1
            pop = random_pop(popsize, **config['problem'])
            random_fitness(pop)
            counts = {x:0 for x in pop}
            for individual in k_tournament_with_replacement(pop, outsize, k=2,\
                                **config['parent_selection_kwargs']):
                counts[individual] += 1
            failed = True
            for count in counts.values():
                if count > 1:
                    failed = False
                    break
            if failed:
                failures += 1
        assert failures < max(iterations / 10, 2)

    def test_population_unmodified(self):
        # Selection doesn't modify the input population
        for _ in range(5):
            popsize = random.randrange(50, 500)
            pop = random_pop(popsize, **config['problem'])
            random_fitness(pop)
            copies = [copy.deepcopy(x) for x in pop]
            selection = k_tournament_with_replacement(pop, random.randint(1, popsize * 2),\
                        k=random.randint(2, popsize), **config['parent_selection_kwargs'])
            for i in range(popsize):
                assert same_object(pop[i], copies[i])

class TestKTournamentWithoutReplacement:
    def test_output_size(self):
        # Returns the correct number of individuals
        for _ in range(iterations):
            popsize = random.randrange(50, 500)
            pop = random_pop(popsize, **config['problem'])
            random_fitness(pop)
            outsize = random.randint(1, popsize - 3)
            k = random.randint(2, popsize - outsize)
            assert len(k_tournament_without_replacement(pop, outsize, k=k),\
                                **config['survival_selection_kwargs']) == outsize

    def test_elitist(self):
        # Never selects any of the worst k - 1 individuals, and always selects
        # at least one of the best popsize - outsize - k + 2 individuals
        # Get out a sheet of paper and derive this for a fun exercise :)
        for _ in range(iterations * 10): # Very prone to false positives
            popsize = random.randrange(10, 100)
            pop = random_pop(popsize, **config['problem'])
            random_fitness(pop)
            outsize = random.randint(1, popsize - 3)
            k = random.randint(2, popsize - outsize)
            ordered = sorted(pop, key=lambda x:x.fitness)
            worst_individuals = set(ordered[:k-1])
            best_individuals = set(ordered[-(popsize-outsize-k+2):])
            out = k_tournament_without_replacement(pop, outsize, k=k,\
                                **config['survival_selection_kwargs'])
            for selected in out:
                assert selected not in worst_individuals
            failed = True
            for selected in out:
                if selected in best_individuals:
                    failed = False
                    break
            assert not failed

    def test_is_based_on_fitness(self):
        # Individuals with a higher fitness are selected more often
        popsize = random.randrange(50, 500)
        pop = random_pop(popsize, **config['problem'])
        outsize = popsize // 2
        k = 2
        random_fitness(pop)
        counts = {x:0 for x in pop}
        out_of_order = 0
        for _ in range(iterations):
            for individual in k_tournament_without_replacement(pop, outsize, k=k,\
                                **config['survival_selection_kwargs']):
                counts[individual] += 1
        ordering = sorted(pop, key=lambda x:x.fitness)
        for i in range(len(ordering) - 1):
            if counts[ordering[i]] > counts[ordering[i + 1]]:
                out_of_order += 1
        assert out_of_order < popsize * iterations / 10

    def test_definitely_no_duplicates(self):
        # Selection is without replacement
        for _ in range(iterations):
            popsize = random.randrange(50, 500)
            pop = random_pop(popsize, **config['problem'])
            random_fitness(pop)
            outsize = random.randint(1, popsize - 3)
            k = random.randint(2, popsize - outsize)
            exists = {x:False for x in pop}
            for individual in k_tournament_without_replacement(pop, outsize, k=2,\
                                **config['survival_selection_kwargs']):
                assert not exists[individual]
                exists[individual] = True

    def test_population_unmodified(self):
        # Selection doesn't modify the input population
        for _ in range(5):
            popsize = random.randrange(50, 500)
            pop = random_pop(popsize, **config['problem'])
            random_fitness(pop)
            copies = [copy.deepcopy(x) for x in pop]
            outsize = random.randint(1, popsize - 3)
            k = random.randint(2, popsize - outsize)
            selection = k_tournament_without_replacement(pop, outsize, k=k,\
                                **config['survival_selection_kwargs'])
            for i in range(popsize):
                assert same_object(pop[i], copies[i])

class TestFitnessProportionate:
    def test_output_size(self):
        # Returns the correct number of individuals
        for _ in range(iterations):
            popsize = random.randrange(50, 500)
            pop = random_pop(popsize, **config['problem'])
            random_fitness(pop)
            outsize = random.randint(1, popsize * 2)
            assert len(fitness_proportionate_selection(pop, outsize,\
                                **config['parent_selection_kwargs'])) == outsize

    def test_strongly_prefers_outliers(self):
        # Very high fitness means very high bias
        for _ in range(iterations):
            popsize = random.randrange(50, 500)
            outsize = popsize * 3
            min_normal = random.uniform(-10, 10)
            max_normal = random.uniform(-10, 10)
            outlier = max_normal + ((max_normal - min_normal) * popsize * 1000)
            pop = random_pop(popsize, **config['problem'])
            random_fitness(pop, min_normal, max_normal)
            random.choice(pop).fitness = outlier
            not_it = 0
            for ind in fitness_proportionate_selection(pop, outsize,\
                                **config['parent_selection_kwargs']):
                if ind.fitness <= max_normal:
                    not_it += 1
            assert not_it < outsize / 10

    def test_is_uniform(self):
        # Uniform fitness means uniform random selection
        popsize = random.randrange(50, 500)
        out_of_bounds = 0
        outsize = popsize * 1000
        expected = outsize / popsize
        min_bound = max(expected / 1.2, 1)
        max_bound = expected * 1.2
        for _ in range(iterations):
            pop = random_pop(popsize, **config['problem'])
            identical_fitness(pop)
            counts = {x:0 for x in pop}
            out = fitness_proportionate_selection(pop, outsize,\
                                **config['parent_selection_kwargs'])
            for individual in out:
                counts[individual] += 1
            for count in counts.values():
                if min_bound > count or max_bound < count:
                    out_of_bounds += 1
        assert out_of_bounds <= 1.2 * iterations

    def test_definitely_duplicates(self):
        # Always has duplicates when out > in
        for _ in range(iterations):
            popsize = random.randrange(50, 500)
            pop = random_pop(popsize, **config['problem'])
            random_fitness(pop)
            outsize = popsize + 1
            counts = {x:0 for x in pop}
            for individual in fitness_proportionate_selection(pop, outsize,\
                                **config['parent_selection_kwargs']):
                counts[individual] += 1
            ones = 0
            multiples = 0
            for count in counts.values():
                if count == 1:
                    ones += 1
                elif count >= 2:
                    multiples += 1
            assert ones <= outsize - 1
            assert multiples >= 1

    def test_probably_duplicates(self):
        # Can have duplicates even when out < in
        failures = 0
        for _ in range(iterations):
            popsize = random.randrange(50, 500)
            outsize = popsize - 1
            pop = random_pop(popsize, **config['problem'])
            random_fitness(pop)
            counts = {x:0 for x in pop}
            for individual in fitness_proportionate_selection(pop, outsize,\
                                **config['parent_selection_kwargs']):
                counts[individual] += 1
            failed = True
            for count in counts.values():
                if count > 1:
                    failed = False
                    break
            if failed:
                failures += 1
        assert failures < max(iterations / 10, 2)

    def test_population_unmodified(self):
        # Selection doesn't modify the input population
        for _ in range(5):
            popsize = random.randrange(50, 500)
            pop = random_pop(popsize, **config['problem'])
            random_fitness(pop)
            copies = [copy.deepcopy(x) for x in pop]
            selection = fitness_proportionate_selection(pop, random.randint(1, popsize * 2),\
                                **config['parent_selection_kwargs'])
            for i in range(popsize):
                assert same_object(pop[i], copies[i])

class TestTruncation:
    def test_output_size(self):
        # Returns the correct number of individuals
        for _ in range(iterations):
            popsize = random.randrange(50, 500)
            pop = random_pop(popsize, **config['problem'])
            random_fitness(pop)
            outsize = random.randint(1, popsize - 1)
            assert len(truncation(pop, outsize,\
                                **config['survival_selection_kwargs'])) == outsize

    def test_no_baddies(self):
        # Selects none of the worst individuals
        for _ in range(iterations):
            popsize = random.randrange(50, 500)
            pop = random_pop(popsize, **config['problem'])
            random_fitness(pop)
            outsize = random.randint(1, popsize)
            worst_individuals = sorted(pop, key=lambda x:x.fitness)[:popsize-outsize]
            out = truncation(pop, outsize,\
                                **config['survival_selection_kwargs'])
            for ind in worst_individuals:
                assert ind not in out

    def test_all_goodies(self):
        # Selects all of the best individuals
        for _ in range(iterations):
            popsize = random.randrange(50, 500)
            pop = random_pop(popsize, **config['problem'])
            random_fitness(pop)
            outsize = random.randint(1, popsize)
            best_individuals = sorted(pop, key=lambda x:x.fitness)[popsize-outsize:]
            out = truncation(pop, outsize,\
                                **config['survival_selection_kwargs'])
            for ind in best_individuals:
                assert ind in out

    def test_no_duplicates(self):
        # Selection is without replacement
        for _ in range(iterations):
            popsize = random.randrange(50, 500)
            pop = random_pop(popsize, **config['problem'])
            random_fitness(pop)
            outsize = random.randint(1, popsize - 1)
            exists = {x:False for x in pop}
            for individual in truncation(pop, outsize,\
                                **config['survival_selection_kwargs']):
                assert not exists[individual]
                exists[individual] = True

    def test_population_unmodified(self):
        # Selection doesn't modify the input population
        for _ in range(5):
            popsize = random.randrange(50, 500)
            pop = random_pop(popsize, **config['problem'])
            random_fitness(pop)
            copies = [copy.deepcopy(x) for x in pop]
            outsize = random.randint(1, popsize - 1)
            selection = truncation(pop, outsize,\
                                **config['survival_selection_kwargs'])
            for i in range(popsize):
                assert same_object(pop[i], copies[i])