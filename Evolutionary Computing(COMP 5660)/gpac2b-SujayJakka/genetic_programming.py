
# genetic_programming.py

import random
from base_evolution import BaseEvolutionPopulation

class GeneticProgrammingPopulation(BaseEvolutionPopulation):
    def generate_children(self):
        children = list()
        recombined_child_count = 0
        mutated_child_count = 0

        # 2b TODO: Generate self.num_children children by either:
        #          recombining two parents OR
        #          generating a mutated copy of a single parent.
        #          Use self.mutation_rate to decide how each child should be made.
        #          Use your Assignment Series 1 generate_children function as a reference.
        #          Count the number of recombined/mutated children in the provided variables.

        # Randomly select self.num_children * 2 parents using your selection algorithm
        parents = self.parent_selection(self.population, self.num_children * 2, **self.parent_selection_kwargs)
        random.shuffle(parents)

        while len(children) != self.num_children:
            # Sample uniformly a random prob from the range of 0 to 1
            mutation_prob = random.uniform(0, 1)
            if mutation_prob <= self.mutation_rate:
                random_parent = random.choice(parents)
                children.append(random_parent.mutate(**self.mutation_kwargs))
                mutated_child_count += 1
            else:
                random_parent_1 = random.choice(parents)
                while True:
                    random_parent_2 = random.choice(parents)
                    if random_parent_1 is not random_parent_2:
                        break
                
                children.append(random_parent_1.recombine(random_parent_2, **self.recombination_kwargs))
                recombined_child_count += 1


        self.log.append(f'Number of children: {len(children)}')
        self.log.append(f'Number of recombinations: {recombined_child_count}')
        self.log.append(f'Number of mutations: {mutated_child_count}')

        return children
