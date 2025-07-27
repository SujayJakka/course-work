
# cutting_stock/fitness_functions.py

import cutting_stock.implementation as impl
from functools import partial

'''Base fitness function for Assignments 1a and 1b.

Evaluates the input solution on the input problem.

For standard use (not minimize_area), fitness is the total length of stock, minus the used length of stock.
If the solution is invalid (any Shapes overlap or are out-of-bounds), returns failure_fitness.

Returns a dictionary containing the solution's fitness.

@param solution: indexable collection of placements, defining shape positions
@param shapes: indexable collection of shapes, of the same length as solution
@param bounds: bounds of the problem
@param failure_fitness: fitness to assign to solutions that violate constraints
@param minimize_area: if True, fitness is calculated using the solution's bounding box area
@return: dict containing values explained above
'''
def base_fitness_function(solution, shapes, bounds, failure_fitness, minimize_area, **kwargs):
    cells = impl.place_all(solution, shapes, bounds)

    if impl.count_overlaps(cells) or impl.count_out_of_bounds(cells, bounds):
        # Violations are not allowed, and all solutions with any violations are equally bad.
        fitness = failure_fitness

    else:
        if not minimize_area:
            # Fitness is the total length minus the used length
            available = bounds[0][1] - bounds[0][0]
            fitness = available - impl.get_extent(cells, False)
        else:
            # Fitness is the total area minus the used area
            available_area = (bounds[0][1] - bounds[0][0]) * (bounds[1][1] - bounds[1][0])
            used_area = impl.get_extent(cells, False) * impl.get_extent(cells, True)
            fitness = available_area - used_area

    return {
        'fitness': fitness
    }


'''Constraint satisfaction fitness function for Assignment 1c.

This is similar to base_fitness_function, except fitness has been renamed to base fitness,
and there are two new outputs (violations and unconstrained fitness).

unconstrained fitness is the fitness a solution would have if we ignore the
two constraints that shapes must be entirely in-bounds and must not overlap.

violations is a count of the number of times the constraints are violated,
i.e., the number of cells that are out-of-bounds and the number of overlapping cells.
It serves as a quantification of how badly a solution violated the constraints.

@param solution: indexable collection of placements, defining shape positions
@param shapes: indexable collection of shapes, of the same length as solution
@param bounds: bounds of the problem
@param failure_fitness: fitness to assign to solutions that violate constraints
@param minimize_area: if True, fitness is calculated using the solution's bounding box area
@return: dict containing values explained above
'''
def unconstrained_fitness_function(solution, shapes, bounds, failure_fitness, minimize_area, **kwargs):
    cells = impl.place_all(solution, shapes, bounds)

    # Unconstrained fitness ignores all violations
    if not minimize_area:
        # Fitness is the total length minus the used length
        available = bounds[0][1] - bounds[0][0]
        unconstrained_fitness = available - impl.get_extent(cells, False)
    else:
        # Fitness is the total area minus the used area
        available_area = (bounds[0][1] - bounds[0][0]) * (bounds[1][1] - bounds[1][0])
        used_area = impl.get_extent(cells, False) * impl.get_extent(cells, True)
        unconstrained_fitness = available_area - used_area

    # Count all violations
    violations = impl.count_overlaps(cells) + impl.count_out_of_bounds(cells, bounds)

    if violations:
        # All solutions with any violations have equally bad base fitness.
        base_fitness = failure_fitness
    else:
        base_fitness = unconstrained_fitness

    return {
        'base fitness': base_fitness,
        'unconstrained fitness': unconstrained_fitness,
        'violations': violations
    }


'''Multiobjective fitness function for Assignment 1d.

This function calculates fitness similarly to basic_fitness_function,
but returns two fitness values: one minimizing length, the other minimizing width.

@param solution: indexable collection of placements, defining shape positions
@param shapes: indexable collection of shapes, of the same length as solution
@param bounds: bounds of the problem
@param failure_fitness: fitness to assign to solutions that violate constraints
@param shared_edges: if True, adds a third objective (explained in the notebook/document)
@return: dict containing values explained above
'''
def multiobjective_fitness_function(solution, shapes, bounds, failure_fitness, shared_edges=None, **kwargs):
    cells = impl.place_all(solution, shapes, bounds)

    invalid = impl.count_overlaps(cells) or impl.count_out_of_bounds(cells, bounds)

    if invalid:
        # All solutions with any violations are equally bad.
        length = failure_fitness
        width = failure_fitness
    else:
        length_available = bounds[0][1] - bounds[0][0]
        width_available = bounds[1][1] - bounds[1][0]
        length = length_available - impl.get_extent(cells, False)
        width = width_available - impl.get_extent(cells, True)

    to_return = {
        'length': length,
        'width': width
    }

    if shared_edges:
        if invalid:
            to_return['edges'] = failure_fitness
        else:
            to_return['edges'] = -impl.count_shared_edges(cells)

    return to_return
