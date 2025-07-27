import statistics
import scipy

def run_stats(dataset1, dataset2):
    with open(dataset1, 'r') as f:
        data1 = [int(line) for line in f.readlines()]

    with open(dataset2, 'r') as f:
        data2 = [int(line) for line in f.readlines()]

    assert len(data1) == len(data2), 'Datasets do not have the same number of samples!'

    print('Number of samples:', len(data1))

    print(dataset1 + ' mean:', statistics.mean(data1))
    print(dataset1 + ' stdv:', statistics.stdev(data1))

    print(dataset2 + ' mean:', statistics.mean(data2))
    print(dataset2 + ' stdv:', statistics.stdev(data2))

    test_result = scipy.stats.ttest_ind(data1, data2, equal_var=False)
    print('p-value:', test_result.pvalue)
