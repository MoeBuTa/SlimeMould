from collections import deque
from slime.cell import Cell
import networkx as nx
import math

DIFFUSION_THRESHOLD = 3.5
DIFFUSION_DECAY_RATE = 1.26
MOVING_THRESHOLD = 1
MAX_PH = 5.5
MAX_PH_INCREASE_STEP = 0.2


def get_neighbours(idx):
    return [
        (idx[0] - 1, idx[1] - 1),  # up   1, left  1
        (idx[0] - 1, idx[1]),  # up   1,
        (idx[0] - 1, idx[1] + 1),  # up   1, right 1
        (idx[0], idx[1] - 1),  # , left  1
        (idx[0], idx[1] + 1),  # , right 1
        (idx[0] + 1, idx[1] - 1),  # down 1, left  1
        (idx[0] + 1, idx[1]),  # down 1,
        (idx[0] + 1, idx[1] + 1),  # down 1, right 1
    ]


def step_direction(index: int, idx: tuple):
    next_step = {
        0: (0, 0),
        1: (-1, -1),
        2: (1, -1),
        3: (-1, 1),
        4: (1, 1),
        5: (-1, 0),
        6: (1, 0),
        7: (0, -1),
        8: (0, 1)
    }
    return next_step[index][0] + idx[0], next_step[index][1] + idx[1]


