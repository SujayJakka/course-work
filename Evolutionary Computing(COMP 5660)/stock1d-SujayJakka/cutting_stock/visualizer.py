
# cutting_stock/visualizer.py

import cutting_stock.implementation as impl
import matplotlib.pyplot as plt

'''Creates a matplotlib figure visualizing a solution.

You shouldn't be calling this directly; it is wrapped in a function object returned by the fitness functions.

@param solution: the solution to visualize
@param shapes: shapes that were input to the fitness function
@param bounds: bounds that were input to the fitness function
@param visible_margin: width of out-of-bounds cells to display
@param path: path to save figure into; figure is instead shown to console if this evaluates to False
'''
def visualize(solution, shapes, bounds, visible_margin, path=None, **kwargs):
    cells = impl.place_all(solution, shapes, bounds)

    x_display = (bounds[0][0] - visible_margin, bounds[0][1] + visible_margin)
    y_display = (bounds[1][0] - visible_margin, bounds[1][1] + visible_margin)

    red = [None] * len(shapes)
    green = [None] * len(shapes)
    blue = [None] * len(shapes)
    for i in range(len(shapes)):
        red[i] = (5 * (i + 1) / len(shapes)) % 1.0
        green[i] = (3 * (i + 1) / len(shapes)) % 1.0
        blue[i] = (2 * (i + 1) / len(shapes)) % 1.0
    halfway = len(shapes) // 2
    red = red[:halfway] + list(reversed(red[halfway:]))
    green = list(reversed(green))

    # imshow axes are a bit backwards; y-axis comes first, x-axis second
    # Except for text... that's the normal order... and must be done after coloring, I think
    with plt.ioff():
        fig, ax = plt.subplots(constrained_layout=True)
        rgbs = [[[1.0, 1.0, 1.0, 1.0] for _ in range(*x_display)] for __ in range(*y_display)]

        # Set the borders
        for x in range(*x_display):
            rgbs[visible_margin - 1][x + visible_margin] = [0.0, 0.0, 0.0, 0.25]
            rgbs[bounds[1][1] + visible_margin][x + visible_margin] = [0.0, 0.0, 0.0, 0.25]
        for y in range(*y_display):
            rgbs[y + visible_margin][visible_margin - 1] = [0.0, 0.0, 0.0, 0.25]
            rgbs[y + visible_margin][bounds[0][1] + visible_margin] = [0.0, 0.0, 0.0, 0.25]

        # Place the shapes
        overlaps = set()
        for cell, shapelist in cells.items():
            if impl.in_bounds(cell, (x_display, y_display)):
                if len(shapelist) > 1:
                    rgbs[cell[1] + visible_margin][cell[0] + visible_margin] = [0.0, 0.0, 0.0, 1.0]
                    overlaps.add((cell[0] + visible_margin, cell[1] + visible_margin, len(shapelist)))
                else:
                    rgbs[cell[1] + visible_margin][cell[0] + visible_margin] =\
                            [red[shapelist[0]],
                             green[shapelist[0]],
                             blue[shapelist[0]],
                             1.0]

        ax.set_xticks([])
        ax.set_yticks([])
        ax.imshow(rgbs, origin='lower')
        for overlap in overlaps:
            ax.text(overlap[0], overlap[1], str(overlap[2]),
                    ha='center', va='center', fontsize=5.0, color='white')

        # This didn't work, as the linewidth is not to the same scale as the cells
        # Now, we instead set RGBs to black above (this is left for posterity)
        # ax.grid(color='black', snap=True, linewidth=1.0)
        # ax.set_xticks([bounds[0][0] + visible_margin - 0.75, bounds[0][1] + visible_margin], ['min x', 'max x'])
        # ax.set_yticks([bounds[1][0] + visible_margin - 0.75, bounds[1][1] + visible_margin], ['min y', 'max y'])
        ax.margins = (0.01)
        fig.canvas.header_visible = False
        fig.canvas.footer_visible = False

        if path:
            fig.savefig(path, bbox_inches='tight')
            plt.close(fig)
        else:
            fig.show()

