
# fitness.py

import gpac
import random
from functools import cache
from math import inf


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def nearest_distance_to_pills(set_of_pill_locations, current_location):
    nearest_distance_to_pill = inf
    for pill_location in set_of_pill_locations:
        nearest_distance_to_pill = min(nearest_distance_to_pill, manhattan(pill_location, current_location))
    return nearest_distance_to_pill

def nearest_distance_to_ghosts(player_location_dict, my_player, current_location):
    nearest_distance_to_ghost = inf
    for player in player_location_dict:
        # Makes sure to not calculate the distance with my_player to itself
        # Without this the function will always return 0
        if player != my_player:
            nearest_distance_to_ghost = min(nearest_distance_to_ghost, manhattan(player_location_dict[player], current_location))
    return nearest_distance_to_ghost

def find_state_score(terminal_dict, node):
    if not isinstance(node.primitive, str):
        return node.primitive
    elif node.primitive == "G":
        return terminal_dict["G"]
    elif node.primitive == "P":
        return terminal_dict["P"]
    elif node.primitive == "F":
        return terminal_dict["F"]
    elif node.primitive == "W":
        return terminal_dict["W"]
    elif node.primitive == "+":
        return find_state_score(terminal_dict, node.left) + find_state_score(terminal_dict, node.right)
    elif node.primitive == "-":
        return find_state_score(terminal_dict, node.left) - find_state_score(terminal_dict, node.right)
    elif node.primitive == "*":
        return find_state_score(terminal_dict, node.left) * find_state_score(terminal_dict, node.right)
    elif node.primitive == "/":
        a = find_state_score(terminal_dict, node.left)
        b = find_state_score(terminal_dict, node.right)
        # If the denominator is 0, it will just return 0
        if b == 0:
            return 0
        else:
            return a / b
    elif node.primitive == "RAND":
        a = find_state_score(terminal_dict, node.left)
        b = find_state_score(terminal_dict, node.right)
        return random.uniform(min(a, b), max(a, b))
    
# Fitness function that plays a game using the provided pac_controller
# with optional ghost controller and game map specifications.
# Returns Pac-Man score from a full game as well as the game log.
def play_GPac(pac_controller, ghost_controller=None, game_map=None, **kwargs):
    game_map = parse_map(game_map)
    game = gpac.GPacGame(game_map, **kwargs)

    # Game loop, representing one turn.
    while not game.gameover:
        # Evaluate moves for each player.
        for player in game.players:
            actions = game.get_actions(player)
            s_primes = game.get_observations(actions, player)
            selected_action_idx = None

            # Select Pac-Man action(s) using provided strategy.
            if 'm' in player:
                if pac_controller is None:
                    # Random Pac-Man controller.
                    selected_action_idx = random.randrange(len(actions))

                else:
                    '''
                    ####################################
                    ###   YOUR 2a CODE STARTS HERE   ###
                    ####################################
                    '''
                    # 2a TODO: Score all of the states stored in s_primes by evaluating your tree.

                    # Variables used to keep track of the index of the best state and corresponding score of that state
                    best_action_idx = 0
                    best_score = -inf

                    # Directions that signify the different ways we can move
                    # Will be used to add to our current location to determine how many walls are around us
                    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                    
                    for i in range(len(s_primes)):
                        curr_state = s_primes[i]

                        # Dimensions of the board
                        ROWS, COLS = len(curr_state["walls"]), len(curr_state["walls"][0])

                        # Dictionary that we will use to cache our G, P, F, and W values
                        terminal_dict = {}
                        terminal_dict["G"] = nearest_distance_to_ghosts(curr_state["players"], player, curr_state["players"][player])
                        terminal_dict["P"] = nearest_distance_to_pills(curr_state["pills"], curr_state["players"][player])
                        terminal_dict["F"] = 0

                        # If the fruit is not on the board, it will just set F to 0
                        if curr_state["fruit"] is not None:
                            terminal_dict["F"] = manhattan(curr_state["fruit"], curr_state["players"][player])

                        terminal_dict["W"] = 0
                        for d1, d2 in directions:
                            new_r, new_c = curr_state["players"][player][0] + d1, curr_state["players"][player][1] + d2

                            # Checks to see if new_r and new_c represents the location of a wall or simply out of bounds
                            if new_r < 0 or new_r == ROWS or new_c < 0 or new_c == COLS or curr_state["walls"][new_r][new_c]:
                                terminal_dict["W"] += 1

                        # Finds the score of the state and checks to see if it is the best state seen so far
                        state_score = find_state_score(terminal_dict, pac_controller.genes)
                        if state_score > best_score:
                            best_action_idx = i
                            best_score = state_score
                    
                    # 2a TODO: Assign index of state with the best score to selected_action_idx.
                    selected_action_idx = best_action_idx

                    # You may want to uncomment these print statements for debugging.
                    # print(selected_action_idx)
                    # print(actions)
                    '''
                    ####################################
                    ###    YOUR 2a CODE ENDS HERE    ###
                    ####################################
                    '''

            # Select Ghost action(s) using provided strategy.
            else:
                if ghost_controller is None:
                    # Random Ghost controller.
                    selected_action_idx = random.randrange(len(actions))

                else:
                    '''
                    ####################################
                    ###   YOUR 2c CODE STARTS HERE   ###
                    ####################################
                    '''
                    # 2c TODO: Score all of the states stored in s_primes by evaluating your tree

                    # 2c TODO: Assign index of state with the best score to selected_action_idx.
                    selected_action_idx = None

                    # You may want to uncomment these print statements for debugging.
                    # print(selected_action_idx)
                    # print(actions)
                    '''
                    ####################################
                    ###    YOUR 2c CODE ENDS HERE    ###
                    ####################################
                    '''

            game.register_action(actions[selected_action_idx], player)
        game.step()
    return game.score, game.log


# Function for parsing map contents.
# Note it is cached, so modifying a file requires a kernel restart.
@cache
def parse_map(path_or_contents):
    if not path_or_contents:
        # Default generic game map, with a cross-shaped path.
        size = 21
        game_map = [[True for __ in range(size)] for _ in range(size)]
        for i in range(size):
            game_map[0][i] = False
            game_map[i][0] = False
            game_map[size//2][i] = False
            game_map[i][size//2] = False
            game_map[-1][i] = False
            game_map[i][-1] = False
        return tuple(tuple(y for y in x) for x in game_map)

    if isinstance(path_or_contents, str):
        if '\n' not in path_or_contents:
            # Parse game map from file path.
            with open(path_or_contents, 'r') as f:
                lines = f.readlines()
        else:
            # Parse game map from a single string.
            lines = path_or_contents.split('\n')
    elif isinstance(path_or_contents, list) and isinstance(path_or_contents[0], str):
        # Parse game map from a list of strings.
        lines = path_or_contents[:]
    else:
        # Assume the game map has already been parsed.
        return path_or_contents

    for line in lines:
        line.strip('\n')
    firstline = lines[0].split(' ')
    width, height = int(firstline[0]), int(firstline[1])
    game_map = [[False for y in range(height)] for x in range(width)]
    y = -1
    for line in lines[1:]:
        for x, char in enumerate(line):
            if char == '#':
                game_map[x][y] = True
        y -= 1
    return tuple(tuple(y for y in x) for x in game_map)
