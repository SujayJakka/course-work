
# gpac.py

import random
from copy import deepcopy
import matplotlib.pyplot as plt
import matplotlib.path as mpath
from functools import cache, partial
from matplotlib.animation import FuncAnimation


GHOST_ACTIONS = {'up':(0, 1), 'right':(1, 0), 'down':(0, -1), 'left':(-1, 0)}
PAC_ACTIONS = {'hold':(0, 0)}
PAC_ACTIONS.update(GHOST_ACTIONS)


class GPacGame():
    def __init__(self, game_map, pill_density=0.1,
                 fruit_prob=0.2, fruit_score=10,
                 time_multiplier=2, num_ghosts=3,
                 num_pacs=1, pill_spawn='stochastic',
                 fruit_spawn='stochastic', **kwargs):
        assert len(game_map) > 0 and len(game_map[0]) > 0,\
                    "ERROR: MAP MUST BE 2 DIMENSIONAL"
        self.walls = game_map
        self.num_pacs = num_pacs
        self.num_ghosts = num_ghosts
        self.pill_density = pill_density
        self.fruit_prob = fruit_prob
        self.fruit_score = fruit_score
        self.total_time = int(len(self.walls) * len(self.walls[0]) * time_multiplier)
        self.pill_spawn = pill_spawn.casefold()
        self.fruit_spawn = fruit_spawn.casefold()
        self.reset()


    def reset(self):
        # spawn players
        self.players = dict()
        if self.num_pacs == 1:
            self.players['m'] = (0, len(self.walls[0]) - 1)
        else:
            for pac in range(self.num_pacs):
                loc = (0, len(self.walls[0]) - 1)
                counter = 0
                while self.walls[loc[0]][loc[1]] or loc in self.players.values():
                    counter += 1
                    if counter % 2:
                        loc = ((counter + 1) // 2, len(self.walls[0]) - 1)
                    else:
                        loc = (0, len(self.walls[0]) - 1 - (counter // 2))
                self.players[f'm{pac}'] =  tuple(loc)
        for ghost in range(self.num_ghosts):
            if ghost % 3 == 0:
                self.players[f'{ghost}'] = (len(self.walls) - 1, 0)
            elif ghost % 3 == 1:
                self.players[f'{ghost}'] = (0, 0)
            elif ghost % 3 == 2:
                self.players[f'{ghost}'] = (len(self.walls) - 1, len(self.walls[0]) - 1)

        self.pills_consumed = 0
        pills = set()

        placement_strategies = {'stochastic', 'linear', 'manhattan', 'grid', 'waves'}
        assert self.pill_spawn in placement_strategies,\
                f"ERROR: UNRECOGNIZED PILL SPAWN STRATEGY {self.pill_spawn} "+\
                f"BUT EXPECTED ONE OF {placement_strategies}"

        # generate pill placement
        forbidden_locations = {self.players[p] for p in self.players if 'm' in p}
        available_locations = []
        # skip spawning location of pac-man
        for x in range(len(self.walls)):
            for y in range(len(self.walls[x])):
                if (x, y) not in forbidden_locations and not self.walls[x][y]:
                    available_locations.append((x, y))
        assert len(available_locations) > 0, "ERROR: NO VALID PILL LOCATIONS"

        if self.pill_spawn == 'stochastic':
            for location in available_locations:
                    if random.random() <= self.pill_density:
                        pills.add(location)
            if len(pills) == 0: # failsafe logic to guarantee a pill placement
                pills.add(random.choice(available_locations))

        elif self.pill_spawn == 'linear' or self.pill_spawn == 'manhattan':
            pill_freq = max(1, int(round(1/self.pill_density)))
            if self.pill_spawn == 'manhattan':
                available_locations = sorted(available_locations,\
                                             key=lambda location:location[0] + location[1])
            for i in range(0, len(available_locations), pill_freq):
                pills.add(available_locations[i])

        elif self.pill_spawn == 'grid':
            pill_freq = max(1, int(round(1/self.pill_density)))
            for location in available_locations:
                    if location[0] % pill_freq == 0 and\
                            location[1] % pill_freq == 0:
                        pills.add(location)
            assert len(pills) > 0, "ERROR: NO VALID PILL LOCATIONS"

        elif self.pill_spawn == 'waves':
            pill_freq = max(1, int(round(1/self.pill_density)))
            for location in available_locations:
                    if (location[0] + location[1]) % pill_freq == 0:
                        pills.add(location)
            assert len(pills) > 0, "ERROR: NO VALID PILL LOCATIONS"

        self.pills = frozenset(pills)
        self.fruit_consumed = 0
        self.fruit_location = None
        self.fruit_rotation = 0
        self.time = self.total_time
        self.last_fruit_eaten = self.time
        self.last_fruit_spawned = self.time
        self.score = 0
        self.bonus = 0
        self.gameover = False
        self.registered_pac_actions = dict()
        self.registered_ghost_actions = dict()

        # initialize new world file log
        self.log = [f'{len(self.walls)}', f'{len(self.walls[0])}']
        for player, location in self.players.items():
            self.log.append(f'{player} {location[0]} {location[1]}')
        for x in range(len(self.walls)):
            for y in range(len(self.walls[x])):
                if self.walls[x][y]:
                    self.log.append(f'w {x} {y}')
        for x, y in self.pills:
            self.log.append(f'p {x} {y}')
        self.log.append(f't {self.time} {self.score}')


    def update_score(self, time_bonus_or_penalty=None):
        total_pills = self.pills_consumed + len(self.pills)
        self.score = 100 * self.pills_consumed / total_pills
        self.score += self.fruit_consumed * self.fruit_score
        if time_bonus_or_penalty == 'bonus':
            self.score += 100 * self.time / self.total_time
        elif time_bonus_or_penalty == 'penalty':
            self.score -= 100 * self.time / self.total_time


    def manage_fruit(self):
        # check if fruit already exists and whether or not one should spawn this turn
        if self.fruit_location == None and self.last_fruit_eaten != self.time:
            assert self.fruit_spawn in {'stochastic', 'corners_eaten', 'corners_spawned'}
            if self.fruit_spawn == 'stochastic':
                if random.random() <= self.fruit_prob:
                    forbidden_locations = self.pills | {self.players[p] for p in self.players if 'm' in p}
                    available_locations = list()
                    for x in range(len(self.walls)):
                        for y in range(len(self.walls[x])):
                            if (x, y) not in forbidden_locations and not self.walls[x][y]:
                                available_locations.append((x, y))

                    if len(available_locations) == 0:
                        self.fruit_location = None
                    else:
                        self.fruit_location = random.choice(available_locations)
                        # log spawn of fruit
                        self.log.append(f'f {self.fruit_location[0]} {self.fruit_location[1]}')

            else:
                if self.fruit_spawn == 'corners_eaten':
                    elapsed_time = self.last_fruit_eaten - self.time
                else:
                    elapsed_time = self.last_fruit_spawned - self.time
                if (elapsed_time + 1) % max(1, int(round(1 / self.fruit_prob))) == 0:
                    corners = ((0, len(self.walls[0]) - 1),
                               (len(self.walls) - 1, len(self.walls[0]) - 1),
                               (len(self.walls) - 1, 0),
                               (0, 0))
                    spawns = [corner for corner in corners if not self.walls[corner[0]][corner[1]]]
                    pac_locations = {self.players[p] for p in self.players if 'm' in p}
                    if all(s in pac_locations for s in spawns):
                        return # no available place to spawn
                    while True:
                        self.fruit_rotation = (self.fruit_rotation + 1) % len(spawns)
                        if spawns[self.fruit_rotation] not in pac_locations:
                            self.last_fruit_spawned = self.time
                            self.fruit_location = spawns[self.fruit_rotation]
                            # log spawn of fruit
                            self.log.append(f'f {self.fruit_location[0]} {self.fruit_location[1]}')
                            return


    def get_actions(self, player='m'):
        current_location = self.players[player]
        ghost = 'm' not in player
        return get_player_actions(current_location, self.walls, ghost)


    def get_observations(self, actions, player='m'):
        observations = [{'walls':self.walls, 'pills':self.pills, 'fruit':self.fruit_location} \
                            for _ in range(len(actions))]
        current_location = self.players[player]
        for index in range(len(actions)):
            observations[index]['players'] = self.players.copy()
            observations[index]['players'][player] = apply_action(current_location,\
                                                                  actions[index])
        return observations


    def register_action(self, action, player='m'):
        if 'm' in player:
            self.registered_pac_actions[player] = action
        else:
            self.registered_ghost_actions[player] = action


    def step(self):
        self.time -= 1

        # update ghost locations from registered actions
        ghost_moves = dict()
        ghost_destinations = set()
        for player, action in self.registered_ghost_actions.items():
            assert action in self.get_actions(player=player),\
                        f'ERROR: INVALID ACTION ({action}) FOR PLAYER {player}'

            current_location = self.players[player]
            destination = apply_action(current_location, action)
            ghost_destinations.add(destination)
            if current_location in ghost_moves:
                ghost_moves[current_location].add(destination)
            else:
                ghost_moves[current_location] = {destination}
            self.players[player] = destination
        self.registered_ghost_actions.clear()

        # update pac-man locations from registered actions
        late_deaths = set()
        touched_pills = set()
        touched_fruit = False
        for player, action in self.registered_pac_actions.items():
            assert action in self.get_actions(player=player),\
                        f'ERROR: INVALID ACTION ({action}) FOR PLAYER {player}'

            current_location = self.players[player]
            destination = apply_action(current_location, action)
            self.players[player] = destination

            # check if pac-man swapped positions with a ghost
            if destination in ghost_moves and current_location in ghost_moves[destination]:
                del self.players[player]
                continue

            # check if destination has a pill
            if destination in self.pills:
                touched_pills.add(destination)

            # check if destination has a fruit
            touched_fruit |= destination == self.fruit_location

            # check if pac-man ends in the same cell as a ghost
            # we will remove him from the game after he has a chance to eat
            if destination in ghost_destinations:
                late_deaths.add(player)
        self.registered_pac_actions.clear()

        # check for game over by exchanging cells
        if len(self.players) == self.num_ghosts:
            self.gameover = True
            self.update_score('penalty')

        else:
            # eat pills
            if touched_pills:
                self.pills_consumed += len(touched_pills)
                self.pills = self.pills - touched_pills

            # eat fruit
            if touched_fruit:
                self.fruit_consumed += 1
                self.fruit_location = None
                self.last_fruit_eaten = self.time
            # check if all pills are eaten
            if len(self.pills) == 0:
                self.gameover = True
                self.update_score('bonus')

        # apply late deaths
        for death in late_deaths:
            del self.players[death]

        # check for game over by ending in the same cell as a ghost
        if len(self.players) == self.num_ghosts and not self.gameover:
            self.gameover = True
            self.update_score('penalty')

        if not self.gameover:
            self.update_score(None)
            # check for game over by running out of time
            if self.time <= 0:
                self.gameover = True

        # update log
        for player, location in self.players.items():
            self.log.append(f'{player} {location[0]} {location[1]}')
        if not self.gameover:
            self.manage_fruit() # do things with fruit
        self.log.append(f't {self.time} {self.score}')


@cache
def apply_action(current_location, action):
    # PAC_ACTIONS is a superset of GHOST_ACTIONS, so this works for either one
    return tuple(sum(val) for val in zip(current_location, PAC_ACTIONS[action]))


@cache
def get_player_actions(current_location, walls, ghost=False):
    available_actions = list()
    if ghost:
        candidate_actions = GHOST_ACTIONS
    else:
        candidate_actions = PAC_ACTIONS
    for action in candidate_actions:
        x, y = apply_action(current_location, action)
        if 0 <= x < len(walls) \
                and 0 <= y < len(walls[0]) \
                and not walls[x][y]:
            available_actions.append(action)
    return available_actions


# pac-man icon creation
pac_vertices = deepcopy(mpath.Path.unit_circle().vertices)
pac_codes = deepcopy(mpath.Path.unit_circle().codes)
pac_vertices[5] = [0,0]
pac_vertices[6] = [0,0]
pac_vertices[7] = [0,0]
PAC_ICON = mpath.Path(vertices=pac_vertices,codes=pac_codes)


# ghost icon creation
fin_depth = 0.5
ghost_vertices = deepcopy(mpath.Path.unit_circle().vertices)
ghost_codes = deepcopy(mpath.Path.unit_circle().codes)
ghost_vertices[1] = [0.25,-fin_depth]
ghost_vertices[2] = [0.5, -1]
ghost_vertices[3] = [0.75, -fin_depth]
ghost_vertices[4] = [1, -1]
ghost_vertices[5] = [1, 0]
ghost_vertices[19] = [-1, -1]
ghost_vertices[20] = [-0.75, -fin_depth]
ghost_vertices[21] = [-0.5, -1]
ghost_vertices[22] = [-0.25, -fin_depth]
ghost_vertices[23] = [0, -1]
ghost_codes[1] = 2
ghost_codes[2] = 2
ghost_codes[3] = 2
ghost_codes[4] = 2
ghost_codes[5] = 2
ghost_codes[6] = 2
ghost_codes[19] = 2
ghost_codes[20] = 2
ghost_codes[21] = 2
ghost_codes[22] = 2
ghost_codes[23] = 2
GHOST_ICON = mpath.Path(vertices=ghost_vertices,codes=ghost_codes)

SCOREBOARD_SIZE = 4


def render_game(log):
    fig, ax = plt.subplots(layout='none', figsize=(4.0, 3.0))
    fig.canvas.header_visible = False
    fig.canvas.footer_visible = False
    ax.axis('off')

    frames = get_frames(log)
    artists = init_artists(ax, frames[0])
    animation = FuncAnimation(fig, partial(render_frame, artists=artists), frames, partial(draw_walls, log, ax), blit=True)
    jshtml = animation.to_jshtml()
    plt.close(fig)
    return jshtml


def draw_walls(log, ax):
    width = int(log[0])
    height = int(log[1]) + SCOREBOARD_SIZE
    walls = [[(0, 0, 0) for x in range(width)] for y in range(height)]
    log_idx = 2
    while log[log_idx][0] != 'w':
        log_idx += 1
    while log[log_idx][0] == 'w':
        elements = log[log_idx].split(' ')
        x = int(elements[1])
        y = int(elements[2])
        walls[y][x] = (0.2, 0.2, 1)
        log_idx += 1
    with plt.ioff():
        return [ax.imshow(walls, origin='lower')]


def get_frames(log):
    players = dict()
    pills = set()
    log_idx = 2
    while log[log_idx][0] != 'w':
        elements = log[log_idx].split(' ')
        coords = (int(elements[1]), int(elements[2]))
        players[elements[0]] = coords
        log_idx += 1
    while log[log_idx][0] != 'p':
        log_idx += 1
    while log[log_idx][0] == 'p':
        elements = log[log_idx].split(' ')
        coords = (int(elements[1]), int(elements[2]))
        pills.add(coords)
        log_idx += 1
    while log[log_idx][0] != 't':
        log_idx += 1
    elements = log[log_idx].split(' ')
    time = int(elements[1])
    score = round(float(elements[2]), 2)
    fruit = None
    frame = (
                players,
                pills.copy(),
                fruit,
                time,
                score,
                True,
                True
            )
    frames = [frame]
    log_idx += 1
    while log_idx < len(log):
        pills_changed = False
        fruit_changed = False
        players = dict()
        while log[log_idx][0] not in {'t', 'f'}:
            elements = log[log_idx].split(' ')
            coords = (int(elements[1]), int(elements[2]))
            players[elements[0]] = coords
            if elements[0][0] == 'm':
                if coords in pills:
                    pills.remove(coords)
                    pills_changed = True
                if fruit == coords:
                    fruit = None
                    fruit_changed = True
            log_idx += 1
        if log[log_idx][0] == 'f':
            elements = log[log_idx].split(' ')
            fruit = (int(elements[1]), int(elements[2]))
            fruit_changed = True
            log_idx += 1
        elements = log[log_idx].split(' ')
        time = int(elements[1])
        score = round(float(elements[2]), 2)
        frame = (
                    players,
                    pills.copy(),
                    fruit,
                    time,
                    score,
                    pills_changed,
                    fruit_changed
                )
        frames.append(frame)
        log_idx += 1
    return frames


def init_artists(ax, frame):
    (
        players,
        pills,
        fruit,
        time,
        score,
        pills_changed,
        fruit_changed
    ) = frame

    with plt.ioff():
        pill_art = ax.plot(*zip(*pills), '.w')[0]
        pacs = []
        ghosts = []
        for k, v in players.items():
            if 'm' in k:
                pacs.append(v)
            else:
                ghosts.append(v)
        pac_art = ax.plot(*zip(*pacs), ',', marker=PAC_ICON, color='yellow')[0]
        ghost_art = ax.plot(*zip(*ghosts), ',', marker=GHOST_ICON, color='cyan')[0]
        fruit_art = ax.plot([], [], 'Pr')[0]
        xmin, xmax, ymin, ymax = ax.axis()
        time_art = ax.text((xmax // 4), ymax + (SCOREBOARD_SIZE // 3), '',
                            color='white', size='xx-large', horizontalalignment='center')
        score_art = ax.text(((xmax * 3) // 4), ymax + (SCOREBOARD_SIZE // 3), '',
                            color='white', size='xx-large', horizontalalignment='center')
        return pill_art, pac_art, ghost_art, fruit_art, time_art, score_art


def render_frame(frame, artists):
    (
        players,
        pills,
        fruit,
        time,
        score,
        pills_changed,
        fruit_changed
    ) = frame

    (
        pill_art,
        pac_art,
        ghost_art,
        fruit_art,
        time_art,
        score_art
    ) = artists

    with plt.ioff():
        returned_artists = [pac_art, ghost_art, time_art, score_art]

        if pills_changed:
            pill_art.set_data(*zip(*pills))
            returned_artists.append(pill_art)

        pac_xs = []
        pac_ys = []
        ghost_xs = []
        ghost_ys = []
        for k, v in players.items():
            if 'm' in k:
                pac_xs.append(v[0])
                pac_ys.append(v[1])
            else:
                ghost_xs.append(v[0])
                ghost_ys.append(v[1])
        pac_art.set_data(pac_xs, pac_ys)
        ghost_art.set_data(ghost_xs, ghost_ys)

        if fruit_changed:
            if fruit:
                fruit_art.set_visible(True)
                fruit_art.set_data([fruit[0]], [fruit[1]])
            else:
                fruit_art.set_visible(False)
            returned_artists.append(fruit_art)

        time_art.set_text(str(time))
        score_art.set_text(str(score))
        return returned_artists


# test game with random agents if you run this file
if __name__ == "__main__":
    size = 21
    game_map = [[1 for __ in range(size)] for _ in range(size)]
    for i in range(size):
        game_map[0][i] = game_map[i][0] = game_map[size//2][i] = game_map[i][size//2] = game_map[size-1][i] = game_map[i][size-1] = 0
    game = GPacGame(game_map)
    while not game.gameover:
        [game.register_action(random.choice(game.get_actions(player = player)), player = player) for player in game.players]
        game.step()
    [print(line) for line in game.log]
