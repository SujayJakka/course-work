
# tests/test_base_evolution.py

from test_utils import *
import random, pytest, copy, os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from snake_eyes import read_config
from selection import *
import base_evolution as evo

config = read_config('configs/1b/easy_green_config.txt', globals(), locals())
iterations = 100

class TestChildGeneration:
    def test_length(self):
        # generate_children produces the correct number of children
        config['ea']['parent_selection'] = uniform_random_selection
        for _ in range(iterations):
            config['ea']['mu'] = random.randint(1, 100)
            config['ea']['num_children'] = random.randint(1, 100)
            config['ea']['mutation_rate'] = random.random()
            ea = evo.BaseEvolutionPopulation(**config['ea'], **config)
            random_fitness(ea.population)
            assert len(ea.generate_children()) == ea.num_children

    def test_unmodified_parents(self):
        # generate_children has no impact on the population
        # If this fails, it's likely because you are not deep copying genes
        config['ea']['parent_selection'] = uniform_random_selection
        for _ in range(iterations):
            config['ea']['mu'] = random.randint(1, 100)
            config['ea']['num_children'] = random.randint(1, 100)
            config['ea']['mutation_rate'] = random.random()
            ea = evo.BaseEvolutionPopulation(**config['ea'], **config)
            random_fitness(ea.population)
            copies = copy.deepcopy(ea.population)
            children = ea.generate_children()
            for i in range(len(copies)):
                assert same_object(ea.population[i], copies[i])

    def test_always_mutates(self):
        # generate_children mutates all children with mutation rate of 1
        config['ea']['parent_selection'] = uniform_random_selection
        config['ea']['mutation_rate'] = 1.0
        config['ea']['mu'] = 2
        config['ea']['num_children'] = 100
        mutated = 0
        for _ in range(iterations):
            ea = evo.BaseEvolutionPopulation(**config['ea'], **config)
            random_fitness(ea.population)
            # Convoluted nested loops because, as usual, numpy arrays break equality checks
            for child in ea.generate_children():
                if has_unique_allele(child, ea.population):
                    mutated += 1
        assert mutated >= 0.75 * config['ea']['num_children'] * iterations

    def test_never_mutates(self):
        # generate_children mutates no children with mutation rate of 0
        config['ea']['parent_selection'] = uniform_random_selection
        config['ea']['mutation_rate'] = 0.0
        config['ea']['mu'] = 2
        config['ea']['num_children'] = 100
        for _ in range(iterations):
            ea = evo.BaseEvolutionPopulation(**config['ea'], **config)
            random_fitness(ea.population)
            for child in ea.generate_children():
                assert not has_unique_allele(child, ea.population)

    def test_sometimes_mutates(self):
        # generate_children mutates children half the time with mutation rate of 0.5
        config['ea']['parent_selection'] = uniform_random_selection
        config['ea']['mutation_rate'] = 0.5
        config['ea']['mu'] = 2
        config['ea']['num_children'] = 100
        mutants = 0
        for _ in range(iterations):
            local_mutants = 0
            ea = evo.BaseEvolutionPopulation(**config['ea'], **config)
            random_fitness(ea.population)
            for child in ea.generate_children():
                if has_unique_allele(child, ea.population):
                    local_mutants += 1
            mutants += local_mutants
        ratio = mutants / config['ea']['num_children'] / iterations
        assert ratio < 0.65
        assert ratio > 0.35

    def test_random_number_of_mutations(self):
        # generate_children mutates a stochastic number of children
        # If this fails, you are probably calculating a deterministic number of mutations per generation
        # You should instead check for mutation independently for each child
        config['ea']['parent_selection'] = uniform_random_selection
        config['ea']['mutation_rate'] = 0.5
        config['ea']['mu'] = 2
        config['ea']['num_children'] = 100
        num_mutants = set()
        for _ in range(iterations):
            local_mutants = 0
            ea = evo.BaseEvolutionPopulation(**config['ea'], **config)
            random_fitness(ea.population)
            for child in ea.generate_children():
                if has_unique_allele(child, ea.population):
                    local_mutants += 1
            num_mutants.add(local_mutants)
        assert len(num_mutants) > 2
