import matplotlib.pyplot as plt
from collections import defaultdict
import re


class BaseHistogramMaker:
    def __init__(self, **kwargs):
        self.data = defaultdict(int)


    def add(self, value):
        self.data[value] += 1


    def save_to_file(self, file):
        with open(file, 'w') as f:
            for key, val in self.data.items():
                f.write(f'{key}:{val}\n')


    LOAD_REGEX = re.compile(r'(.*):(.*)')
    def load_from_file(self, file):
        with open(file, 'r') as f:
            matches = LOAD_REGEX.findall(f.read())
        for m in matches:
            self.data[int(m[0])] = int(m[1])


    @classmethod
    def merge(cls, others):
        hist = cls()
        for other in others:
            for key, val in other.data.items():
                hist.data[key] += val
        return hist


    def get_plot(self, input_fig_ax=None, min_zero=False):
        with plt.ioff():
            if not self.data:
                if not input_fig_ax:
                    print('Empty histogram! Returning an empty plot.')
                fig, ax = plt.subplots(constrained_layout=True)
                fig.canvas.header_visible = False
                fig.canvas.footer_visible = True
                return fig

            min_x = min(self.data.keys())
            if min_zero:
                min_x = min(min_x, 0)
            max_x = max(self.data.keys())
            x_range = max_x - min_x
            buckets = [0] * (x_range + 1)
            labels = [str(i) for i in range(min_x, max_x + 1)]
            for key, val in self.data.items():
                buckets[key - min_x] = val

            if input_fig_ax:
                fig, ax = input_fig_ax
            else:
                fig, ax = plt.subplots(constrained_layout=True)
                fig.canvas.header_visible = False
                fig.canvas.footer_visible = True

            bars = ax.bar(labels, buckets, color='tab:orange')
            if x_range < 100:
                delta = 5
            elif x_range < 300:
                delta = 10
            elif x_range < 500:
                delta = 25
            elif x_range < 1000:
                delta = 50
            else:
                delta = 100
            mod = min_x % delta
            if mod:
                lowest_tick = min_x - mod + delta
            else:
                lowest_tick = min_x
            ticks = [str(num) for num in range(lowest_tick, max_x + 1, delta)]
            if input_fig_ax:
                return ticks
            ax.set_xticks(ticks, ticks)
            return fig


class HistogramMaker(BaseHistogramMaker):
    def __init__(self, failure_fitness, **kwargs):
        super().__init__(**kwargs)
        self.num_invalid = 0
        self.failure_fitness = failure_fitness


    def add(self, fitness):
        if fitness == self.failure_fitness:
            self.num_invalid += 1
        else:
            super().add(fitness)


    def save_to_file(self, file):
        super().save_to_file(file)
        with open(file, 'a') as f:
            f.write(str(self.failure_fitness) + '\n')
            f.write(str(self.num_invalid) + '\n')


    def load_from_file(self, file):
        super().load_from_file(file)
        with open(file, 'r') as f:
            data = list(f.readlines())
        self.failure_fitness = int(data[-2])
        self.num_invalid = int(data[-1])


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
                fig.canvas.header_visible = False
                fig.canvas.footer_visible = True
                return fig

            max_bucket = max(self.data.values())
            if self.num_invalid > 5.0 * max_bucket:
                fig, (upper, lower) = plt.subplots(2, 1, sharex=True, constrained_layout=True)

                invalid_bar = upper.bar('Invalid', self.num_invalid, color='k')
                upper.bar_label(invalid_bar, [self.num_invalid], fmt='{:.5g}', fontsize=8.0)
                upper.set_ylim(self.num_invalid * 0.9, self.num_invalid * 1.05)
                upper.tick_params(bottom=False)

                lower.bar('Invalid', self.num_invalid, color='k')
                ticks = super().get_plot((fig, lower), True)
                ticks = ['Invalid'] + ticks[1:]
                lower.set_xticks(ticks, ticks)
                lower.set_ylim(0, max_bucket * 1.25)

                fig.supxlabel('Fitness')
                fig.supylabel('Occurrences')
                fig.suptitle(title)

            else:
                fig, ax = plt.subplots(constrained_layout=True)
                invalid_bar = ax.bar('Invalid', self.num_invalid, color='k')
                ax.bar_label(invalid_bar, [self.num_invalid])

                ticks = super().get_plot((fig, ax), True)
                ticks = ['Invalid'] + ticks[1:]
                ax.set_xticks(ticks, ticks)

                ax.set_xlabel('Fitness')
                ax.set_ylabel('Occurrences')
                ax.set_title(title)

            fig.canvas.header_visible = False
            fig.canvas.footer_visible = True
            return fig


class InvalidityHistogramMaker(BaseHistogramMaker):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    def get_plot(self, title):
        with plt.ioff():
            fig = super().get_plot()
            ax = fig.axes[0]
            ax.set_xlabel('Violations')
            ax.set_ylabel('Occurrences')
            ax.set_title(title)
            return fig


class PenaltyHistogramMaker(BaseHistogramMaker):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    def add(self, penalized_fitness):
        super().add(int(round(penalized_fitness)))


    def get_plot(self, title):
        with plt.ioff():
            fig = super().get_plot()
            ax = fig.axes[0]
            ax.set_xlabel('Penalized Fitness (Rounded)')
            ax.set_ylabel('Occurrences')
            ax.set_title(title)
            return fig

