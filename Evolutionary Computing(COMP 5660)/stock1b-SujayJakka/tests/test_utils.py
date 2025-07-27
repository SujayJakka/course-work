
# tests/test_utils.py

import pytest, random, os, sys, inspect
import numpy as np
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from linear_genotype import LinearGenotype

def random_pop(mu, *args, **kwargs):
    return LinearGenotype.initialization(mu, *args, **kwargs)

def unique_parents(*args, **kwargs):
    shared_alleles = True
    while shared_alleles:
        shared_alleles = False
        parents = random_pop(2, *args, **kwargs)
        for index in range(len(parents[0].genes)):
            if equivalent_alleles(parents[0].genes[index], parents[1].genes[index]):
                shared_alleles = True
                break
    return parents

def random_fitness(pop, minimum=-1000, maximum=1000):
    for i in range(len(pop)):
        pop[i].fitness = random.uniform(minimum, maximum)

def identical_fitness(pop, minimum=-1000, maximum=1000):
    fitness = random.uniform(minimum, maximum)
    for i in range(len(pop)):
        pop[i].fitness = fitness

def same_object(obj1, obj2):
    if dir(obj1) != dir(obj2):
        return False
    dir1 = obj1.__dict__
    dir2 = obj2.__dict__
    for attr in dir1:
        # Because Numpy arrays break equality checks... >:(
        equal = dir1[attr] == dir2[attr]
        if isinstance(equal, bool):
            if not equal:
                return False
        elif not equal.all():
            return False
    return True

def equivalent_alleles(allele1, allele2):
    for i in range(len(allele1)):
        # Because Numpy arrays break equality checks... >:(
        equal = allele1[i] == allele2[i]
        if isinstance(equal, bool):
            if not equal:
                return False
        elif not equal.all():
            return False
    return True

def get_changes(child, parent):
    changes = []
    for i in range(len(child.genes)):
        if not equivalent_alleles(child.genes[i], parent.genes[i]):
            changes.append(i)
    return changes

def allele_is_unique(allele, adults):
    for adult in adults:
        for adult_allele in adult.genes:
            if equivalent_alleles(allele, adult_allele):
                return False
    return True

def has_unique_allele(child, adults):
    for allele in child.genes:
        if allele_is_unique(allele, adults):
            return True
    return False
