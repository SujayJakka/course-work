import matplotlib.pyplot as plt
from collections import defaultdict

class HistogramMaker:
    def __init__(self, failure_fitness, **kwargs):
        self.data = defaultdict(int)
        self.num_invalid = 0
        self.failure_fitness = failure_fitness


    def add(self, fitness):
        if fitness == self.failure_fitness:
            self.num_invalid += 1
        else:
            self.data[fitness] += 1


    def save_to_file(self, file):
        with open(file, 'w') as f:
            f.write(str(self.failure_fitness) + '\n')
            f.write(str(self.num_invalid) + '\n')
            for key, val in self.data.items():
                f.write(f'{key}:{val}' + '\n')


    def load_from_file(self, file):
        with open(file, 'r') as f:
            data = list(f.readlines())
        self.failure_fitness = int(data[0])
        self.num_invalid = int(data[1])
        self.data = defaultdict(int)
        for i in range(2, len(data)):
            key, val = data[i].split(':')
            self.data[int(key)] = int(val)


    @classmethod
    def merge(cls, others):
        hist = cls(others[0].failure_fitness)
        for other in others:
            assert other.failure_fitness == hist.failure_fitness
            hist.num_invalid += other.num_invalid
            for key, val in other.data.items():
                hist.data[key] += val
        return hist


    def get_plot(self, title):
        with plt.ioff():
            if len(self.data) == 0:
                fig, ax = plt.subplots(constrained_layout=True)
                invalid_bar = ax.bar('Invalid', self.num_invalid, color='k')
                ax.bar_label(invalid_bar, [self.num_invalid])
                ticks = ['Invalid']
                ax.set_xticks(ticks, ticks)
                ax.set_xlabel('Fitness')
                ax.set_ylabel('Occurrences')
                ax.set_title(title)

            buckets = dict()
            for fitness, count in self.data.items():
                buckets[str(fitness)] = count
            max_bucket = max(buckets.values())
            zeros = [0 for _ in range(max(self.data.keys()) + 1)]

            if self.num_invalid > 5.0 * max_bucket:
                fig, (upper, lower) = plt.subplots(2, 1, sharex=True, constrained_layout=True)
                invalid_bar = upper.bar('Invalid', self.num_invalid, color='k')
                upper.bar_label(invalid_bar, [self.num_invalid], fmt='{:.5g}', fontsize=8.0)
                lower.bar('Invalid', self.num_invalid, color='k')
                lower.bar(list(map(str, range(len(zeros)))), zeros)
                nonzero_bars = lower.bar(buckets.keys(), buckets.values())
                lower.set_ylim(0, max_bucket * 1.25)
                max_x = max(self.data.keys())
                if max_x < 100:
                    ticks = ['Invalid'] + [str(num) for num in range(5, max_x + 1, 5)]
                elif max_x < 300:
                    ticks = ['Invalid'] + [str(num) for num in range(10, max_x + 1, 10)]
                else:
                    ticks = ['Invalid'] + [str(num) for num in range(25, max_x + 1, 25)]
                lower.set_xticks(ticks, ticks)
                upper.set_ylim(self.num_invalid * 0.9, self.num_invalid * 1.05)
                upper.tick_params(bottom=False)
                fig.supxlabel('Fitness')
                fig.supylabel('Occurrences')
                fig.suptitle(title)

            else:
                fig, ax = plt.subplots(constrained_layout=True)
                invalid_bar = ax.bar('Invalid', self.num_invalid, color='k')
                ax.bar_label(invalid_bar, [self.num_invalid])
                ax.bar(list(map(str, range(len(zeros)))), zeros)
                nonzero_bars = ax.bar(buckets.keys(), buckets.values())
                ticks = ['Invalid'] + [str(num) for num in range(5, max(self.data.keys()) + 1, 5)]
                ax.set_xticks(ticks, ticks)
                ax.set_ylim(0, max(self.num_invalid, max_bucket) * 1.25)
                ax.set_xlabel('Fitness')
                ax.set_ylabel('Occurrences')
                ax.set_title(title)

            fig.canvas.header_visible = False
            fig.canvas.footer_visible = True
            return fig
