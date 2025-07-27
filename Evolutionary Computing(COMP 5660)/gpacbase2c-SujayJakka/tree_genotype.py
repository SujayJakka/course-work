
# tree_genotype.py

import random
from copy import deepcopy
from fitness import manhattan
from collections import deque

# Node Class that is used to make up the objects for TreeGenotype()
class Node():
    def __init__(self, primitive, parent):
        self.primitive = primitive
        self.left = None
        self.right = None
        # Added Fields
        self.parent = parent
        self.height = None
        self.size = None

# Function to update node fields after recombination and mutation
def update_node_fields(node):
    if not node:
        return

    node.size = 1 + node.left.size + node.right.size
    node.height = 1 + max(node.left.height, node.right.height)
    update_node_fields(node.parent)
        
def full_method(curr_depth, parent, **kwargs):

    # Will create a terminal node if it reaches depth limit
    # Will create either a G, P, F, W, or Constant Node in the case of Pac-Man
    # Will create either a G, P, F, W, M, or Constant Node in the case of Ghosts

    if curr_depth == kwargs["depth_limit"]:
        length_of_terminals = len(kwargs["terminals"])
        terminal_type = random.randint(0, length_of_terminals - 1)
        if terminal_type != length_of_terminals - 1:
            terminal_node = Node(kwargs["terminals"][terminal_type], parent)
            terminal_node.height = 0
            terminal_node.size = 1
            return terminal_node
        else:
            constant_range = kwargs["constant_range"]
            terminal_node = Node(random.uniform(constant_range[0], constant_range[1]), parent)
            terminal_node.height = 0
            terminal_node.size = 1
            return terminal_node
    # If not at depth limit will create another nonterminal node
    # The possible nonterminal nodes that it can create are +, -, *, /, or RAND
    else:
        nonterminal_type = random.randint(0, 4)
        nonterminal_node = Node(kwargs["nonterminals"][nonterminal_type], parent)
        nonterminal_node.left = full_method(curr_depth + 1, nonterminal_node, **kwargs)
        nonterminal_node.right = full_method(curr_depth + 1, nonterminal_node, **kwargs)
        nonterminal_node.height = 1 + max(nonterminal_node.left.height, nonterminal_node.right.height)
        nonterminal_node.size = 1 + nonterminal_node.left.size + nonterminal_node.right.size
        return nonterminal_node

# Same as the full method except we are able to create a terminal node even when we are not at the depth limit
# There is a 50/50 chance of creating a terminal or nonterminal node at any depth except for the depth limit,
# where we are forced to choose a terminal node
def grow_method(curr_depth, parent, **kwargs):
    continue_depth = random.randint(0, 1)

    # Will create a terminal node if it reaches depth limit or if we randomly select 0
    # Will create either a G, P, F, W, or Constant Node
    # Will create either a G, P, F, W, M, or Constant Node in the case of Ghosts
    
    if curr_depth == kwargs["depth_limit"] or continue_depth == 0:
        length_of_terminals = len(kwargs["terminals"])
        terminal_type = random.randint(0, length_of_terminals - 1)
        if terminal_type != length_of_terminals - 1:
            terminal_node = Node(kwargs["terminals"][terminal_type], parent)
            terminal_node.height = 0
            terminal_node.size = 1
            return terminal_node
        else:
            constant_range = kwargs["constant_range"]
            terminal_node = Node(random.uniform(constant_range[0], constant_range[1]), parent)
            terminal_node.height = 0
            terminal_node.size = 1
            return terminal_node
    # If not at depth limit will create another nonterminal node
    # The possible nonterminal nodes that it can create are +, -, *, /, or RAND
    else:
        nonterminal_type = random.randint(0, 4)
        nonterminal_node = Node(kwargs["nonterminals"][nonterminal_type], parent)
        nonterminal_node.left = grow_method(curr_depth + 1, nonterminal_node, **kwargs)
        nonterminal_node.right = grow_method(curr_depth + 1, nonterminal_node, **kwargs)
        nonterminal_node.height = 1 + max(nonterminal_node.left.height, nonterminal_node.right.height)
        nonterminal_node.size = 1 + nonterminal_node.left.size + nonterminal_node.right.size
        return nonterminal_node

