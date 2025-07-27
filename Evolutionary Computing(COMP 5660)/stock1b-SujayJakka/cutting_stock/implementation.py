"""
cutting_stock/implementation.py

************************************************************
************************************************************
************************************************************
***  Everything in this file is problem implementation.  ***
***     You don't need to read or understand it, but     ***
***   it may improve your comprehension of the problem,  ***
*** and is generally a decent example of good practices. ***
***   The implementation foregoes some optimizations,    ***
***  in order to be more easily-understood and modular.  ***
************************************************************
************************************************************
************************************************************
"""

"""Checks if a cell falls within an (,] (inclusive, exclusive) range.

@param cell: iterable values representing the cell to check
@param bounds: iterable of same length as cell, containing pairs of values defining each dimension
@return: whether the cell falls within the specified bounds
"""
def in_bounds(cell, bounds):
    assert len(cell) == len(bounds), "Different dimensions for cell and bounds"
    return all([bounds[i][0] <= cell[i] < bounds[i][1] for i in range(len(cell))])


"""Returns the orthogonal neighbors to a cell.

@param cell: cell to get the neighbors of
@return: all cells that are +/- 1 in a single dimension
"""
def get_neighbors(cell):
    candidates = set()
    dimensions = len(cell)
    for d in range(dimensions):
        candidates.add((cell[i] + 1 if i == d else cell[i] for i in range(dimensions)))
        candidates.add((cell[i] - 1 if i == d else cell[i] for i in range(dimensions)))
    return candidates


"""Applies a placement to a shape (rotation and translation).

@param shape: the shape to place
@param placement: the placement defining the shape's position
@return: the set of cells the shape occupies
"""
def place_shape(shape, placement):
    assert len(placement) == 3, "Placement must have exactly 3 values"
    assert placement[0] % 1 == 0, "Placement values must be integers"
    assert placement[1] % 1 == 0, "Placement values must be integers"

    # First, rotate the shape
    # Data structure is irrelevant; this is an intermediate and only needs to be iterable
    if placement[2] == 0:
        rotated = shape
    elif placement[2] == 1:
        rotated = [(cell[1], -cell[0]) for cell in shape]
    elif placement[2] == 2:
        rotated = [(-cell[0], -cell[1]) for cell in shape]
    elif placement[2] == 3:
        rotated = [(-cell[1], cell[0]) for cell in shape]
    else:
        assert False, "Rotation must be 0, 1, 2, or 3"

    # Returns as a set of tuples, for efficient placement and collision checks
    return {(cell[0] + placement[0], cell[1] + placement[1]) for cell in rotated}


"""Applies a solution to the problem, calculating all occupied cells and listing which shapes occupy them.
In other words, this is the phenotype mapping.

@param solution: indexable collection of placements defining shape positions
@param shapes: indexable collection of shapes, of the same length as solution
@param bounds: bounds of the problem
@return: dict, keyed on coordinate tuples, containing a list of indices representing shapes occupying that cell
"""
def place_all(solution, shapes, bounds):
    assert len(solution) == len(shapes), "Solution must have the same length as shapes"
    occupied = dict()
    for i in range(len(shapes)):
        assert in_bounds([solution[i][0], solution[i][1]], bounds), "Translation is out of bounds"
        for cell in place_shape(shapes[i], solution[i]):
            if cell in occupied:
                occupied[cell].append(i)
            else:
                occupied[cell] = [i]
    return occupied


"""Calculates the extent of occupied cells along an axis.

@param cells: dict of cells as output by place_all()
@param y: if True, counts extent along the y-axis, else along the x-axis
@return: extent of occupied cells along the given axis
"""
def get_extent(cells, y = False):
    if y:
        values = [cell[1] for cell in cells]
    else:
        values = [cell[0] for cell in cells]
    return 1 + max(values) - min(values)


"""Counts the number of overlap violations.

For any occupied cell, the number of violations is the number of shapes occupying it minus one.

@param cells: dict of cells as output by place_all()
@return: number of overlap violations
"""
def count_overlaps(cells):
    count = 0
    for shapes in cells.values():
        count += len(shapes) - 1
    return count


"""Counts the number of out-of-bounds violations.

For cells occupied by multiple shapes, each shape counts as a separate violation.

@param cells: dict of cells as output by place_all()
@param bounds: problem bounds
@return: the number of out-of-bounds cells
"""
def count_out_of_bounds(cells, bounds):
    count = 0
    for cell, shapes in cells.items():
        if not in_bounds(cell, bounds):
            count += len(shapes)
    return count


def count_shared_edges(cells):
    count = 0
    for cell, shapes in cells.items():
        neighbor_cells = [(cell[0] + 1, cell[1]), (cell[0], cell[1] + 1)]
        for neighbor_cell in neighbor_cells:
            if neighbor_cell in cells:
                for neighbor_shape in cells[neighbor_cell]:
                    if neighbor_shape not in shapes:
                        count += 1
                        break
    return count
