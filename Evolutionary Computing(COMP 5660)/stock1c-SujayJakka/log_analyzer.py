
# log_analyzer.py

from statistics import mean


def universal_analysis(log, evals):
    entries = [entry.split(': ') for entry in log]
    values = dict()
    for entry in entries:
        key = entry[0]
        val = entry[1]
        if key not in values:
            values[key] = [val]
        else:
            values[key].append(val)

    mu = int(values['mu'][0])
    num_children = int(values['num_children'][0])
    evaluations = [int(val) for val in values['Evaluations']]
    if evaluations[0] != mu:
        print('Initial evaluation count is incorrect.')
    for i in range(1, len(evaluations)):
        delta = evaluations[i] - evaluations[i-1]
        if delta != num_children:
            print('A generation increased the evaluation count by an incorrect amount. ' +\
                  'This could be a false positive caused by updating the evaluation count after survival selection.')
            break

    if evaluations[-1] < evals or evaluations[-1] >= evals + num_children:
        print('Final evaluation count seems incorrect.')

    child_counts = [int(val) for val in values['Number of children']]
    num_generations = len(child_counts)
    if any([count != num_children for count in child_counts]):
        print('Number of children seems incorrect.')

    combined_pre_pop_sizes = [int(val) for val in values['Pre-survival population size']]
    expected = mu + num_children
    if any([size != expected for size in combined_pre_pop_sizes]):
        print('Population size before survival selection seems incorrect.')

    combined_post_pop_sizes = [int(val) for val in values['Post-survival population size']]
    if any([size != mu for size in combined_post_pop_sizes]):
        print('Population size after survival selection seems incorrect.')

    if num_generations == 1:
        print('You only have one generation of children!')

    return values


def analyze_base_log(log, evals):
    values = universal_analysis(log, evals)
    means = [float(val) for val in values['Local mean']]
    best_mean_so_far = means[0]
    for i in range(1, len(means)):
        if means[i] > best_mean_so_far:
            best_mean_so_far = means[i]
        elif means[i] / best_mean_so_far < 0.75:
            print('Mean population fitness dropped significantly over time at least once. ' +\
                  'This *may* indicate a bug (especially if using truncation), or poor configuration. '+\
                  'You may ignore this if you deliberately chose a very non-elitist configuration and can justify your choice.')
            break


def analyze_constraint_satisfaction_log(log, evals):
    values = universal_analysis(log, evals)
    mean_penalized = [float(val) for val in values['Local mean penalized fitness']]
    max_penalized = [float(val) for val in values['Local best penalized fitness']]
    mean_base = [float(val) for val in values['Local mean base fitness']]
    max_base = [float(val) for val in values['Local best base fitness']]

    if any([len(x) != len(max_base) for x in [mean_penalized, max_penalized, mean_base]]):
        print('Different amounts of data recorded for different fitness metrics.')

    best_mean_so_far = mean_penalized[0]
    for i in range(1, len(mean_penalized)):
        if mean_penalized[i] > best_mean_so_far:
            best_mean_so_far = mean_penalized[i]
        elif mean_penalized[i] / best_mean_so_far < 0.75:
            print('Mean population penalized fitness dropped significantly over time at least once. ' +\
                  'This *may* indicate a bug (especially if using truncation), or poor configuration. '+\
                  'You may ignore this if you deliberately chose a very non-elitist configuration and can justify your choice.')
            break


def analyze_multiobjective_log(log, evals):
    values = universal_analysis(log, evals)

    front_sizes = [int(val) for val in values['Individuals in the Pareto front']]
    if all([size == 1 for size in front_sizes]):
        print('Every generation\'s Pareto front only has one individual.')

    mean_length = [float(val) for val in values['Local mean length']]
    max_length = [float(val) for val in values['Local best length']]
    mean_width = [float(val) for val in values['Local mean length']]
    max_width = [float(val) for val in values['Local best length']]
    hypervolume = [float(val) for val in values['Local Pareto front hypervolume']]

    if any([len(x) != len(hypervolume) for x in [mean_length, max_length, mean_width, max_width]]):
        print('Different amounts of data recorded for different objective scores.')

    best_volume_so_far = hypervolume[0]
    for i in range(1, len(hypervolume)):
        if hypervolume[i] > best_volume_so_far:
            best_volume_so_far = hypervolume[i]
        elif hypervolume[i] / best_volume_so_far < 0.75:
            print('Local Pareto front hypervolume dropped significantly over time at least once. ' +\
                  'This *may* indicate a bug (especially if using truncation), or poor configuration. '+\
                  'You may ignore this if you deliberately chose a very non-elitist configuration and can justify your choice.')
            break

