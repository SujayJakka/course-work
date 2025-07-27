
# tests/test_linear_genotype.py

from test_utils import *
import random, pytest, copy
import numpy as np
from snake_eyes import read_config

config = read_config('configs/1b/easy_green_config.txt', globals(), locals())
iterations = 500

class TestUniformRecombination:
    @classmethod
    def setup_class(cls):
        config['recombination_kwargs']['method'] = 'uniform'

    def test_length(self):
        # Returns child with correct genes length
        for _ in range(iterations):
            parents = unique_parents(**config['problem'])
            child = parents[0].recombine(parents[1], **config['recombination_kwargs'])
            assert len(child.genes) == len(parents[0].genes)

    def test_is_uniform(self):
        # Each locus is selected uniform randomly
        expected_lower_bound = 0.2
        expected_upper_bound = 0.8
        out_of_bounds = 0
        m_iterations = iterations * 100
        points = [0 for _ in range(len(config['problem']['shapes']))]
        for _ in range(m_iterations):
            parents = unique_parents(**config['problem'])
            child = parents[0].recombine(parents[1], **config['recombination_kwargs'])
            num_from_first = 0
            for i in range(len(child.genes)):
                if equivalent_alleles(child.genes[i], parents[0].genes[i]):
                    num_from_first += 1
                    points[i] += 1
            ratio = num_from_first / len(child.genes)
            if ratio < expected_lower_bound or ratio > expected_upper_bound:
                out_of_bounds += 1
        assert out_of_bounds < m_iterations / 10
        min_bound = 0.4
        max_bound = 0.6
        for point in points:
            ratio = point / m_iterations
            assert ratio < max_bound
            assert ratio > min_bound

    def test_parents_unmodified(self):
        # Parents are not modified at all by recombination
        for _ in range(iterations):
            parents = random_pop(2, **config['problem'])
            copies = [copy.deepcopy(x) for x in parents]
            child = parents[0].recombine(parents[1], **config['recombination_kwargs'])
            assert same_object(copies[0], parents[0])
            assert same_object(copies[1], parents[1])

class Test1PointCrossoverRecombination:
    @classmethod
    def setup_class(cls):
        config['recombination_kwargs']['method'] = 'one-point'

    def test_length(self):
        # Returns child with correct genes length
        for _ in range(iterations):
            parents = random_pop(2, **config['problem'])
            child = parents[0].recombine(parents[1], **config['recombination_kwargs'])
            assert len(child.genes) == len(parents[0].genes)

    def test_has_1_point(self):
        # Child has one distinct crossover point
        # No clones; always take at least one allele from each parent
        for _ in range(iterations):
            parents = unique_parents(**config['problem'])
            child = parents[0].recombine(parents[1], **config['recombination_kwargs'])
            changes = get_changes(child, parents[0])
            for change in changes:
                assert change >= changes[0]

    def test_point_is_uniformly_selected(self):
        # The crossover point is selected uniformly out of all valid loci
        # All points that take at least one allele from each parent are valid
        # This will fail if the above test fails
        # Being off-by-one is an extremely common error that causes this to fail:
        # make sure the first locus is always from one parent,
        # make sure the last locus is always from the other parent,
        # and make sure all other loci can be from either parent.
        length = len(config['problem']['shapes'])
        counts = {x:0 for x in range(length)}
        m_iterations = iterations * 100
        for _ in range(m_iterations):
            parents = unique_parents(**config['problem'])
            child = parents[0].recombine(parents[1], **config['recombination_kwargs'])
            counts[get_changes(child, parents[0])[0]] += 1
        expected = m_iterations / (length - 1)
        expected_lower_bound = expected - (expected * 0.2)
        expected_upper_bound = expected + (expected * 0.2)
        min_bound = expected - (expected * 0.4)
        max_bound = expected + (expected * 0.4)
        assert counts[0] == 0
        counts[0] = expected
        out_of_bounds = 0
        for hit in counts.values():
            assert hit < max_bound
            assert hit > min_bound
            if hit > expected_upper_bound or hit < expected_lower_bound:
                out_of_bounds += 1
        assert out_of_bounds < length / 20

    def test_parents_unmodified(self):
        # Parents are not modified at all by recombination
        for _ in range(iterations):
            parents = random_pop(2, **config['problem'])
            copies = [copy.deepcopy(x) for x in parents]
            child = parents[0].recombine(parents[1], **config['recombination_kwargs'])
            assert same_object(copies[0], parents[0])
            assert same_object(copies[1], parents[1])

class TestMutation:
    def test_length(self):
        # Returns child with correct genes length
        for _ in range(iterations):
            parent = random_pop(1, **config['problem'])[0]
            child = parent.mutate(**config['mutation_kwargs'])
            assert len(child.genes) == len(parent.genes)

    def test_usually_changes(self):
        # Mutation usually produces changes
        fails = 0
        for _ in range(iterations):
            parent = random_pop(1, **config['problem'])[0]
            child = parent.mutate(**config['mutation_kwargs'])
            if len(get_changes(child, parent)) == 0:
                fails += 1
        ratio = fails / iterations
        assert ratio < 0.15

    def test_no_locus_bias(self):
        # Each locus has the same independent chance of mutating
        counts = [0 for _ in range(len(config['problem']['shapes']))]
        m_iterations = iterations * 100
        for _ in range(m_iterations):
            parent = random_pop(1, **config['problem'])[0]
            child = parent.mutate(**config['mutation_kwargs'])
            for i in range(len(child.genes)):
                for j in range(len(child.genes[i])):
                    if child.genes[i][j] != parent.genes[i][j]:
                        counts[i] += 1
                        break
        average_change = sum(counts) / len(counts)
        expected_lower_bound = average_change - average_change * 0.2
        expected_upper_bound = average_change + average_change * 0.2
        out_of_bounds = 0
        for count in counts:
            if count > expected_upper_bound or count < expected_lower_bound:
                out_of_bounds += 1
        assert out_of_bounds < len(config['problem']['shapes']) / 20

    def test_parent_unmodified(self):
        # Parent is not modified at all by mutation
        for _ in range(iterations):
            parent = random_pop(1, **config['problem'])[0]
            cpy = copy.deepcopy(parent)
            child = parent.mutate(**config['mutation_kwargs'])
            assert same_object(cpy, parent)