class SlimeCell(Cell):

    def __init__(self, idx: tuple, pheromone: float, mould, dish, is_capital):
        super().__init__(pheromone=pheromone, cell_type=1)

        self.idx = idx
        self.pheromone = pheromone
        self.max_ph = 4
        self.direction = None
        self.is_capital = is_capital
        self.reached_food_id = None
        self.mould = mould
        self.dish = dish
        self.food_path = []

        # (food_id, food_idx)
        self.step_food = None
        self.curr_target = None

    def find_nearest_food(self, food_ids):
        min_dist = -1
        min_i = 0
        # find the nearest food
        for i in food_ids:
            food_idx = self.dish.get_food_position(i)
            dist = math.dist(self.idx, food_idx)
            if min_dist > dist or min_dist < 0:
                min_dist = dist
                min_i = i
        return min_i, min_dist

    def set_reached_food_path(self):
        # target food (food_id, food_idx)
        target_food_id = self.mould.get_current_target()[0]
        self.curr_target = target_food_id

        mould_reached_food_ids = self.mould.get_reached_food_ids()

        if len(mould_reached_food_ids) == 0:
            self.food_path.append(self.mould.get_current_target()[0])

        else:
            # find the nearest food
            min_i = self.find_nearest_food(food_ids=self.mould.get_reached_food_ids())[0]

            # find the shortest path from the nearest food to the target food
            self.food_path = nx.shortest_path(G=self.dish.get_food_graph(), source=min_i, target=target_food_id)
        step_food_id = self.food_path.pop(0)
        self.step_food = (step_food_id, self.dish.get_food_position(step_food_id))

    def reset_step_food(self):
        # reached target
        if self.reached_food_id == self.curr_target and self.curr_target == self.mould.get_current_target()[0]:
            return

        if self.step_food is None or len(self.food_path) == 0:
            self.set_reached_food_path()
        else:
            # reached step food
            step_food_idx = self.dish.get_food_position(self.step_food[0])
            if math.dist(step_food_idx, self.idx) < 3:
                step_food_id = self.food_path.pop(0)
                self.step_food = (step_food_id, self.dish.get_food_position(step_food_id))

    def sensory(self):

        # target_food = self.mould.get_current_target()
        # food_idx = target_food[1]
        if self.reached_food_id == self.step_food:
            self.reset_step_food()
        food_idx = self.step_food[1]

        # (-1, -1)
        if food_idx[0] < self.idx[0] and food_idx[1] < self.idx[1]:
            self.direction = 1
        # (1, -1)
        elif food_idx[0] > self.idx[0] and food_idx[1] < self.idx[1]:
            self.direction = 2
        # (-1, 1)
        elif food_idx[0] < self.idx[0] and food_idx[1] > self.idx[1]:
            self.direction = 3
        # (1, 1)
        elif food_idx[0] > self.idx[0] and food_idx[1] > self.idx[1]:
            self.direction = 4
        # (-1, 0)
        elif food_idx[0] < self.idx[0]:
            self.direction = 5
        # (1, 0)
        elif food_idx[0] > self.idx[0]:
            self.direction = 6
        # (0, -1)
        elif food_idx[1] < self.idx[1]:
            self.direction = 7
        # (0, 1)
        elif food_idx[1] > self.idx[1]:
            self.direction = 8

    @staticmethod
    def check_boundary(idx, lattice_shape):
        if idx[0] >= lattice_shape[0] or idx[0] <= 0 or idx[1] >= lattice_shape[1] or idx[1] <= 0:
            return False
        return True

    # diffusion
    def diffusion(self, lattice, decay):

        new_idx = step_direction(self.direction, self.idx)
        neighbours = get_neighbours(self.idx)

        # make sure the first neighbour is the next step
        neighbours.remove(new_idx)
        neighbours = deque(neighbours)
        neighbours.appendleft(new_idx)

        while neighbours:
            neigh = neighbours.popleft()
            # continue if the neighbor is out of boundary
            if not self.check_boundary(neigh, lattice.shape):
                continue
            neigh_cell = lattice[neigh]
            # neighbour cell is an empty cell
            if neigh_cell.get_cell_type() == 0:

                # todo: next main diffusion place is an empty cell
                if neigh == new_idx and self.pheromone > MOVING_THRESHOLD:
                    # self.mould.update_slime_cell(new_idx, self)
                    self.mould.slime_cell_generator(idx=neigh, pheromone=self.pheromone, decay=decay,
                                                    is_capital=self.is_capital)
                    self.pheromone *= (1 - DIFFUSION_DECAY_RATE * decay)

                    self.is_capital = False
                    continue

                # neighbour cell is a random diffusion cell
                if self.pheromone > DIFFUSION_THRESHOLD and \
                        self.find_nearest_food(self.mould.get_reached_food_ids())[1] < self.mould.distance_for_diffusion_threshold:
                    self.mould.slime_cell_generator(idx=neigh, pheromone=self.pheromone/DIFFUSION_DECAY_RATE, decay=decay)
                    self.pheromone *= (1 - (2 * DIFFUSION_DECAY_RATE * decay))

            # neighbor is a slime
            elif neigh_cell.get_cell_type() == 1:

                # todo: next main diffusion place is a slime cell
                if neigh == new_idx and self.pheromone > MOVING_THRESHOLD:
                    neigh_increase_ph = neigh_cell.pheromone + self.pheromone / DIFFUSION_DECAY_RATE
                    if neigh_increase_ph > neigh_cell.max_ph:

                        neigh_cell.pheromone = neigh_cell.max_ph

                    else:
                        neigh_cell.pheromone = neigh_increase_ph
                    self.pheromone /= DIFFUSION_DECAY_RATE

                    self.mould.update_slime_cell(new_idx, neigh_cell)

                # neighbor bigger than self
                # increase self-pheromone when find neighbor nearby
                if neigh_cell.pheromone > self.pheromone and self.max_ph < MAX_PH:
                    self.max_ph += MAX_PH_INCREASE_STEP
                    self.pheromone += (neigh_cell.pheromone / 10)

            # add pheromone if current cell find food nearby
            elif neigh_cell.get_cell_type() == 2:

                # eat food
                self.pheromone = 7
                self.max_ph = 7
                self.reached_food_id = neigh_cell.get_food_id()
                new_food_id = neigh_cell.get_food_id()
                if new_food_id not in self.mould.get_reached_food_ids():
                    self.mould.update_food_connection(new_food_id)
                    self.mould.get_reached_food_ids().add(new_food_id)

        self.mould.update_slime_cell(self.idx, self)

    def step(self, lattice, decay):
        """
        * The sensory stage: all slime cells adjust their direction based on the pheromones
        * The diffusion stage: all pheromones undergo diffusion
        """
        # alive after diffusion
        self.sensory()
        self.diffusion(lattice, decay)

    def get_idx(self):
        return self.idx

    def get_pheromone(self):
        return self.pheromone

    def set_pheromone(self, ph):
        self.pheromone = ph

    def get_reached_food_id(self):
        return self.reached_food_id

    def remove_capital(self):
        self.is_capital = False