# BFS on the TreeGenotype of a parent.
# Will return a dictionary with an integer as the key representing
# when a node was encountered in the BFS, and the value of the dictionary is a tuple
# of the corresponding node and depth of the node.
# E.g. number -> (node, depth)
def bfs(node):

    bfs_dict = {}
    queue = deque()
    queue.append(node)
    node_count = 0
    depth = 0

    while queue:
        for _ in range(len(queue)):
            popped_node = queue.pop()
            node_count += 1
            bfs_dict[node_count] = (popped_node, depth)
            
            if popped_node.left:
                queue.append(popped_node.left)
                queue.append(popped_node.right)
                
        depth += 1

    return bfs_dict

class TreeGenotype():
    def __init__(self):
        self.fitness = None
        self.genes = None
        # Added Fields
        self.base_fitness = None
        self.log = None


    @classmethod
    def initialization(cls, mu, depth_limit, **kwargs):
        population = [cls() for _ in range(mu)]

        # 2a TODO: Initialize genes member variables of individuals
        #          in population using ramped half-and-half.
        #          Pass **kwargs to your functions to give them
        #          the sets of terminal and nonterminal primitives.

        # For every individual in the population it has a random chance of being initialized with the grow or full method
        # The probability for selecting the full method is set in the config
        # There is also a uniform chance of selecting a depth_limit in the range [1, depth_limit]
        for individual in population:
            prob_of_full_method = random.uniform(0, 1)
            rand_depth_limit = random.randint(1, depth_limit)
            
            if prob_of_full_method <= kwargs["prob_of_full_method"]:
                individual.genes = full_method(0, None, depth_limit=rand_depth_limit, **kwargs)
            else:
                individual.genes = grow_method(0, None, depth_limit=rand_depth_limit, **kwargs)

        return population


    def serialize(self):
        # 2a TODO: Return a string representing self.genes in the required format.

        # Array to join all the serialized strings at the very end
        # O(n^2) -> O(n)
        serialized_string = []

        def preorder_traversal(node, curr_depth):
            if node is None:
                return
                
            serialized_string.append(("|" * curr_depth) + str(node.primitive)+ "\n")
            preorder_traversal(node.left, curr_depth + 1)
            preorder_traversal(node.right, curr_depth + 1)

        preorder_traversal(self.genes, 0)
        return "".join(serialized_string)


    def deserialize(self, serialization):
        # 2a TODO: Complete the below code to recreate self.genes from serialization,
        #          which is a string generated by your serialize method.
        #          We have provided logic for tree traversal to help you get started,
        #          but you need to flesh out this function and make the genes yourself.

        def to_float_to_string(primitive):
            try:
                return float(primitive)
            except ValueError:
                return primitive

        lines = serialization.split('\n')

        # We pop the last element as each serialization has an unneccessary new line character at the end
        lines.pop()

        # TODO: Create the root node yourself here based on lines[0]
        root = Node(to_float_to_string(lines[0]), None)

        parent_stack = [(root, 0)]
        for line in lines[1:]:
            my_depth = line.count('|')
            my_primitive = line.strip('|')
            parent, parent_depth = parent_stack.pop()
            right_child = False
            while parent_stack and parent_depth >= my_depth:
                parent, parent_depth = parent_stack.pop()
                right_child = True

            # TODO: Create a node using the above variables as appropriate.
            node = Node(to_float_to_string(my_primitive), None)

            if not right_child:
                parent.left = node
            else:
                parent.right = node
            
            parent_stack.extend([(parent, parent_depth), \
                                 (node, my_depth)])

        # TODO: Use the data structure you've created to assign self.genes.
        self.genes = root

    def recombine(self, mate, depth_limit, **kwargs):
        child = self.__class__()

        # 2b TODO: Recombine genes of mate and genes of self to
        #          populate child's genes member variable.
        #          We recommend using deepcopy, but also recommend
        #          that you deepcopy the minimal amount possible.

        parent_1_genes_clone = deepcopy(self.genes)
        parent_2_genes_clone = deepcopy(mate.genes)

        # Dictionary of mapping, integer_of_when_node_encountered -> (node, depth)
        parent_1_dict = bfs(parent_1_genes_clone)
        parent_2_dict = bfs(parent_2_genes_clone)

        num_nodes_parent_1 = parent_1_genes_clone.size
        num_nodes_parent_2 = parent_2_genes_clone.size

        while True:

            # Uniform Randomly choose a subtree to remove from parent 1's genes
            root_subtree_p1, root_subtree_p1_depth = parent_1_dict[random.randint(1, num_nodes_parent_1)]

            # Uniform Randomly choose a subtree from parent 2's genes to recombine with parent 1's genes
            root_subtree_p2 = parent_2_dict[random.randint(1, num_nodes_parent_2)][0]

            # Check to see if the depth of the root of the subtree chosen from parent 1
            # plus the height from the root of the subtree chosen from parent 2 is less than
            # or equal to depth_limit.
            if root_subtree_p1_depth + root_subtree_p2.height <= depth_limit:

                # If the subtree chosen from parent 1 is the whole tree then simply assign
                # the genes of the child to the subtree chosen from parent 2.
                if root_subtree_p1_depth == 0:
                    child.genes = root_subtree_p2
                    child.genes.parent = None
                elif root_subtree_p1 is root_subtree_p1.parent.left:
                    # Update Parent and Child Relationships
                    root_subtree_p1.parent.left = root_subtree_p2
                    root_subtree_p2.parent = root_subtree_p1.parent
                    
                    update_node_fields(root_subtree_p2.parent)
                    child.genes = parent_1_genes_clone
                else:
                    # Update Parent and Child Relationships
                    root_subtree_p1.parent.right = root_subtree_p2
                    root_subtree_p2.parent = root_subtree_p1.parent
                    
                    update_node_fields(root_subtree_p2.parent)
                    child.genes = parent_1_genes_clone
                break

        return child


    def mutate(self, depth_limit, **kwargs):
        mutant = self.__class__()
        mutant.genes = deepcopy(self.genes)

        # 2b TODO: Mutate mutant.genes to produce a modified tree.
        mutant_dict = bfs(mutant.genes)
        num_nodes_mutant = mutant.genes.size

        # If there is only one node in the TreeGenotype then return, as you do not want to change the whole true
        if num_nodes_mutant == 1:
            return mutant

        while True:
            # Uniform Randomly choose a subtree to remove from the mutant's genes
            # Check to see if the chosen subtree is not also the whole tree
            while True:
                root_subtree_mutant, root_subtree_mutant_depth = mutant_dict[random.randint(1, num_nodes_mutant)]
                if root_subtree_mutant_depth != 0:
                    break
                    
            # Grow a new tree using the Grow Method
            new_subtree = grow_method(0, None, depth_limit=depth_limit, **kwargs)
    
            # Check to see if the depth of the root of the subtree chosen from the mutant
            # plus the height from the root of the new subtree chosen is less than
            # or equal to depth_limit.
            if root_subtree_mutant_depth + new_subtree.height <= depth_limit:
                if root_subtree_mutant is root_subtree_mutant.parent.left:
                    # Update Parent and Child Relationships
                    root_subtree_mutant.parent.left = new_subtree
                    new_subtree.parent = root_subtree_mutant.parent
                    
                    update_node_fields(new_subtree.parent)
                else:
                    # Update Parent and Child Relationships
                    root_subtree_mutant.parent.right = new_subtree
                    new_subtree.parent = root_subtree_mutant.parent
                    
                    update_node_fields(new_subtree.parent)
                break

        return mutant
